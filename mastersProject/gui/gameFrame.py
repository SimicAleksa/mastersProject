import tkinter as tk
from tkinter import ttk, messagebox
import requests

from mastersProject.dsl_classes.game_world import GameWorld
from mastersProject.enums_consts import POSSIBLE_COMMANDS
from mastersProject.interpreter import parse_dsl
from PIL import ImageTk
from PIL import Image
from io import BytesIO
from os.path import join, dirname
from openai import OpenAI
from functools import partial
import dill as pickle
import os

client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))

# Help command message
help_message = "Possible commands:\n" + "\n".join(POSSIBLE_COMMANDS)


class GamePlayFrame(ttk.Frame):
    def __init__(self, parent, game_title, with_images, generate_infinitely, reload_saved_file):
        super().__init__(parent)
        self.this_folder = dirname(__file__)
        if reload_saved_file:
            try:
                with open(game_title + ".pickle", 'rb') as file:
                    game_state = pickle.load(file)

                game_world = GameWorld()
                game_world.regions = game_state['regions']
                game_world.items = game_state['items']
                game_world.enemies = game_state['enemies']
                game_world.weapons = game_state['weapons']
                game_world.armors = game_state['armors']
                game_world.player = game_state['player']
                game_world.start_position = game_state['start_position']
                game_world.final_position = game_state['final_position']
                game_world.settings = game_state['settings']
                game_world.current_enemy = game_state['current_enemy']
                game_world.prev_direction = game_state['prev_direction']
                game_world.opposite_dirs = game_state['opposite_dirs']

                self.gameWorld = game_world
            except:
                messagebox.showinfo("Information", "Selected game does not have a saved file. You can not select to "
                                                   "reload it.")
                return
        else:
            try:
                self.gameWorld = parse_dsl("gameDSL.tx", game_title)
            except Exception as e:
                messagebox.showinfo("Error", e.message + f", on line {e.col}")
                return

        frame_title_label = ttk.Label(self, text=game_title[:-5], font=("Arial", 14, "bold"))
        frame_title_label.pack(pady=10)

        self.text_area = tk.Text(self, wrap=tk.WORD, width=80, height=20)
        self.text_area.pack(pady=10)
        self.text_area.insert("1.0", self.gameWorld.regions[0].print_self())  # Replace with parsed text

        self.input_label = ttk.Label(self, text="Type your commands:")
        self.input_label.pack(pady=5)
        self.input_entry = ttk.Entry(self, width=50)
        self.input_entry.pack(pady=5)
        self.input_entry.bind("<Return>", lambda event: self.process_user_input(event, with_images, game_title,
                                                                                generate_infinitely))

        if with_images:
            self.image_label = tk.Label(self, width=256, height=256)
            self.image_label.pack()
            self.generate_image(self.gameWorld.regions[0], game_title, generate_infinitely)

        self.save_button = tk.Button(self, text="Save",
                                     command=partial(self.save_game_state, game_title, self.gameWorld))
        self.save_button.pack(padx=5, pady=5)

    def save_game_state(self, game_title, game_world):
        game_state = {
            'regions': game_world.regions,
            'items': game_world.items,
            'enemies': game_world.enemies,
            'weapons': game_world.weapons,
            'armors': game_world.armors,
            'player': game_world.player,
            'start_position': game_world.start_position,
            'final_position': game_world.final_position,
            'current_enemy': game_world.current_enemy,
            'prev_direction': game_world.prev_direction,
            'opposite_dirs': game_world.opposite_dirs,
            'settings': game_world.settings,
        }
        with open(game_title + ".pickle", 'wb') as file:
            pickle.dump(game_state, file)

        messagebox.showinfo("Information", "Game state saved!!")

    def generate_image(self, region, game_title, generate_infinitely):
        region_name = region.name
        image_path = os.path.join(os.getcwd(), "games", game_title, region_name + ".png")
        if os.path.exists(image_path):
            self.img_fromPipe = Image.open(image_path)
        else:
            if generate_infinitely:
                self.img_fromPipe = self.infinitely_generate_pictures(region, game_title)
            else:
                self.img_fromPipe = Image.open(join(self.this_folder, "resources\\noImage.png"))

        self.img = self.img_fromPipe.resize((256, 256))
        self.img = ImageTk.PhotoImage(self.img)
        self.image_label.config(image=self.img)

    def infinitely_generate_pictures(self, region, game_title):
        prompt = self.gameWorld.region_string_for_image_creation(region)

        response = client.images.generate(
            model="dall-e-2",
            prompt=prompt,
            size="256x256",
            n=1,
        )
        games_directory = "games/" + game_title
        generated_image = Image.open(BytesIO(requests.get(response.data[0].url).content))
        generated_image.save(games_directory + '/' + region.name + '.png')

        return generated_image

    def display_help(self):
        self.text_area.insert("end", "\n\n" + help_message + "\n\n")

    def process_user_input(self, event, with_images, game_title, generate_infinitely):
        user_input = self.input_entry.get().strip()
        self.text_area.insert("end", '\n' + '---------------------------------' + '\n')
        self.text_area.insert("end", '\n' + user_input)
        self.input_entry.delete(0, tk.END)
        the_end = False

        if self.gameWorld.player.position == self.gameWorld.final_position:
            possible_moves = ["move N", "move E", "move S", "move W"]
            for door in self.gameWorld.final_position.connections:
                possible_move = "move " + door
                possible_moves.remove(possible_move)
            if user_input in possible_moves:
                if generate_infinitely:
                    new_discovered_areas = self.gameWorld.explore_new_area()
                    self.text_area.insert("end", '\n' + new_discovered_areas)
                else:
                    self.text_area.delete("1.0", tk.END)
                    self.text_area.insert("1.0", "THE END")
                    the_end = True
                    if with_images:
                        self.img = ImageTk.PhotoImage(file=join(self.this_folder, "resources\\theEnd.png"))
                        self.image_label.config(image=self.img)

        if not the_end:
            if user_input.startswith("move"):
                direction = user_input.split()[1]
                if self.gameWorld.current_enemy is not None:
                    self.text_area.insert("end", '\n' + "You shall not pass \n")
                else:
                    text, moved = self.gameWorld.player.move(direction, self.gameWorld)
                    self.gameWorld.prev_direction = direction
                    self.text_area.insert("end", '\n' + text)
                    self.text_area.insert("end", '\n' + self.gameWorld.player.print_self())
                    if with_images and moved:
                        self.generate_image(self.gameWorld.player.position, game_title, generate_infinitely)

            elif user_input.startswith("take"):
                item = user_input[5:]
                text = self.gameWorld.player.take(item, self.gameWorld)
                self.text_area.insert("end", '\n' + text)
                self.text_area.insert("end", '\n' + self.gameWorld.player.print_self())

            elif user_input.startswith("drop"):
                item = user_input[5:]
                text = self.gameWorld.player.drop(item, self.gameWorld)
                self.text_area.insert("end", '\n' + text)
                self.text_area.insert("end", '\n' + self.gameWorld.player.print_self())

            elif user_input.startswith("use"):
                item = user_input[4:]
                text = self.gameWorld.player.use(item, self.gameWorld)
                self.text_area.insert("end", '\n' + text)
                self.text_area.insert("end", '\n' + self.gameWorld.player.print_self())

            elif user_input.startswith("open"):
                item = user_input[5:]
                text = self.gameWorld.player.open(item, self.gameWorld)
                self.text_area.insert("end", '\n' + text)
                self.text_area.insert("end", '\n' + self.gameWorld.player.print_self())

            elif user_input.startswith("equip"):
                item = user_input[6:]
                text = self.gameWorld.player.equip(item, self.gameWorld)
                self.text_area.insert("end", '\n' + text)
                self.text_area.insert("end", '\n' + self.gameWorld.player.print_self())

            elif user_input.startswith("unequip"):
                item = user_input[8:]
                text = self.gameWorld.player.unequip(item, self.gameWorld)
                self.text_area.insert("end", '\n' + text)
                self.text_area.insert("end", '\n' + self.gameWorld.player.print_self())

            elif user_input.startswith("info"):
                item = user_input[5:]
                text = self.gameWorld.player.print_item_info(item, self.gameWorld)
                self.text_area.insert("end", '\n' + text)

            elif user_input == "inventory":
                text = self.gameWorld.player.print_inventory()
                self.text_area.insert("end", '\n' + text)

            elif user_input == "health":
                health = self.gameWorld.player.get_health()
                self.text_area.insert("end", f'\nCurrent Health: {health}')

            elif user_input == "attack":
                text = self.gameWorld.attack_enemy()
                self.text_area.insert("end", '\n' + text)

            elif user_input == "flee":
                text = self.gameWorld.flee()
                self.text_area.insert("end", '\n' + text)

            elif user_input.startswith("inc "):
                stat = user_input[4:]
                text = self.gameWorld.player.inc_stat(stat)
                self.text_area.insert("end", '\n' + text)

            elif user_input == "stats":
                text = self.gameWorld.player.get_stats_string()
                self.text_area.insert("end", '\n' + text)

            elif user_input == "help":
                pass

            elif user_input == "exit":
                self.pack_forget()

            else:
                self.text_area.insert("end", " <--> Invalid command. Type 'help' for possible commands")

        if user_input == "help" and not the_end:
            self.display_help()
