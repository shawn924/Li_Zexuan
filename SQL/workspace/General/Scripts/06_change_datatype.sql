--changing datatype
alter table dutchairport 
alter column cross_country_flights type int USING (REPLACE(cross_country_flights, ',', '')::integer),
alter column local_flights type int USING (REPLACE(local_flights, ',', '')::integer),
alter column commercial_flights type int USING (REPLACE(commercial_flights, ',', '')::integer),
alter column scheduled_flights type int USING (REPLACE(scheduled_flights, ',', '')::integer),
alter column passenger type int USING (REPLACE(passenger, ',', '')::integer),
alter column cargo type int USING (REPLACE(cargo, ',', '')::integer),
alter column mail type int USING (REPLACE(mail, ',', '')::integer);