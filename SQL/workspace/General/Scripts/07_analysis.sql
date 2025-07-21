--1. Retrieve first 10 rows
select * from dutchairport limit 10;

--2. Filtering - find all commerical flights during 2021-2024
select sum(commercial_flights)
from dutchairport d
where periods in ('2021','2022','2023','2024') and d.airport = 'Total Dutch airports';

--annual summary
select
	periods,
	sum(cross_country_flights) as total_cross_country_flights,
	sum(local_flights) as total_local_flights,
	sum(commercial_flights) as total_commercial_flights,
	sum(scheduled_flights) as total_scheduled_flights,
	sum(passenger) as total_passenger,
	sum(cargo) as total_cargo,
	sum(mail) as total_mail
from dutchairport
where airport = 'Total Dutch airports' and periods in ('2021','2022','2023','2024')
group by periods
order by periods


--calculating year-over-year growth rates of commercial flights and passenger
with year_totals as (
	select
		periods,
		sum(commercial_flights) as total_commercial_flights,
		sum(passenger) as total_passenger
	from dutchairport
	where airport = 'Total Dutch airports' and periods in ('2020','2021','2022','2023','2024')
	group by periods
	order by periods
)
select 
	periods,
	total_commercial_flights,
	round((total_commercial_flights-lag(total_commercial_flights) over (order by periods)) * 100 / nullif(lag(total_commercial_flights) over (order by periods),0),2) as commercial_flights_growth_pct,
	total_passenger,
	round((total_passenger-lag(total_passenger) over (order by periods)) * 100 / nullif(lag(total_passenger) over (order by periods),0),2) as passenger_growth_pct
from year_totals
order by periods;

--52% growth in commerical flights from 2021-2022,and 110% growth in passenger from 2021-2022

--Airport capacity analysis
with airport_stats as (
	select
		airport,
		sum(commercial_flights) as total_flights,
		sum(passenger) as total_passenger
	from dutchairport
	where airport != 'Total Dutch airports'
	group by airport
),
all_airport as (
	select
		SUM(total_passenger) AS overall_passenger,
    	SUM(total_flights) AS overall_flights
    from airport_stats
)
select
	a.airport,
	a.total_passenger,
	--calculate passenger percentage
	round(a.total_passenger * 100/ t.overall_passenger,2) as passenger_pct,
	--ranking by airport
	dense_rank() over (order by a.total_passenger desc) as passenger_rank,
	a.total_flights,
	--calculate flights percentage
	round(a.total_flights * 100/ t.overall_flights,2) as flights_pct,
	--ranking by airport
	dense_rank() over (order by a.total_flights desc) as flights_rank,
	--compare difference of passenger_rank and flights_rank
	(dense_rank() OVER (ORDER BY a.total_passenger DESC) - DENSE_RANK() OVER (ORDER BY a.total_flights DESC)) AS rank_difference
from airport_stats a
cross join all_airport t
order by passenger_rank;


--2024 monthly analysis
WITH monthly_2024 AS (
    -- get 2024 monthly data
    SELECT 
        airport,
        periods,
        passenger,
        commercial_flights,
        CASE 
            WHEN periods LIKE '%January' THEN 1
            WHEN periods LIKE '%February' THEN 2
            WHEN periods LIKE '%March' THEN 3
            WHEN periods LIKE '%April' THEN 4
            WHEN periods LIKE '%May' THEN 5
            WHEN periods LIKE '%June' THEN 6
            WHEN periods LIKE '%July' THEN 7
            WHEN periods LIKE '%August' THEN 8
            WHEN periods LIKE '%September' THEN 9
            WHEN periods LIKE '%October' THEN 10
            WHEN periods LIKE '%November' THEN 11
            WHEN periods LIKE '%December' THEN 12
        END AS month_num,
        CASE 
            WHEN periods LIKE '%January' THEN 'Jan'
            WHEN periods LIKE '%February' THEN 'Feb'
            WHEN periods LIKE '%March' THEN 'Mar'
            WHEN periods LIKE '%April' THEN 'Apr'
            WHEN periods LIKE '%May' THEN 'May'
            WHEN periods LIKE '%June' THEN 'Jun'
            WHEN periods LIKE '%July' THEN 'Jul'
            WHEN periods LIKE '%August' THEN 'Aug'
            WHEN periods LIKE '%September' THEN 'Sep'
            WHEN periods LIKE '%October' THEN 'Oct'
            WHEN periods LIKE '%November' THEN 'Nov'
            WHEN periods LIKE '%December' THEN 'Dec'
        END AS month_short
    FROM dutchairport
    WHERE airport = 'Total Dutch airports'
    AND periods LIKE '2024%'  and periods != '2024' and periods not like '%quarter'
),
stats_2024 AS (
    SELECT
        AVG(passenger) AS avg_passengers,
        MAX(passenger) AS max_passengers,
        MIN(passenger) AS min_passengers,
        SUM(passenger) AS total_passengers
    FROM monthly_2024
)
SELECT 
    m.periods,
    m.month_short,
    m.passenger,
    -- 与年度平均值的比较
    ROUND(s.avg_passengers, 0) AS year_avg,
    m.passenger - ROUND(s.avg_passengers, 0) AS diff_from_avg,
    ROUND((m.passenger - s.avg_passengers) * 100.0 / s.avg_passengers, 1) AS pct_diff,
    -- 当月排名
    RANK() OVER (ORDER BY m.passenger DESC) AS month_rank,
    -- 标记最佳月份
    CASE WHEN m.passenger = s.max_passengers THEN '★ Peak Month' ELSE '' END AS is_peak,
    -- 计算累计百分比
    ROUND(SUM(m.passenger) OVER (ORDER BY m.month_num) * 100.0 / s.total_passengers, 1) AS cumulative_pct
FROM monthly_2024 m
CROSS JOIN stats_2024 s
ORDER BY m.month_num;

/*2024 July and August has the most passenger
which are 14.1% and 16.1% higher then year average respectively*/ 


--covid_19 impacts on dutchairport

WITH 
pre_covid_annual AS (
    SELECT 
        '2019' AS year,
        SUM(passenger) AS annual_passengers,
        SUM(commercial_flights) AS annual_flights
    FROM dutchairport
    where airport = 'Total Dutch airports' and periods = '2019'
),
post_covid_annual AS (
    SELECT 
    	periods,
        SUM(passenger) AS annual_passengers,
        SUM(commercial_flights) AS annual_flights
    FROM dutchairport
    where airport = 'Total Dutch airports' and periods IN ('2020', '2021', '2022', '2023', '2024')  -- 年度数据
    GROUP BY periods
)
SELECT 
    p.periods,
    p.annual_passengers,
    a.annual_passengers AS pre_covid_passengers,
    ROUND((p.annual_passengers - a.annual_passengers) * 100.0 / a.annual_passengers, 1) AS passenger_change_pct,
    p.annual_flights,
    a.annual_flights AS pre_covid_flights,
    ROUND((p.annual_flights - a.annual_flights) * 100.0 / a.annual_flights, 1) AS flight_change_pct,
    -- 计算恢复指数(当前值占2019年的百分比)
    ROUND(p.annual_passengers * 100.0 / a.annual_passengers, 1) AS passenger_recovery_index,
    ROUND(p.annual_flights * 100.0 / a.annual_flights, 1) AS flight_recovery_index,
    -- 判断是否已恢复到疫情前水平
    CASE WHEN p.annual_passengers >= a.annual_passengers THEN 'Fully Recovered'
         WHEN p.annual_passengers >= a.annual_passengers * 0.9 THEN 'Nearly Recovered (90%+)'
         WHEN p.annual_passengers >= a.annual_passengers * 0.75 THEN 'Partially Recovered (75%+)'
         ELSE 'Significantly Below' END AS recovery_status
FROM post_covid_annual p
CROSS JOIN pre_covid_annual a
ORDER BY p.periods;

/*until 2024, dutch airports have not recover til the level before covid, but it has been recovering every year. 
By 2024, it has recovered 0verr 90% in both passenger and flights*/