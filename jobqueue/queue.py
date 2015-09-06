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
                  "Jobs(Id INTEGER PRIMARY KEY AUTOINCREMENT, "
                        "Details TEXT NOT NULL, "
                        "Created INTEGER NOT NULL, "
                        "Status TEXT DEFAULT 'PENDING', "
                        "Timeout INTEGER DEFAULT 0)")

  def lease(self, timeout=3600):
    job_id, job = self._pop_with_id(update='LEASED', timeout=timeout)
    return job_id

  def list(self, statuses=None):
    with self.con:
      cur = self.con.cursor()
      cur.execute("SELECT Details, Status, Timeout "
                  "FROM Jobs")
      rows = cur.fetchall()
    def _update_status(status):
      (job, status, timeout) = status
      if status == 'LEASED' and timeout != 0 and timeout < int(time.time()):
        status = 'TIMEDOUT'
      return (job, status, timeout)
    rows = map(_update_status, rows)
    if statuses is None:
      return rows
    else:
      return [(job, status, timeout) for job, status, timeout in rows
              if status in statuses]

  def status(self, job_id, update=None):
    with self.con:
      cur = self.con.cursor()
      if update is None:
        cur.execute("SELECT Details, Status, Timeout "
                    "FROM Jobs "
                    "WHERE Id=?", (job_id,))
        try:
          (job, _status, timeout) = cur.fetchone()
        except TypeError:
          raise ValueError("Could not find jobs with id '%s'" % job_id)
        if _status == 'LEASED' and timeout != 0 and timeout < int(time.time()):
          _status = 'TIMEDOUT'
        return _status
      else:
        cur.execute("UPDATE Jobs "
                    "SET Status=? "
                    "WHERE Id=?", (update, job_id))
        return update

  def get(self, job_id):
    with self.con:
      cur = self.con.cursor()
      cur.execute("SELECT Details FROM Jobs "
                  "WHERE Id=?", (job_id,))
      try:
        (job,) = cur.fetchone()
      except TypeError:
        raise ValueError("Could not find jobs with id '%s'" % job_id)
      return job

  def put(self, jobs):
    with self.con:
      cur = self.con.cursor()
      cur.execute("INSERT INTO Jobs (Details, Status, Created) "
                  "VALUES (?,'PENDING', strftime('%s', 'now'))", (jobs,))

  def _pop_with_id(self, update='UNKNOWN', timeout=None):
    with self.con:
      cur = self.con.cursor()
      cur.execute("BEGIN EXCLUSIVE")
      cur.execute("SELECT Id, Details FROM Jobs WHERE "
                  "  Status='PENDING' OR ("
                  "    Status='LEASED' AND"
                  "    Timeout<strftime('%s', 'now') AND"
                  "    Timeout IS NOT 0"
                  "  )")
      try:
        row_id, job = cur.fetchone()
      except TypeError:
        raise Exception("No more jobs to pop")
      if timeout is None:
        cur.execute("UPDATE Jobs SET "
                    "  Status=? "
                    "WHERE Id=?", (update, row_id))
      else:
        cur.execute("UPDATE Jobs SET "
                    "  Status=?, "
                    "  Timeout=strftime('%s', 'now') + ? "
                    "WHERE Id=?", (update, timeout, row_id))
      return row_id, job

  def pop(self, update='UNKNOWN'):
    row_id, job = self._pop_with_id(update=update)
    return job
