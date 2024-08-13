import tkinter as tk
from tkinter import ttk, messagebox

from mastersProject.enums_consts import POSSIBLE_COMMANDS
from mastersProject.interpreter import parse_dsl
from PIL import ImageTk
from PIL import Image

from os.path import join, dirname

import os

# Help command message
help_message = "Possible commands:\n" + "\n".join(POSSIBLE_COMMANDS)


class GamePlayFrame(ttk.Frame):
    def __init__(self, parent, game_title, with_images):
        super().__init__(parent)
        self.this_folder = dirname(__file__)
        try:
            self.gameWorld = parse_dsl("gameDSL.tx", game_title)
        except:
            messagebox.showinfo("Information", "Game code is invalid. You need to verify it.")
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
        self.input_entry.bind("<Return>", lambda event: self.process_user_input(event, with_images, game_title))

        if with_images:
            self.image_label = tk.Label(self, width=512, height=512)
            self.image_label.pack()
            self.generate_image(self.gameWorld.regions[0].name, game_title)

    def generate_image(self, region_name, game_title):
        image_path = os.path.join("if_dsl_gui_ai/games", game_title, region_name + ".png")
        if os.path.exists(image_path):
            self.img_fromPipe = Image.open(image_path)
        else:
            self.img_fromPipe = Image.open(join(self.this_folder, "noImg.png"))
        self.img = self.img_fromPipe.resize((512, 512))
        self.img = ImageTk.PhotoImage(self.img)
        self.image_label.config(image=self.img)

    def display_help(self):
        self.text_area.insert("end", "\n\n" + help_message + "\n\n")

    def process_user_input(self, event, with_images, game_title):
        user_input = self.input_entry.get().strip()
        self.text_area.insert("end", '\n' + user_input)
        self.input_entry.delete(0, tk.END)
        the_end = False

        if self.gameWorld.player.position == self.gameWorld.final_position:
            possible_moves = ["move N", "move E", "move S", "move W"]
            for door in self.gameWorld.final_position.connections:
                possible_move = "move " + door
                possible_moves.remove(possible_move)
            if user_input in possible_moves:
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", "THE END")
                the_end = True
                if with_images:
                    self.img = ImageTk.PhotoImage(file=join(self.this_folder, "theEnd.png"))
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
                        self.generate_image(self.gameWorld.player.position.name, game_title)

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
                text = self.gameWorld.player.print_item_info(item,self.gameWorld)
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

            elif user_input == "exit":
                self.pack_forget()

            else:
                self.text_area.insert("end", " <--> Invalid command. Type 'help' for possible commands")

        if user_input == "help" and not the_end:
            self.display_help()

