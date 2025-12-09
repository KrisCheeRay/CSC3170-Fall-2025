PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS admin (
  id            INTEGER PRIMARY KEY,
  username      TEXT    NOT NULL UNIQUE,
  password_hash TEXT    NOT NULL,
  display_name  TEXT,
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
  phone         TEXT UNIQUE,
  org           TEXT,
  email         TEXT UNIQUE,
  work_address  TEXT,
  role          TEXT    NOT NULL DEFAULT 'admin'
);
CREATE INDEX IF NOT EXISTS ix_admin_username ON admin(username);
CREATE INDEX IF NOT EXISTS ix_admin_phone    ON admin(phone);
CREATE INDEX IF NOT EXISTS ix_admin_email    ON admin(email);
CREATE INDEX IF NOT EXISTS ix_admin_role     ON admin(role);

CREATE TABLE IF NOT EXISTS visitor (
  id            INTEGER PRIMARY KEY,
  name          TEXT    NOT NULL,
  phone         TEXT    NOT NULL UNIQUE,
  org           TEXT,
  email         TEXT,
  password_hash TEXT    NOT NULL,
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_visitor_phone ON visitor(phone);

CREATE TABLE IF NOT EXISTS location (
  id        INTEGER PRIMARY KEY,
  campus    TEXT    NOT NULL,  
  name      TEXT    NOT NULL,
  is_active INTEGER DEFAULT 1
);
CREATE INDEX IF NOT EXISTS ix_location_campus ON location(campus);
CREATE INDEX IF NOT EXISTS ix_location_name   ON location(name);
CREATE UNIQUE INDEX IF NOT EXISTS uq_location_campus_name
  ON location(campus, name);

CREATE TABLE IF NOT EXISTS reservation (
  id           INTEGER PRIMARY KEY,
  visitor_id   INTEGER NOT NULL REFERENCES visitor(id),
  start_time   DATETIME NOT NULL,
  end_time     DATETIME NOT NULL,
  location     TEXT    NOT NULL,   
  location_id  INTEGER REFERENCES location(id),
  purpose      TEXT,
  status       TEXT    NOT NULL DEFAULT 'pending',
  is_driving   INTEGER NOT NULL DEFAULT 0,
  plate_number TEXT,              
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_reservation_visitor_id ON reservation(visitor_id);
CREATE INDEX IF NOT EXISTS ix_reservation_start_time ON reservation(start_time);
CREATE INDEX IF NOT EXISTS ix_reservation_end_time   ON reservation(end_time);
CREATE INDEX IF NOT EXISTS ix_reservation_location   ON reservation(location);
CREATE INDEX IF NOT EXISTS ix_reservation_location_id ON reservation(location_id);
CREATE INDEX IF NOT EXISTS ix_reservation_status     ON reservation(status);
CREATE INDEX IF NOT EXISTS ix_reservation_plate      ON reservation(plate_number);

CREATE INDEX IF NOT EXISTS ix_resv_loc_time
  ON reservation(location, start_time, end_time);

CREATE INDEX IF NOT EXISTS ix_resv_status_date
  ON reservation(status, start_time);

CREATE TABLE IF NOT EXISTS notification (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  visitor_id     INTEGER NOT NULL REFERENCES visitor(id) ON DELETE CASCADE,
  type           TEXT    NOT NULL,
  reservation_id INTEGER     REFERENCES reservation(id) ON DELETE SET NULL,
  title          TEXT    NOT NULL,
  body           TEXT,
  is_read        INTEGER NOT NULL DEFAULT 0,
  created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_notification_visitor_id ON notification(visitor_id);
CREATE INDEX IF NOT EXISTS ix_notification_is_read    ON notification(is_read);
CREATE INDEX IF NOT EXISTS ix_notification_created_at ON notification(created_at);
