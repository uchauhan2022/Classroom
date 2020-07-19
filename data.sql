create table users (
  id integer primary key autoincrement,
  first_name varchar(100) not null,
  last_name varchar(100),
  username varchar(100) not null,
  email varchar(100) not null,
  password varchar(100) not null,
  activation_status integer default 0,
  token varchar(100) not null,
  role integer default 1
);
-- for super admin role = 69
-- for teacher role = 420
--for student role = 1
