--Table: channels

CREATE TABLE channels (
  id           integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  name         nvarchar(32) NOT NULL DEFAULT "None",
  url          nvarchar(255) DEFAULT "",
  urlstream    nvarchar(255) DEFAULT "",
  broadcaster  nvarchar(8) DEFAULT "",
  bitrate      nvarchar(16) DEFAULT "",
  del          bit DEFAULT 0,
  group_id     integer,
  adult        bit DEFAULT 0,
  sheduleurl   nvarchar(255) DEFAULT "",
  addsdate     date,
  imgurl       nvarchar(255) DEFAULT "",
  hd           bit DEFAULT 0,
  count        integer DEFAULT 0,
  favourite    integer DEFAULT 0
);
----
--Table: settings

--DROP TABLE settings;

CREATE TABLE settings (
  id          integer PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
  lastupdate  datetime,
  dbver       integer NOT NULL DEFAULT 0
);
----
--Table: shedules

--DROP TABLE shedules;

CREATE TABLE shedules (
  id           integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  channel_id   integer NOT NULL,
  start        bigint NOT NULL,
  "end"        bigint NOT NULL,
  name         nvarchar(64) NOT NULL,
  fanart       nvarchar(255),
  description  text
);
----
--Table: groups

--DROP TABLE groups;

CREATE TABLE groups (
  id     integer PRIMARY KEY NOT NULL UNIQUE,
  name   varchar(16) NOT NULL,
  url    nvarchar(255),
  adult  bit DEFAULT 0
);
----
INSERT INTO settings (id, dbver) VALUES ("1", "6")