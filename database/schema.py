def create_tables(conn):
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artists(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS genres(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS media_items(
            uuid TEXT PRIMARY KEY,
            album_title TEXT NOT NULL,
            format TEXT NOT NULL CHECK(format IN ('CD', 'Vinyl')),
            date_added DATE NOT NULL,
            release_date DATE,
            barcode TEXT,
            cover_path TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS media_item_artists(
            media_item_uuid TEXT NOT NULL,
            artist_id INTEGER NOT NULL,
            PRIMARY KEY (media_item_uuid, artist_id),
            FOREIGN KEY (media_item_uuid) REFERENCES media_items(uuid) ON DELETE CASCADE,
            FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS media_item_genres(
            media_item_uuid TEXT NOT NULL,
            genre_id INTEGER NOT NULL,
            PRIMARY KEY (media_item_uuid, genre_id),
            FOREIGN KEY (media_item_uuid) REFERENCES media_items(uuid) ON DELETE CASCADE,
            FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()