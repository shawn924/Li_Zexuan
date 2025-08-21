--update '.' as 0
UPDATE dutchairport SET airport = REPLACE(airport, '.', '0') WHERE airport LIKE '%.%';
UPDATE dutchairport SET periods = REPLACE(periods, '.', '0') WHERE periods LIKE '%.%';
UPDATE dutchairport SET cross_country_flights = REPLACE(cross_country_flights, '.', '0') WHERE cross_country_flights LIKE '%.%';
UPDATE dutchairport SET local_flights = REPLACE(local_flights, '.', '0') WHERE local_flights LIKE '%.%';
UPDATE dutchairport SET commercial_flights = REPLACE(commercial_flights, '.', '0') WHERE commercial_flights LIKE '%.%';
UPDATE dutchairport SET scheduled_flights = REPLACE(scheduled_flights, '.', '0') WHERE scheduled_flights LIKE '%.%';
UPDATE dutchairport SET passenger = REPLACE(passenger, '.', '0') WHERE passenger LIKE '%.%';
UPDATE dutchairport SET cargo = REPLACE(cargo, '.', '0') WHERE cargo LIKE '%.%';
UPDATE dutchairport SET mail = REPLACE(mail, '.', '0') WHERE mail LIKE '%.%';
UPDATE dutchairport SET periods = REPLACE(periods, '*', '') WHERE periods LIKE '%*%';

--delete last row
delete from dutchairport
where airport = 'Source: CBS0';