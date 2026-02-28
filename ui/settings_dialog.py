import customtkinter as ctk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import os
import csv

from customtkinter import CTkFont

from database.schema import create_tables
from services.config_service import ConfigService
from services.media_service import MediaService

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, conn, main_window):
        super().__init__()
        self.conn = conn
        self.title("Settings")
        self.geometry("400x200")

        self.config_service = ConfigService()
        self.main_window = main_window

        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.appearance_label = ctk.CTkLabel(self.form_frame, text="Appearance:", font=CTkFont(size=14, weight="bold"))
        self.appearance_label.pack(pady=(0, 10))

        self.light_dark_button = ctk.CTkButton(self.form_frame, text="Light/Dark Mode", command=self.set_light_dark, height=30, width=300)
        self.light_dark_button.pack(pady=(0, 5))

        self.data_label = ctk.CTkLabel(self.form_frame, text="Data:", font=CTkFont(size=14, weight="bold"))
        self.data_label.pack(pady=(0, 10))

        self.export_button = ctk.CTkButton(self.form_frame, text="Export CSV", command=self.export_csv, height=30, width=300)
        self.export_button.pack(pady=(0, 5))

        self.erase_database_button = ctk.CTkButton(self.form_frame, text="Erase Database", command=self.erase_database, height=30, width=300)
        self.erase_database_button.pack(pady=(0,5))

    def erase_database(self):
        message = messagebox.askyesno("Erase Database?", "The database will be unrecoverable after!", parent=self)

        if message:
            try:
                os.remove("data/database.db")
                create_tables(self.conn)
                messagebox.showinfo("Erased Database", "Database was successfully erased!", parent=self)

            except:
                messagebox.showerror("Error", "Could not erase and create new database", parent=self)

    def set_light_dark(self):
        if self.config_service.get_value("appearance","theme") == "dark":
            self.config_service.set_value("appearance","theme", "light")
        else:
            self.config_service.set_value("appearance","theme", "dark")

        self.main_window.apply_theme()

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")],parent=self)

        if path:
            media_service = MediaService(self.conn)

            items = media_service.get_all()

            with open(path, "w") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Album Title", "Artist", "Genre", "Format", "Release Date", "Barcode"])

                for item in items:
                    artists = ", ".join([a.name for a in item.artists])
                    genres = ", ".join([g.name for g in item.genres])

                    writer.writerow([item.album_title, artists, genres, item.format, item.release_date, item.barcode])

                messagebox.showinfo("Export Successful!", "The database was exported successfully!", parent=self)