from models.media_item import Genre

class GenreService:
    def __init__(self, conn):
        self.conn = conn

    def get_or_create(self, name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM genres WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row != None:
            return Genre(row[0], row[1])
        else:
            cursor.execute("INSERT INTO genres (name) VALUES (?)", (name,))
            self.conn.commit()
            return Genre(cursor.lastrowid, name)

    def get_all(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM genres")
        rows = cursor.fetchall()
        genre_list = []
        for row in rows:
            genre_list.append(Genre(row[0], row[1]))
        return genre_list
