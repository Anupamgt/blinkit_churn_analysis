-- One row per activated user: the feature table every chart is built from.
-- Churn definition (q-commerce native): no order in the final 28 days of the window.
-- Window ends 2026-07-06; last signup cohort is 2026-05-18, so every user has >= 7 weeks of history.
--
-- Experience features use each user's FIRST 3 ORDERS only. Lifetime late-share is biased:
-- a one-order user can only score 0% or 100%, and heavy users rack up more incidents simply
-- because they order more. Fixing the window makes users comparable.
DROP TABLE IF EXISTS user_features;
CREATE TABLE user_features AS
WITH o AS (
    SELECT o.*,
           u.signup_week,
           o.week - u.signup_week AS tenure_week,
           ROW_NUMBER() OVER (PARTITION BY o.user_id ORDER BY o.order_ts) AS order_seq
    FROM orders o JOIN users u USING (user_id)
),
t AS (
    SELECT user_id, COUNT(*) AS tickets FROM support_tickets GROUP BY user_id
)
SELECT
    u.user_id,
    u.signup_week                                         AS cohort_week,
    u.city_tier,
    u.acq_channel,
    u.ad_load_arm,
    COUNT(o.order_id)                                     AS n_orders,
    ROUND(SUM(o.basket_value), 0)                         AS gmv,
    SUM(CASE WHEN o.order_seq <= 3 THEN o.is_late END)       AS first3_late,
    SUM(CASE WHEN o.order_seq <= 3 THEN o.had_stockout END)  AS first3_stockout,
    MAX(o.delivery_fee > 0 AND o.week >= 14)              AS hit_new_fee,
    COALESCE(t.tickets, 0)                                AS tickets,
    ROUND(SUM(o.ad_revenue), 2)                           AS ad_revenue,
    MAX(o.order_ts) < '2026-06-08'                        AS churned,   -- silent for final 28 days
    GROUP_CONCAT(DISTINCT o.tenure_week)                  AS active_weeks
FROM users u
JOIN o USING (user_id)       -- inner join: users who never ordered never activated; they are not "churned"
LEFT JOIN t USING (user_id)
GROUP BY u.user_id;
