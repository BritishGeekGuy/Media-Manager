import os
import uuid

import customtkinter as ctk
import datetime
import tkinter.messagebox as messagebox
import shutil

from services.artist_service import ArtistService
from services.genre_service import GenreService
from services.media_service import MediaService
from tkinter import filedialog

class AddEditDialog (ctk.CTkToplevel):
    def __init__(self, conn, on_save=None, media_item=None):
        super().__init__()
        self.media_item = media_item
        self.conn = conn
        self.on_save = on_save
        self.cover_path = None
        if media_item is not None:
            self.title("Edit Media")
        else:
            self.title("Add Media")
        self.geometry("500x650")

        self.media_service = MediaService(self.conn)
        if self.media_item is not None:
            self.album_uuid = self.media_item.uuid
        else:
            self.album_uuid = str(uuid.uuid4())

        self.form_frame = ctk.CTkScrollableFrame(self)
        self.form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.title_label = ctk.CTkLabel(self.form_frame, text="Album Title")
        self.title_label.pack(pady=(10,0))

        self.title_entry = ctk.CTkEntry(self.form_frame, width=300)
        self.title_entry.pack(pady=(0,10))

        self.format_label = ctk.CTkLabel(self.form_frame, text="Format")
        self.format_label.pack(pady=(10,0))

        self.format_entry = ctk.CTkOptionMenu(self.form_frame, values=["CD", "Vinyl"])
        self.format_entry.pack(pady=(0,10))

        self.artist_label = ctk.CTkLabel(self.form_frame, text="Artist")
        self.artist_label.pack(pady=(10,0))

        self.artist_entry = ctk.CTkComboBox(self.form_frame, values=[], width=300)
        self.artist_entry.pack(pady=(0,10))
        self.artist_entry.set("")

        self.genre_label = ctk.CTkLabel(self.form_frame, text="Genre")
        self.genre_label.pack(pady=(10,0))

        self.genre_entry = ctk.CTkComboBox(self.form_frame, values=[], width=300)
        self.genre_entry.pack(pady=(0,10))
        self.genre_entry.set("")

        self.release_date_label = ctk.CTkLabel(self.form_frame, text="Release Date (DD-MM-YYYY)")
        self.release_date_label.pack(pady=(10,0))

        self.release_date_entry = ctk.CTkEntry(self.form_frame, width=300)
        self.release_date_entry.pack(pady=(0,10))

        self.barcode_label = ctk.CTkLabel(self.form_frame, text="Barcode")
        self.barcode_label.pack(pady=(10,0))

        self.barcode_entry = ctk.CTkEntry(self.form_frame, width=300)
        self.barcode_entry.pack(pady=(0,10))

        self.cover_label = ctk.CTkLabel(self.form_frame, text="Cover Image")
        self.cover_label.pack(pady=(10,0))

        self.cover_button = ctk.CTkButton(self.form_frame, text="Choose Image", width=300, command=self.choose_image)
        self.cover_button.pack(pady=(0,10))

        self.save_button = ctk.CTkButton(self.form_frame, text="Save", width=300, command=self.save)
        self.save_button.pack(pady=(20,5))

        self.cancel_button = ctk.CTkButton(self.form_frame, text="Cancel", width=300, fg_color="grey", command=lambda: self.destroy())
        self.cancel_button.pack(pady=(0,10))

        self.after(100, self.load_options)

    def load_options(self):
        artist_service = ArtistService(self.conn)
        genre_service = GenreService(self.conn)
        artists = artist_service.get_all()
        genres = genre_service.get_all()
        self.artist_entry.configure(values=[a.name for a in artists])
        self.genre_entry.configure(values=[g.name for g in genres])
        if self.media_item is not None:
            self.populate_fields()

    def save(self):
        if not self.title_entry.get() or not self.artist_entry.get() or not self.genre_entry.get():
            messagebox.showwarning("Missing Fields", "Please fill in the Album Title, Artist and Genre fields", parent=self)
            return

        album_title = self.title_entry.get()
        artists = self.artist_entry.get()
        genres = self.genre_entry.get()
        media_format = self.format_entry.get()
        date_str = self.release_date_entry.get().replace("/", "-")
        if date_str != "":
            try:
                release = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
            except ValueError:
                messagebox.showwarning("Invalid Date", "Please enter the date in DD-MM-YYYY format.", parent=self)
                return

            if release > datetime.date.today():
                messagebox.showwarning("Invalid Date", "Release date cannot be in the future.", parent=self)
                return
        else:
            release = None
        barcode = self.barcode_entry.get()

        if self.media_item is not None:
            self.media_service.update(self.media_item.uuid, album_title, media_format, release, barcode, self.cover_path, [artists], [genres])
        else:
            self.media_service.add(album_title, media_format, release, barcode,self.cover_path,[artists], [genres], self.album_uuid)

        if self.on_save:
            self.on_save()
        self.destroy()

    def choose_image(self):
        path = filedialog.askopenfilename(parent=self, filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if path:
            new_filename = self.album_uuid + os.path.splitext(path)[1]
            destination = os.path.join("data/covers/", new_filename)
            os.makedirs("data/covers/", exist_ok=True)
            shutil.copyfile(path, destination)

            self.cover_path = destination
            self.cover_button.configure(text="Image Selected")

    def populate_fields(self):
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, self.media_item.album_title)

        self.format_entry.set(self.media_item.format)

        if self.media_item.artists:
            self.artist_entry.set(self.media_item.artists[0].name)

        if self.media_item.genres:
            self.genre_entry.set(self.media_item.genres[0].name)

        if self.media_item.release_date:
            self.release_date_entry.delete(0, "end")
            current_release_date = datetime.datetime.strptime(self.media_item.release_date, "%Y-%m-%d").date()
            self.release_date_entry.insert(0, current_release_date)

        self.barcode_entry.delete(0, "end")
        self.barcode_entry.insert(0, self.media_item.barcode)

        if self.media_item.cover_path:
            self.cover_path = self.media_item.cover_path
            self.cover_button.configure(text="Image Selected")
