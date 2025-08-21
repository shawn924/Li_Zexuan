--4. Which product categories generate the highest revenue?
select * from olist_order_items_dataset;
select * from olist_products_dataset;
select * from product_category_name_translation;

DROP TABLE IF EXISTS products_re;
CREATE TABLE products_re AS
SELECT ooi.order_id,
	   ooi.product_id,
	   oo.order_purchase_timestamp::date as order_purchase_timestamp,
	   pct.product_category_name_english as product_category,
	   ooi.price,
	   ooi.freight_value,
	   (ooi.price+ooi.freight_value) as total_revenue
FROM olist_order_items_dataset ooi JOIN olist_products_dataset op on ooi.product_id=op.product_id
LEFT JOIN product_category_name_translation pct on op.product_category_name=pct.product_category_name
INNER JOIN olist_orders_dataset oo ON ooi.order_id = oo.order_id;


--Analysis
--Aggregate Revenue by English Category
SELECT
    product_category,
    ROUND(SUM(total_revenue::numeric), 2) AS total_revenue,
	COUNT(*) AS order_count
FROM products_re
GROUP BY product_category
ORDER BY total_revenue DESC;
