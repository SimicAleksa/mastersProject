import tkinter as tk
from tkinter import ttk, messagebox
from functools import partial  # For triggering only when the button is clicked
import requests

from mastersProject.interpreter import parse_dsl
from PIL import ImageTk, Image
from os.path import join, dirname
import os
import openai
import base64
from io import BytesIO
from openai import OpenAI

# Initialize OpenAI API with your API key
client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))


class PictureCreatorFrame(ttk.Frame):
    def __init__(self, parent, games_directory, selected_game):
        super().__init__(parent)
        self.default_img = Image.open(os.path.join(os.getcwd(), "gui\\resources\\noImage.png"))
        try:
            self.gameWorld = parse_dsl("gameDSL.tx", selected_game)
        except:
            messagebox.showinfo("Information", "Game code is invalid. You need to verify it.")
            return

        self.counter = -1
        self.next_region_button = tk.Button(self, text="Next region",
                                            command=partial(self.generate_next_region, games_directory))
        self.next_region_button.grid(row=6, column=1, columnspan=2, padx=10, pady=10)

    def generate_next_region(self, games_directory):
        if self.counter < len(self.gameWorld.regions):
            self.counter += 1
            if self.counter == len(self.gameWorld.regions):
                messagebox.showinfo("Information", "You have created pictures for your game.")
                self.pack_forget()
            else:
                self.next_region_button.grid_remove()
                self.region_name = self.gameWorld.regions[self.counter].name
                self.text_area = tk.Text(self, wrap=tk.WORD, width=80, height=10)
                self.text_area.insert("1.0", self.gameWorld.regions[self.counter].print_self())
                self.text_area.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

                self.generate_button = tk.Button(self, text="Generate", command=partial(self.generate_image))
                self.generate_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

                self.save_button = tk.Button(self, text="Pick", command=partial(self.save_image, games_directory))
                self.save_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

                self.image_label0 = tk.Label(self, width=256, height=256)
                self.image_label1 = tk.Label(self, width=256, height=256)
                self.image_label2 = tk.Label(self, width=256, height=256)
                self.image_label3 = tk.Label(self, width=256, height=256)

                self.image_label0.grid(row=2, column=0)
                self.image_label1.grid(row=2, column=1)
                self.image_label2.grid(row=4, column=0)
                self.image_label3.grid(row=4, column=1)

                if not os.path.isfile(games_directory + "/" + self.region_name + ".png"):
                    self.display_default_images()
                else:
                    messagebox.showinfo("Information", "You have already created pictures for your game. If you want "
                                                       "to change them, remove all of them from the game directory "
                                                       "then try the picture creator once more.")

    def display_default_images(self):
        self.img0_fromPipe = self.default_img
        self.img1_fromPipe = self.default_img
        self.img2_fromPipe = self.default_img
        self.img3_fromPipe = self.default_img

        self.update_image_labels()

        self.radio_var = tk.StringVar(value="Option 1")

        self.radio_button0 = tk.Radiobutton(self, text="Option 1", variable=self.radio_var, value="Option 1")
        self.radio_button1 = tk.Radiobutton(self, text="Option 2", variable=self.radio_var, value="Option 2")
        self.radio_button2 = tk.Radiobutton(self, text="Option 3", variable=self.radio_var, value="Option 3")
        self.radio_button3 = tk.Radiobutton(self, text="Option 4", variable=self.radio_var, value="Option 4")

        self.radio_button0.grid(row=3, column=0, padx=1, pady=1)
        self.radio_button1.grid(row=3, column=1, padx=1, pady=1)
        self.radio_button2.grid(row=5, column=0, padx=1, pady=1)
        self.radio_button3.grid(row=5, column=1, padx=1, pady=1)

    def generate_image(self):
        prompt = self.text_area.get("1.0", "end-1c").lower()

        response = client.images.generate(
                model="dall-e-2",
                prompt=prompt,
                size="256x256",
                n=4,
            )
        self.img0_fromPipe = Image.open(BytesIO(requests.get(response.data[0].url).content))
        self.img1_fromPipe = Image.open(BytesIO(requests.get(response.data[1].url).content))
        self.img2_fromPipe = Image.open(BytesIO(requests.get(response.data[2].url).content))
        self.img3_fromPipe = Image.open(BytesIO(requests.get(response.data[3].url).content))

        self.update_image_labels()

    def update_image_labels(self):
        self.img0 = ImageTk.PhotoImage(self.img0_fromPipe)
        self.img1 = ImageTk.PhotoImage(self.img1_fromPipe)
        self.img2 = ImageTk.PhotoImage(self.img2_fromPipe)
        self.img3 = ImageTk.PhotoImage(self.img3_fromPipe)
        self.image_label0.config(image=self.img0)
        self.image_label1.config(image=self.img1)
        self.image_label2.config(image=self.img2)
        self.image_label3.config(image=self.img3)

    def save_image(self, games_directory):
        selected_image = None
        if self.radio_var.get() == "Option 1":
            selected_image = self.img0_fromPipe
        elif self.radio_var.get() == "Option 2":
            selected_image = self.img1_fromPipe
        elif self.radio_var.get() == "Option 3":
            selected_image = self.img2_fromPipe
        elif self.radio_var.get() == "Option 4":
            selected_image = self.img3_fromPipe

        if selected_image:
            selected_image.save(games_directory + '/' + self.region_name + '.png')

        self.save_button.grid_remove()
        self.next_region_button.grid(row=6, column=1, columnspan=2, padx=10, pady=10)
