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