--3. How do delivery delays affect customer review scores?

--found some order have multiple reviews, so i keep only the latest or most relevant review per order_id.
--safer way than distinct. distinct might accidentally drop information if review records differ meaningfully.
DROP TABLE IF EXISTS cleaned_reviews;

CREATE TABLE cleaned_reviews AS
SELECT *
FROM (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_creation_date DESC) AS rn
  FROM olist_order_reviews_dataset
) sub
WHERE rn = 1;


DROP TABLE IF EXISTS delay_reviews;
CREATE TABLE delay_reviews AS
SELECT o.order_id,
	   o.customer_id,
	   o.order_purchase_timestamp,
	   o.customer_state,
	   o.delay_days,
	   o.delivered_status,
	   cr.review_score
FROM order_region o JOIN cleaned_reviews cr ON o.order_id=cr.order_id;

--Analysis
--Average delay by review score
SELECT review_score,
	   ROUND(AVG(delay_days::numeric),2) as avg_delay_days,
	   COUNT(*) as number_reviews
FROM delay_reviews
WHERE delivered_status='Delivered_Late'
GROUP BY review_score
ORDER BY review_score;

--Categorize delay buckets and check score impact
SELECT
    CASE
        WHEN delay_days <= -3 THEN 'early_3+'
        WHEN delay_days BETWEEN -2 AND 0 THEN 'on_time'
        WHEN delay_days BETWEEN 1 AND 5 THEN 'late_1_5'
        WHEN delay_days > 5 THEN 'late_6+'
        ELSE 'unknown'
    END AS delay_category,
    ROUND(AVG(review_score), 2) AS avg_review_score,
    COUNT(*) AS total_orders
FROM
    delay_reviews
GROUP BY
    delay_category
ORDER BY
    avg_review_score DESC;	 

