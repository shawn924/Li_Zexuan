-- 1. What % of orders are delivered late?
DROP TABLE IF EXISTS orders_delivery_analysis;

CREATE TABLE orders_delivery_analysis AS
SELECT 
    distinct oo.order_id,
	oo.order_status,
	oo.order_purchase_timestamp::date as order_purchase_timestamp,
	to_timestamp(ooi.shipping_limit_date,'YYYY-MM-DD HH24:MI:SS') as limit_date_fromseller,
	to_timestamp(oo.order_delivered_carrier_date,'YYYY-MM-DD HH24:MI:SS') as date_tologistic,
  to_timestamp(oo.order_delivered_customer_date,'YYYY-MM-DD HH24:MI:SS') as delivered_date,
  to_timestamp(oo.order_estimated_delivery_date,'YYYY-MM-DD HH24:MI:SS') as estimated_delivered_date,
	CASE WHEN oo.order_delivered_customer_date <= oo.order_estimated_delivery_date THEN 'Delivered_On_Time'
	ELSE 'Delivered_Late'
	END AS Delivered_Status,
	CASE WHEN oo.order_delivered_carrier_date <= ooi.shipping_limit_date THEN 'Tologistic_On_Time'
	ELSE 'Tologistic_Late'
	END AS Shipped_Status
FROM olist_orders_dataset oo Join olist_order_items_dataset ooi on oo.order_id = ooi.order_id
WHERE oo.order_status = 'delivered' and 
	  oo.order_delivered_customer_date IS NOT NULL AND 
	  oo.order_delivered_carrier_date IS NOT NULL AND
	  oo.order_purchase_timestamp IS NOT NULL
ORDER BY delivered_date;

SELECT * from orders_delivery_analysis;

--Check percentage of late orders and late sending
SELECT COUNT(*) as total_delivered_orders,
	   SUM(CASE WHEN delivered_status = 'Delivered_Late' THEN 1 ELSE 0 END) as late_orders,
       SUM(CASE WHEN shipped_Status = 'Tologistic_Late' THEN 1 ELSE 0 END) as late_sending,
	   ROUND(SUM(CASE WHEN delivered_status = 'Delivered_Late' THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 2) AS late_orders_percentage,
	   ROUND(SUM(CASE WHEN shipped_Status = 'Tologistic_Late' THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 2) AS late_sending_percentage
FROM orders_delivery_analysis;

--Check percentage of late orders and late sending by Months
SELECT DATE_TRUNC('month', order_purchase_timestamp) AS months,
	   COUNT(*) as total_delivered_orders,
	   SUM(CASE WHEN delivered_status = 'Delivered_Late' THEN 1 ELSE 0 END) as late_orders,
       SUM(CASE WHEN shipped_Status = 'Tologistic_Late' THEN 1 ELSE 0 END) as late_sending,
	   ROUND(SUM(CASE WHEN delivered_status = 'Delivered_Late' THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 2) AS late_orders_percentage,
	   ROUND(SUM(CASE WHEN shipped_Status = 'Tologistic_Late' THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 2) AS late_sending_percentage
FROM orders_delivery_analysis
GROUP BY months
ORDER BY months;