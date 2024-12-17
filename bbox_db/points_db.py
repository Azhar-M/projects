import sqlite3

con = sqlite3.connect('points.db')
cur = con.cursor()

cmd_points = '''
        CREATE TABLE IF NOT EXISTS points (
            x_m REAL,
            y_m REAL, 
            z_m REAL,
            lon REAL,
            lat REAL
            );
            '''
cur.execute(cmd_points)
con.commit()
con.close()