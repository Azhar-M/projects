import sqlite3

con = sqlite3.connect('bbox_grid.db')
cur = con.cursor()

cmd_bbox = '''
    CREATE TABLE IF NOT EXISTS bbox (
        bbox_id INTEGER PRIMARY KEY,
        top_left_x REAL, top_left_y REAL,
        top_right_x REAL, top_right_y REAL,
        bottom_right_x REAL, bottom_right_y REAL,
        bottom_left_x REAL, bottom_left_y REAL
    );
'''
cur.execute(cmd_bbox)
con.commit()
con.close()