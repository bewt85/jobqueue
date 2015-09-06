import sqlite3 as sql

class Queue(object):
  def __init__(self, db_filename):
    self.con = sql.connect(db_filename)
    self._create_tables()

  def _create_tables(self):
    with self.con:
      cur = self.con.cursor()
      cur.execute("CREATE TABLE IF NOT EXISTS "
                  "Arguments(Id INTEGER PRIMARY KEY AUTOINCREMENT, "
                            "Args TEXT, Status TEXT, "
                            "Created INTEGER)")

  def put(self, arguments):
    with self.con:
      cur = self.con.cursor()
      cur.execute("INSERT INTO Arguments (Args, Status, Created) "
                  "VALUES (?,'PENDING', strftime('%s', 'now'))", (arguments,))

  def pop(self):
    with self.con:
      cur = self.con.cursor()
      cur.execute("BEGIN EXCLUSIVE")
      cur.execute("SELECT Id,Args FROM Arguments WHERE Status='PENDING' "
                  "ORDER BY Id LIMIT 1")
      try:
        row_id, args = cur.fetchone()
      except TypeError:
        raise Exception("No more arguments to pop")
      cur.execute("UPDATE Arguments SET Status='UNKNOWN' WHERE Id=?", (row_id,))
      return args
