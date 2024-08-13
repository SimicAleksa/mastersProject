import tkinter as tk
from tkinter import ttk, messagebox
import os


class GptCreatorFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Create the large text area for the GPT prompt
        self.prompt_label = ttk.Label(self, text="Enter your GPT Prompt:")
        self.prompt_label.pack(pady=10)

        self.prompt_text = tk.Text(self, height=10, width=60, wrap=tk.WORD)
        self.prompt_text.pack(pady=10,padx = 10)

        # Create the smaller text area for the game name
        self.name_label = ttk.Label(self, text="Enter the Name of Your Game:")
        self.name_label.pack(pady=10)

        self.name_text = tk.Entry(self, width=30)
        self.name_text.pack(pady=10,padx=10)

        # Create the generate button
        self.generate_button = ttk.Button(self, text="Generate", command=self.generate_game)
        self.generate_button.pack(pady=20)

    def generate_game(self):
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        game_name = self.name_text.get().strip()

        if prompt and game_name:
            print(f"Generating game '{game_name}' with prompt:\n{prompt}")
        else:
            messagebox.showwarning("Input Error", "Please fill in both fields.")