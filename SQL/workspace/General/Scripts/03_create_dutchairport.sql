--Creating dutchairport table with column name Airports,Periods, Aircraft movement cross country, Aircraft movement local flights, Commercial flights, All flights, Total passengers,Total cargo, Total mail

create table dutchairport(
		airport varchar(50),
		periods varchar(50),
		cross_country_flights varchar(50),
		local_flights varchar(50),
		commercial_flights varchar(50),
		scheduled_flights varchar(50),
		passenger varchar(50),
		cargo varchar(50),
		mail varchar(50)
)

--delete table if need
--drop table dutchairport;