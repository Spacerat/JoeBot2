
import sqlite3


connection = sqlite3.connect('data/database')

def query(sql):
    curs = conn.cursor()
    result = curs.execute(q)
    if result:
        if sql.startswith("INSERT"):
            conn.commit()
            return cursor.lastrowid
        else:
            return cursor.fetchall()
    else:
        connection.commit()
