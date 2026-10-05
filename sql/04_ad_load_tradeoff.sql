-- Sponsored-listing ad load (randomized arm) vs retention and monetization.
-- Because the arm was randomly assigned, differences here are causal, not correlational.
SELECT ad_load_arm,
       COUNT(*)                                         AS users,
       ROUND(100.0 * AVG(churned), 1)                   AS churn_pct,
       ROUND(AVG(n_orders), 2)                          AS orders_per_user,
       ROUND(SUM(ad_revenue) / SUM(n_orders), 2)        AS ad_rev_per_order,
       ROUND(AVG(ad_revenue), 1)                        AS ad_rev_per_user
FROM user_features
GROUP BY ad_load_arm
ORDER BY ad_load_arm;
