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
      cur.execute("CREATE TABLE IF NOT EXISTS "
                  "Leases(Id INTEGER PRIMARY KEY AUTOINCREMENT, "
                         "Created INTEGER NOT NULL, "
                         "Expires INTEGER NOT NULL, "
                         "Status TEXT DEFAULT 'LET', "
                         "ArgumentsId INTEGER NOT NULL, "
                         "FOREIGN KEY(ArgumentsId) REFERENCES Arguments(Id))")

  def _create_lease(self, arg_id, timeout):
    with self.con:
      cur = self.con.cursor()
      cur.execute("INSERT INTO Leases (Created, Expires, ArgumentsId) "
                  "VALUES (strftime('%s', 'now'), "
                          "strftime('%s', 'now') + ?, "
                          "?)", (timeout, arg_id))

  def lease(self):
    arg_id, args = self._pop_with_id(status='LEASED')
    self._create_lease(arg_id, 3600)
    return arg_id

  def get(self, arg_id):
    with self.con:
      cur = self.con.cursor()
      cur.execute("SELECT (Args) "
                  "FROM Arguments "
                  "WHERE Id=?", (arg_id,))
      (args,) = cur.fetchone()
      return args

  def put(self, arguments):
    with self.con:
      cur = self.con.cursor()
      cur.execute("INSERT INTO Arguments (Args, Status, Created) "
                  "VALUES (?,'PENDING', strftime('%s', 'now'))", (arguments,))

  def _pop_with_id(self, status='UNKNOWN'):
    with self.con:
      cur = self.con.cursor()
      cur.execute("BEGIN EXCLUSIVE")
      cur.execute("SELECT Id,Args FROM Arguments WHERE Status='PENDING' "
                  "ORDER BY Id LIMIT 1")
      try:
        row_id, args = cur.fetchone()
      except TypeError:
        raise Exception("No more arguments to pop")
      cur.execute("UPDATE Arguments SET Status=? WHERE Id=?", (status, row_id))
      return row_id, args

  def pop(self, status='UNKNOWN'):
    row_id, args = self._pop_with_id(status=status)
    return args
