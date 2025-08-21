--2. Which regions (states/cities) have the longest delivery times?
DROP TABLE IF EXISTS order_region;
CREATE TABLE order_region AS
SELECT 
	oda.order_id,
    oda.customer_id,
	oda.order_purchase_timestamp,
	oc.customer_state,
	oc.customer_city,
	DATE_PART('day', oda.delivered_date - oda.order_purchase_timestamp) AS actual_delivery_days,
	DATE_PART('day', oda.estimated_delivered_date - oda.order_purchase_timestamp) AS estimated_delivery_days,
	DATE_PART('day', oda.delivered_date - oda.estimated_delivered_date) AS delay_days,
	oda.delivered_status,
	oda.shipped_status
FROM 
    orders_delivery_analysis oda
JOIN 
    olist_customers_dataset oc ON oda.customer_id = oc.customer_id;

--Check which state having most delay days
SELECT customer_state,
	   count(*) as total_orders,
	   ROUND(AVG(delay_days::numeric),2) as average_delay_days,
	   ROUND(100 * SUM(CASE WHEN delay_days > 0 THEN 1 ELSE 0 END)::numeric / COUNT(*),2) AS late_pct
FROM order_region
WHERE delivered_status = 'Delivered_Late'
GROUP BY customer_state
HAVING count(*)>10
order by average_delay_days desc;


