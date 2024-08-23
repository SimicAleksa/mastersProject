import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from mastersProject.gui.codeEditorFrame import CodeEditorFrame
from mastersProject.gui.gameFrame import GamePlayFrame
from mastersProject.gui.gptCreationFrame import GptCreatorFrame
from mastersProject.gui.pictureCreatorFrame import PictureCreatorFrame


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Interactive Fiction Creator")

        window_width = 1200
        window_height = 985
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y - 50}")

        # Configure the main menu
        self.navbar = tk.Menu(self.root)
        self.root.config(menu=self.navbar)
        self.navbar.add_command(label="Start", command=self.show_start_frame)
        self.navbar.add_command(label="Create Fiction", command=lambda: self.show_fiction_frame(None))
        self.navbar.add_command(label="GPT creation", command=self.show_gpt_creation_frame)
        self.navbar.add_command(label="Library", command=self.show_library_frame)

        # Background setup on root window
        pill_image = Image.open(os.path.join(os.getcwd(), "gui\\background.jpg"))
        resized_image = pill_image.resize((window_width, window_height))
        background_image = ImageTk.PhotoImage(resized_image)
        background_label = tk.Label(self.root, image=background_image)
        background_label.place(relwidth=1, relheight=1)
        self.background_image = background_image

        # Initialize frames
        self.start_frame = ttk.Frame(self.root, padding=20)
        self.fiction_frame = ttk.Frame(self.root, padding=20)
        self.fiction_frame.config(style="Transparent.TFrame")
        self.library_frame = ttk.Frame(self.root, padding=20)
        self.library_frame.config(style="Transparent.TFrame")
        self.gpt_creation_frame = ttk.Frame(self.root, padding=20)
        self.play_frame = ttk.Frame(self.root, padding=20)
        self.picture_creator_frame = ttk.Frame(self.root, padding=20)

        # Style setup
        frame_bg = '#ffffff'
        frame_opacity = 0.5
        style = ttk.Style()
        style.configure("Transparent.TFrame", background=self.adjust_color_opacity(frame_bg, frame_opacity))

        # Initialize text area
        self.text_area = tk.Text(self.fiction_frame, wrap=tk.WORD, width=90, height=50)
        self.text_area.pack(pady=10)

        # Initialize other widgets
        self.fiction_type = tk.StringVar(value="game")
        self.play_button = ttk.Button(self.library_frame, text="Play", command=self.show_play_frame)
        self.play_button.pack(pady=10)

        self.picture_creator_button = ttk.Button(self.library_frame, text="Picture creator",
                                                 command=self.show_picture_creator_frame)
        self.picture_creator_button.pack(pady=10)

        self.with_images_var = tk.BooleanVar()
        self.with_images_checkbox = ttk.Checkbutton(self.library_frame, text="With Images",
                                                    variable=self.with_images_var)
        self.with_images_checkbox.pack(pady=10)

        self.generate_infinitely_var = tk.BooleanVar()
        self.generate_infinitely_checkbox = ttk.Checkbutton(self.library_frame, text="Generate infinitely",
                                                    variable=self.generate_infinitely_var)
        self.generate_infinitely_checkbox.pack(pady=10)

        self.reload_previous_game = tk.BooleanVar()
        self.reload_previous_game_checkbox = ttk.Checkbutton(self.library_frame, text="Reload saved game",
                                                    variable=self.reload_previous_game)
        self.reload_previous_game_checkbox.pack(pady=10)

        # Load the library
        self.load_library()

        # Show the start frame initially
        self.show_start_frame()

        self.root.mainloop()

    def adjust_color_opacity(self, color, opacity):
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        return f'#{int(r * opacity):02x}{int(g * opacity):02x}{int(b * opacity):02x}'

    def show_play_frame(self):
        self._hide_all_frames()
        selected_game = self.games_listbox.get(tk.ACTIVE)
        if selected_game:
            games_directory = "games/" + selected_game + "/" + selected_game
            with open(games_directory, "r") as file:
                content = file.read()
            with_images = self.with_images_var.get()
            generate_infinitely = self.generate_infinitely_var.get()
            reload_saved_file = self.reload_previous_game.get()
            self.play_frame = GamePlayFrame(self.root, selected_game, with_images,generate_infinitely,reload_saved_file)
            self.play_frame.pack(padx=20, pady=100)

    def show_start_frame(self):
        self._hide_all_frames()
        self.start_frame.pack()

    def show_fiction_frame(self, content=None):
        self._hide_all_frames()
        self.on_game_selected(content)

    def show_library_frame(self):
        self._hide_all_frames()
        self.load_games()
        self.library_frame.pack(padx=20, pady=200)

    def show_gpt_creation_frame(self):
        self._hide_all_frames()
        self.gpt_creation_frame = GptCreatorFrame(self.root)
        self.gpt_creation_frame.pack(padx=20, pady=100)

    def show_picture_creator_frame(self):
        self._hide_all_frames()
        selected_game = self.games_listbox.get(tk.ACTIVE)
        if selected_game:
            games_directory = "games/" + selected_game
            self.picture_creator_frame = PictureCreatorFrame(self.root, games_directory, selected_game)
            self.picture_creator_frame.pack(padx=60, pady=60)

    def on_game_selected(self, content=None):
        self.fiction_frame = CodeEditorFrame(self.root, content)
        self.fiction_frame.pack(padx=20, pady=20)
        if content is None:
            messagebox.showinfo("Information", "Steps when saving your game:\n"
                                               "1) Create a new folder with the same name as your game (e.g., 'simplegame.game') inside the games folder.\n"
                                               "2) Save your game inside the folder you just created.\n"
                                               "(e.g., 'games/simplegame.game/simplegame.game').")

    def load_library(self):
        self.games_listbox = tk.Listbox(self.library_frame, selectmode=tk.SINGLE)
        self.games_listbox.pack(padx=10, pady=10)

        self.load_games()

        self.load_button = ttk.Button(self.library_frame, text="Load code", command=self.load_selected_game)
        self.load_button.pack(pady=10)

    def load_games(self):
        games_directory = "games"
        saved_files = [f for f in os.listdir(os.path.join(os.getcwd(), games_directory)) if f.endswith(".game")]
        self.games_listbox.delete(0, tk.END)
        for saved_file in saved_files:
            self.games_listbox.insert(tk.END, saved_file)

    def load_selected_game(self):
        selected_game = self.games_listbox.get(tk.ACTIVE)
        if selected_game:
            games_directory = "games/" + selected_game
            game_path = os.path.join(games_directory, selected_game)
            with open(game_path, "r") as file:
                content = file.read()
                self.show_fiction_frame(content)

    def _hide_all_frames(self):
        for frame in [self.start_frame, self.fiction_frame, self.library_frame, self.gpt_creation_frame,
                      self.play_frame, self.picture_creator_frame]:
            frame.pack_forget()
