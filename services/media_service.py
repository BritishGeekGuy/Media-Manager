import uuid
import datetime

from models.media_item import Artist
from models.media_item import Genre
from models.media_item import MediaItem

from services.artist_service import ArtistService
from services.genre_service import GenreService

class MediaService:
    def __init__(self, conn):
        self.conn = conn

    def add(self, album_title, media_format, release_date, barcode, cover_path, artists=None, genres=None, album_uuid=None):

        if album_uuid == None:
            album_uuid = str(uuid.uuid4())

        date_added = datetime.date.today()
        cursor = self.conn.cursor()

        artists = artists if artists is not None else []
        genres = genres if genres is not None else []

        artist_service = ArtistService(self.conn)
        genre_service = GenreService(self.conn)

        artist_list = []
        genre_list = []

        for name in artists:
            artist_list.append(artist_service.get_or_create(name))
        
        for name in genres:
            genre_list.append(genre_service.get_or_create(name))
        
        cursor.execute("INSERT INTO media_items (uuid, album_title, format, date_added, release_date, barcode, cover_path) VALUES (?, ?, ?, ?, ?, ?, ?)", (album_uuid, album_title, media_format, date_added, release_date, barcode, cover_path))

        for artist in artist_list:
            cursor.execute("INSERT INTO media_item_artists (media_item_uuid, artist_id) VALUES (?, ?)", (album_uuid, artist.id))
        for genre in genre_list:
            cursor.execute("INSERT INTO media_item_genres (media_item_uuid, genre_id) VALUES (?, ?)" , (album_uuid, genre.id))
        
        self.conn.commit()
        return(MediaItem(album_uuid, album_title, media_format, date_added, release_date, barcode, cover_path, artists=artist_list, genres=genre_list))
    
    def get_all(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM media_items")
        rows = cursor.fetchall()
        media_item_list = []

        for row in rows:
            artist_rows = cursor.execute("SELECT artists.id, artists.name FROM artists JOIN media_item_artists ON artists.id = media_item_artists.artist_id WHERE media_item_artists.media_item_uuid = ?", (row[0],)).fetchall()
            artist_list = [Artist(a[0], a[1]) for a in artist_rows]

            genre_rows = cursor.execute("SELECT genres.id, genres.name FROM genres JOIN media_item_genres ON genres.id = media_item_genres.genre_id WHERE media_item_genres.media_item_uuid = ?", (row[0],)).fetchall()
            genre_list = [Genre(g[0], g[1]) for g in genre_rows]

            media_item = MediaItem(row[0],row[1], row[2], row[3], row[4], row[5], row[6], artists=artist_list, genres=genre_list)
            media_item_list.append(media_item)
        return media_item_list

    def get_by_uuid(self, album_uuid):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM media_items WHERE uuid = ?", (album_uuid,))
        row = cursor.fetchone()

        artist_rows = cursor.execute("SELECT artists.id, artists.name FROM artists JOIN media_item_artists ON artists.id = media_item_artists.artist_id WHERE media_item_artists.media_item_uuid = ?", (row[0],)).fetchall()
        artist_list = [Artist(a[0], a[1]) for a in artist_rows]

        genre_rows = cursor.execute("SELECT genres.id, genres.name FROM genres JOIN media_item_genres ON genres.id = media_item_genres.genre_id WHERE media_item_genres.media_item_uuid = ?", (row[0],)).fetchall()
        genre_list = [Genre(g[0], g[1]) for g in genre_rows]

        media_item = MediaItem(row[0],row[1], row[2], row[3], row[4], row[5], row[6], artists=artist_list, genres=genre_list)
        return media_item

    def delete(self, album_uuid):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM media_items WHERE uuid = ?", (album_uuid, ))
        self.conn.commit()

    def update(self, album_uuid, album_title, media_format, release_date, barcode, cover_path, artists=None, genres=None):
        cursor = self.conn.cursor()

        artist_service = ArtistService(self.conn)
        genre_service = GenreService(self.conn)

        artists = artists if artists is not None else []
        genres = genres if genres is not None else []

        artist_list = []
        genre_list = []

        for name in artists:
            artist_list.append(artist_service.get_or_create(name))

        for name in genres:
            genre_list.append(genre_service.get_or_create(name))

        cursor.execute("UPDATE media_items SET album_title = ?, format = ?, release_date = ?, barcode = ?, cover_path = ? WHERE uuid = ?", (album_title, media_format, release_date, barcode, cover_path, album_uuid))
        cursor.execute("DELETE FROM media_item_artists WHERE media_item_uuid = ?", (album_uuid, ))
        cursor.execute("DELETE FROM media_item_genres WHERE media_item_uuid = ?", (album_uuid, ))

        for artist in artist_list:
            cursor.execute("INSERT INTO media_item_artists (media_item_uuid, artist_id) VALUES (?, ?)", (album_uuid, artist.id))
        for genre in genre_list:
            cursor.execute("INSERT INTO media_item_genres (media_item_uuid, genre_id) VALUES (?, ?)" , (album_uuid, genre.id))

        self.conn.commit()
