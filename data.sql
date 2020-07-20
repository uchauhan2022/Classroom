create table users (
  id integer primary key autoincrement,
  name varchar(100) not null,
  email varchar(100) not null,
  password varchar(100) not null,
  activation_status integer default 0,
  token varchar(100) not null,
  role varchar(100) not null
);
-- for super admin role = 69
-- for teacher role = 420
--for student role = 1
