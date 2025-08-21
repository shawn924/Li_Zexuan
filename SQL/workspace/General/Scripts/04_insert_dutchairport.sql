--insert data into dutchairport
insert into dutchairport 
select  * from aviation;

--check rows in the table
select count(*) from dutchairport d;