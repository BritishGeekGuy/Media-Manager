# Simple Media Manager
# Created by BritishGeekGuy
# Released under GNU GPLv3

prog_ver = "1.0.1"

from database.schema import *
from database.connection import *

from services.media_service import MediaService

from ui.main_window import MainWindow

conn = db_connect()
create_tables(conn)
media_service = MediaService(conn)

app = MainWindow(conn)
app.mainloop()

conn.close()
