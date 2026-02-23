import os
import customtkinter as ctk
import tkinter.ttk as ttk
import tkinter
import tkinter.messagebox as messagebox

from PIL import Image, ImageTk
from customtkinter import CTkLabel
from services.media_service import MediaService
from ui.add_edit_dialog import AddEditDialog
from services.genre_service import GenreService

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MainWindow(ctk.CTk):
    def __init__(self, conn):
        super().__init__()
        self.attributes("-zoomed", True)
        self.resizable(True, True)
        self.geometry("1280x720")
        self.title("Media Manager")

        self.conn = conn
        self.media_service = MediaService(self.conn)
        self.current_cover_image = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.top_bar = ctk.CTkFrame(self)
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.top_bar.grid_columnconfigure(0, weight=1)
        self.top_bar.grid_columnconfigure(9, weight=1)

        self.search_bar = ctk.CTkEntry(self.top_bar, placeholder_text = "Search", width=300)
        self.search_bar.grid(row=0, column=1, padx=10, pady=10)
        self.search_bar.bind("<KeyRelease>", lambda e: self.filter_table())

        self.format_label = ctk.CTkLabel(self.top_bar, text="Format:")
        self.format_label.grid(row=0, column=2, padx=(10,0), pady=10)
        self.format_filter = ctk.CTkOptionMenu(self.top_bar, values=["All", "CD", "Vinyl"], command=lambda _: self.filter_table())
        self.format_filter.grid(row=0, column=3, padx=10, pady=10)

        self.genre_label = ctk.CTkLabel(self.top_bar, text="Genre:")
        self.genre_label.grid(row=0, column=4, padx=(10, 0), pady=10)
        self.genre_filter = ctk.CTkOptionMenu(self.top_bar, values=["All"], command=lambda _: self.filter_table())
        self.genre_filter.grid(row=0, column=5, padx=10, pady=10)

        self.add_button = ctk.CTkButton(self.top_bar, text="Add", command=self.open_add_dialog)
        self.add_button.grid(row=0, column=6, padx=10, pady=10)

        self.edit_button = ctk.CTkButton(self.top_bar, text="Edit", command=self.open_edit_dialog)
        self.edit_button.grid(row=0, column=7, padx=10, pady=10)

        self.delete_button = ctk.CTkButton(self.top_bar, text="Delete", command=self.delete_selected)
        self.delete_button.grid(row=0, column=8, padx=10, pady=10)

        self.main_content = ctk.CTkFrame(self)
        self.main_content.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.main_content.grid_columnconfigure(0, weight=3)
        self.main_content.grid_columnconfigure(1, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)

        self.table = ttk.Treeview(self.main_content, columns=("title", "artist", "genre", "format"), show="headings")
        self.table.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=30)
        style.configure("Treeview.Heading", background="#1f1f1f", foreground="white", relief="flat")
        style.map("Treeview", background=[("selected", "#1f6aa5")])
        self.table.heading("title", text="Album Title")
        self.table.heading("artist", text="Artist")
        self.table.heading("genre", text="Genre")
        self.table.heading("format", text="Format")
        self.table.bind("<<TreeviewSelect>>", self.on_row_select)

        self.detail_panel = ctk.CTkFrame(self.main_content)
        self.detail_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.detail_panel.grid_columnconfigure(0, weight=1)

        self.cover_image = tkinter.Label(self.detail_panel, text="No Cover")
        self.cover_image.grid(row=0, column=0, padx=10, pady=10)
        blank = Image.new("RGB", (200, 200), color="#2b2b2b")
        self.current_cover_image = ImageTk.PhotoImage(blank)
        self.cover_image.configure(image=self.current_cover_image)

        self.detail_title = ctk.CTkLabel(self.detail_panel, text="", font=ctk.CTkFont(size=16, weight="bold"))
        self.detail_title.grid(row=1, column=0, padx=10, pady=5)

        self.detail_artist = ctk.CTkLabel(self.detail_panel, text="")
        self.detail_artist.grid(row=2, column=0, padx=10, pady=2)

        self.detail_genre = ctk.CTkLabel(self.detail_panel, text="")
        self.detail_genre.grid(row=3, column=0, padx=10, pady=2)

        self.detail_format = ctk.CTkLabel(self.detail_panel, text="")
        self.detail_format.grid(row=4, column=0, padx=10, pady=2)

        self.detail_release_date = CTkLabel(self.detail_panel, text="")
        self.detail_release_date.grid(row=5, column=0, padx=10, pady=2)

        self.load_table()
        self.load_genre_filter()

    def load_table(self):
        for row in self.table.get_children():
            self.table.delete(row)
        items = self.media_service.get_all()
        for item in items:
            artists = ", ".join([a.name for a in item.artists])
            genres = ", ".join([a.name for a in item.genres])
            self.table.insert('', 'end', iid=item.uuid, values=(item.album_title, artists, genres, item.format))

        self.load_genre_filter()

        children = self.table.get_children()
        if children:
            self.table.selection_set(children[0])
            self.on_row_select(None)
        else:
            self.clear_detail_panel()

    def open_add_dialog(self):
        dialog = AddEditDialog(self.conn, self.load_table)
        dialog.grab_set()

    def open_edit_dialog(self):
        if not self.table.selection():
            messagebox.showwarning("No Selection", "Please select an item to edit.")
            return

        selected_item = self.media_service.get_by_uuid(self.table.selection()[0])
        print("selected_item:", selected_item)
        dialog = AddEditDialog(self.conn, self.load_table, selected_item)
        dialog.grab_set()

    def on_row_select(self, event):
        if not self.table.selection():
            return
        selected_item = self.media_service.get_by_uuid(self.table.selection()[0])
        self.detail_title.configure(text=selected_item.album_title)
        self.detail_artist.configure(text=", ".join([a.name for a in selected_item.artists]))
        self.detail_genre.configure(text=", ".join([g.name for g in selected_item.genres]))
        self.detail_format.configure(text=selected_item.format)
        self.detail_release_date.configure(text=selected_item.release_date)

        if selected_item.cover_path is not None and selected_item.cover_path != "":
            pil_image = Image.open(selected_item.cover_path)
            photo_image = ImageTk.PhotoImage(pil_image.resize((200,200)))
            self.current_cover_image = photo_image
            self.cover_image.configure(image=photo_image, text="")
        else:
            blank = Image.new("RGB", (200, 200), "#2b2b2b")
            blank_photo = ImageTk.PhotoImage(blank)
            self.current_cover_image = blank_photo
            self.cover_image.configure(image=blank_photo, text="No Cover")


    def delete_selected(self):
        if not self.table.selection():
            messagebox.showwarning("Warning", "You must select an item to delete")
            return

        answer = messagebox.askyesno("Warning", "Are you sure you want to delete this item?")
        if answer:
            selected_item = self.media_service.get_by_uuid(self.table.selection()[0])
            if selected_item.cover_path is not None and selected_item.cover_path != "":
                os.remove(selected_item.cover_path)
            self.media_service.delete(self.table.selection()[0])
            self.load_table()

    def filter_table(self):
        search_text = self.search_bar.get().lower()
        format_filter = self.format_filter.get()
        genre_filter = self.genre_filter.get()

        for row in self.table.get_children():
            self.table.delete(row)

        items = self.media_service.get_all()
        for item in items:
            artists = ", ".join([a.name for a in item.artists])
            genres = ", ".join([g.name for g in item.genres])

            if search_text and search_text not in item.album_title.lower() and search_text not in artists.lower():
                continue
            if format_filter != "All" and item.format != format_filter:
                continue
            if genre_filter != "All" and genre_filter not in genres:
                continue

            self.table.insert('', 'end', iid=item.uuid, values=(item.album_title, artists, genres, item.format))

    def load_genre_filter(self):
        genre_service = GenreService(self.conn)
        genres = genre_service.get_all()
        self.genre_filter.configure(values=["All"] + [g.name for g in genres])

    def clear_detail_panel(self):
        blank = Image.new("RGB", (200, 200), "#2b2b2b")
        blank_photo = ImageTk.PhotoImage(blank)
        self.current_cover_image = blank_photo
        self.cover_image.configure(image=blank_photo, text="No Cover")

        self.detail_title.configure(text="")
        self.detail_artist.configure(text="")
        self.detail_genre.configure(text="")
        self.detail_format.configure(text="")
        self.detail_release_date.configure(text="")
