-- Churn by first-3-order experience, among users who reached 3 orders
-- (so every user had the same number of chances to hit a late delivery or stockout).
SELECT 'late_in_first_3' AS driver,
       CASE WHEN first3_late >= 2 THEN '2+' ELSE CAST(first3_late AS TEXT) END AS bucket,
       COUNT(*) AS users,
       ROUND(100.0 * AVG(churned), 1) AS churn_pct
FROM user_features WHERE n_orders >= 3 GROUP BY 1, 2
UNION ALL
SELECT 'stockout_in_first_3',
       CASE WHEN first3_stockout >= 2 THEN '2+' ELSE CAST(first3_stockout AS TEXT) END,
       COUNT(*), ROUND(100.0 * AVG(churned), 1)
FROM user_features WHERE n_orders >= 3 GROUP BY 1, 2
UNION ALL
SELECT 'acq_channel', acq_channel, COUNT(*), ROUND(100.0 * AVG(churned), 1)
FROM user_features GROUP BY 1, 2
UNION ALL
SELECT 'city_tier', city_tier, COUNT(*), ROUND(100.0 * AVG(churned), 1)
FROM user_features GROUP BY 1, 2
ORDER BY 1, 2;
