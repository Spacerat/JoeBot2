
import sqlite3

def query(sql,args=None):
    connection = sqlite3.connect('data/database')
    curs = connection.cursor()
    result = None
    if args: result = curs.execute(sql, args)
    else: result = curs.execute(sql)
    if result:
        if sql.startswith("INSERT") or sql.startswith("UPDATE"):
            connection.commit()
            return curs.lastrowid
        else:
            return curs.fetchall()
    else:
        connection.commit()
