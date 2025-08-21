--5. Which sellers have the highest sales volume and best customer ratings?
DROP TABLE IF EXISTS order_items_cleaned;
CREATE TABLE order_items_cleaned AS
SELECT 
    order_id,
    order_item_id,
    product_id,
    seller_id,
    price,
    freight_value
FROM 
    olist_order_items_dataset
WHERE 
    price IS NOT NULL;


--analysis table
DROP TABLE IF EXISTS seller_sales_summary;
CREATE TABLE seller_sales_summary AS
SELECT 
    oi.seller_id,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(*) AS total_items_sold,
    ROUND(SUM(oi.price::numeric), 2) AS total_sales,
    ROUND(AVG(r.review_score), 2) AS avg_review_score
FROM 
    order_items_cleaned oi
LEFT JOIN 
    olist_orders_dataset o ON oi.order_id = o.order_id
LEFT JOIN 
    cleaned_reviews r ON o.order_id = r.order_id
GROUP BY 
    oi.seller_id;


--Top sellers by sales volume and rating
SELECT 
    seller_id,
    total_items_sold,
    total_sales,
    avg_review_score
FROM 
    seller_sales_summary
WHERE 
    total_items_sold > 100  -- filter for active sellers
    AND avg_review_score >= 4.0
ORDER BY 
    total_sales DESC
LIMIT 10;

--top in sales vs top in reviews
SELECT
    seller_id,
    total_sales,
    avg_review_score,
    RANK() OVER (ORDER BY total_sales DESC) AS sales_rank,
    RANK() OVER (ORDER BY avg_review_score DESC) AS rating_rank
FROM seller_sales_summary
WHERE total_items_sold > 100;



--Monthly Seller Performance
WITH orders_with_date AS (
    SELECT 
        oi.seller_id,
        o.order_purchase_timestamp::date AS order_date,
        DATE_TRUNC('month', o.order_purchase_timestamp::date) AS month,
        oi.price
    FROM olist_order_items_dataset oi
    JOIN olist_orders_dataset o ON oi.order_id = o.order_id
)
SELECT
    seller_id,
    month,
    COUNT(*) AS items_sold,
    SUM(price) AS monthly_sales
FROM orders_with_date
GROUP BY seller_id, month
ORDER BY seller_id, month;