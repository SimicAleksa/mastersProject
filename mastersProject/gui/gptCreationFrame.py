import tkinter as tk
from tkinter import ttk, messagebox
import os

from mastersProject.game_generator import generate_game_from_prompt


class GptCreatorFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.prompt_label = ttk.Label(self, text="Enter your GPT Prompt:")
        self.prompt_label.pack(pady=10)

        self.prompt_text = tk.Text(self, height=10, width=60, wrap=tk.WORD)
        self.prompt_text.pack(pady=10, padx=10)

        self.name_label = ttk.Label(self, text="Enter the Name of Your Game:")
        self.name_label.pack(pady=10)

        self.name_text = tk.Entry(self, width=30)
        self.name_text.pack(pady=10, padx=10)

        self.generate_button = ttk.Button(self, text="Generate", command=self.generate_game)
        self.generate_button.pack(pady=20)

    def generate_game(self):
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        game_name = self.name_text.get().strip()

        if prompt and game_name:
            games_dir = "games"
            game_folder_path = os.path.join(games_dir, f"{game_name}.game")

            if os.path.exists(game_folder_path):
                messagebox.showwarning("Game Exists",
                                       f"A game with the name '{game_name}' already exists. Please choose a different name.")
                return

            try:
                os.makedirs(game_folder_path, exist_ok=True)

                game_file_path = os.path.join(game_folder_path, f"{game_name}.game")

                with open(game_file_path, "w") as game_file:
                    game_text = generate_game_from_prompt(prompt)
                    game_file.write(game_text)

                print(f"Game '{game_name}' has been created successfully with the provided prompt. Check library"
                      f" and game code for further corrections")
                messagebox.showinfo("Success", f"Game '{game_name}' has been created.")

                self.prompt_text.delete("1.0", tk.END)
                self.name_text.delete(0, tk.END)

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while creating the game: {e}")
        else:
            messagebox.showwarning("Input Error", "Please fill in both fields.")
