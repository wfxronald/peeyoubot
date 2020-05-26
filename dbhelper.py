# This file was used when testing the bot using the local SQLite database
# The actual deployment does not use this, instead the database is implemented on PostgreSQL
import sqlite3


class DBHelper:
    def __init__(self, dbname="piubot.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS SongsCleared (id INTEGER PRIMARY KEY, song TEXT NOT NULL, chatid TEXT, level INTEGER)"
        self.conn.execute(stmt)
        self.conn.commit()

        stmt = "CREATE TABLE IF NOT EXISTS User (chatid TEXT PRIMARY KEY, level INTEGER)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_user(self, chatid, level):
        stmt = "INSERT INTO User (chatid, level) VALUES (?, ?)"
        args = (chatid, level)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def update_user(self, chatid, level):
        stmt = "UPDATE User SET level = ? WHERE chatid = ?"
        args = (level, chatid)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_user_level(self, chatid):
        stmt = "SELECT level FROM User WHERE chatid = (?)"
        args = (chatid, )
        return self.conn.execute(stmt, args)

    def add_item(self, song, chatid):
        stmt = "INSERT INTO SongsCleared (id, song, chatid, level) VALUES (?, ?, ?, ?)"
        last_row_id = self.conn.execute("SELECT MAX(id) FROM SongsCleared") 
        for x in last_row_id:
            index = x[0] + 1

        lvl_stmt = self.get_user_level(chatid)
        for y in lvl_stmt:
            level = y[0]

        args = (index, song, chatid, level)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_item(self, song, chatid):
        lvl_stmt = self.get_user_level(chatid)
        for y in lvl_stmt:
            level = y[0]

        stmt = "DELETE FROM SongsCleared WHERE song = (?) AND chatid = (?) AND level = (?)"
        args = (song, chatid, level)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_items(self, chatid):
        lvl_stmt = self.get_user_level(chatid)
        for y in lvl_stmt:
            level = y[0]

        stmt = "SELECT song FROM SongsCleared WHERE chatid = (?) AND level = (?)"
        args = (chatid, level)
        return [x[0] for x in self.conn.execute(stmt, args)]

        