import datetime

class Artist:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Genre:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class MediaItem:
    def __init__(self, uuid, album_title, media_format, date_added, release_date=None, barcode = None, cover_path = None, artists=None, genres=None):
        self.uuid = uuid
        self.album_title = album_title
        self.format = media_format
        self.date_added = date_added
        self.release_date = release_date
        self.barcode = barcode
        self.cover_path = cover_path
        self.artists = artists if artists is not None else []
        self.genres = genres if genres is not None else []
