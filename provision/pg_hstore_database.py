CREATE EXTENSION hstore;
CREATE TABLE stats(data hstore);
insert into stats (data) values ('hello => "world"');
