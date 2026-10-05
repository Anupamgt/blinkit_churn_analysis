-- The original deck ranked "SupportCalls" as the #2 churn driver.
-- Raw view: ticket-raisers churn LESS (they order more, so they have more chances to raise one).
-- Controlled view: hold order count and first-order failures fixed and compare.
SELECT 'raw' AS view,
       CASE WHEN tickets = 0 THEN '0 tickets' ELSE '1+ tickets' END AS ticket_group,
       NULL AS failures_in_first_3,
       COUNT(*) AS users,
       ROUND(100.0 * AVG(churned), 1) AS churn_pct
FROM user_features GROUP BY 1, 2
UNION ALL
SELECT 'users with 3-6 orders',
       CASE WHEN tickets = 0 THEN '0 tickets' ELSE '1+ tickets' END,
       CASE WHEN first3_late + first3_stockout = 0 THEN '0' ELSE '1+' END,
       COUNT(*), ROUND(100.0 * AVG(churned), 1)
FROM user_features WHERE n_orders BETWEEN 3 AND 6 GROUP BY 1, 2, 3
ORDER BY 1, 3, 2;
