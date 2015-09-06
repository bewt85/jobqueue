import sqlite3 as sql
import time

class Queue(object):
  def __init__(self, db_filename):
    self.con = sql.connect(db_filename)
    self._create_tables()

  def _create_tables(self):
    with self.con:
      cur = self.con.cursor()
      cur.execute("CREATE TABLE IF NOT EXISTS "
                  "Arguments(Id INTEGER PRIMARY KEY AUTOINCREMENT, "
                            "Args TEXT NOT NULL, "
                            "Created INTEGER NOT NULL, "
                            "Status TEXT DEFAULT 'PENDING', "
                            "Timeout INTEGER DEFAULT 0)")

  def lease(self, timeout=3600):
    arg_id, args = self._pop_with_id(update='LEASED', timeout=timeout)
    return arg_id

  def status(self, arg_id, update=None):
    with self.con:
      cur = self.con.cursor()
      if update is None:
        cur.execute("SELECT Args, Status, Timeout "
                    "FROM Arguments "
                    "WHERE Id=?", (arg_id,))
        (args, _status, timeout) = cur.fetchone()
        if _status == 'LEASED' and timeout != 0 and timeout < int(time.time()):
          _status = 'TIMEDOUT'
        return _status
      else:
        cur.execute("UPDATE Arguments "
                    "SET Status=? "
                    "WHERE Id=?", (update, arg_id))
        return update

  def get(self, arg_id):
    with self.con:
      cur = self.con.cursor()
      cur.execute("SELECT (Args) FROM Arguments "
                  "WHERE Id=?", (arg_id,))
      (args,) = cur.fetchone()
      return args

  def put(self, arguments):
    with self.con:
      cur = self.con.cursor()
      cur.execute("INSERT INTO Arguments (Args, Status, Created) "
                  "VALUES (?,'PENDING', strftime('%s', 'now'))", (arguments,))

  def _pop_with_id(self, update='UNKNOWN', timeout=None):
    with self.con:
      cur = self.con.cursor()
      cur.execute("BEGIN EXCLUSIVE")
      cur.execute("SELECT Id, Args FROM Arguments WHERE "
                  "  Status='PENDING' OR ("
                  "    Status='LEASED' AND"
                  "    Timeout<strftime('%s', 'now') AND"
                  "    Timeout IS NOT 0"
                  "  )")
      try:
        row_id, args = cur.fetchone()
      except TypeError:
        raise Exception("No more arguments to pop")
      if timeout is None:
        cur.execute("UPDATE Arguments SET "
                    "  Status=? "
                    "WHERE Id=?", (update, row_id))
      else:
        cur.execute("UPDATE Arguments SET "
                    "  Status=?, "
                    "  Timeout=strftime('%s', 'now') + ? "
                    "WHERE Id=?", (update, timeout, row_id))
      return row_id, args

  def pop(self, update='UNKNOWN'):
    row_id, args = self._pop_with_id(update=update)
    return args
