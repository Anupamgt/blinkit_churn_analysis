-- Weekly cohort retention: share of each signup cohort that ordered in tenure week N.
WITH cohort_size AS (
    SELECT signup_week, COUNT(*) AS users FROM users GROUP BY signup_week
),
activity AS (
    SELECT DISTINCT o.user_id, u.signup_week, o.week - u.signup_week AS tenure_week
    FROM orders o JOIN users u USING (user_id)
)
SELECT a.signup_week,
       a.tenure_week,
       COUNT(*)                                     AS active_users,
       ROUND(100.0 * COUNT(*) / c.users, 1)         AS retention_pct
FROM activity a JOIN cohort_size c USING (signup_week)
WHERE a.tenure_week <= 8
GROUP BY a.signup_week, a.tenure_week
ORDER BY a.signup_week, a.tenure_week;
