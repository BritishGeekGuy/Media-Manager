from models.media_item import Artist

class ArtistService:
    def __init__(self, conn):
        self.conn = conn

    def get_or_create(self, name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM artists WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row != None:
            return Artist(row[0], row[1])
        else:
            cursor.execute("INSERT INTO artists (name) VALUES (?)", (name,))
            self.conn.commit()
            return Artist(cursor.lastrowid, name)

    def get_all (self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM artists")
        rows = cursor.fetchall()
        artist_list = []
        for row in rows:
            artist_list.append(Artist(row[0], row[1]))
        return artist_list