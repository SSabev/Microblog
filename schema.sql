drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title string not null,
  text string not null
);

drop table if exists comments;
create table comments (
  comment_id integer primary key autoincrement,
  from_email string not null,
  from_name string not null,
  comment_text string not null,
  p_id int,
  foreign key (p_id) references entries(id)
);
