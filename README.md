# Q-Commerce Retention Lab

**Live dashboard:** `https://anupamgt.github.io/blinkit_churn_analysis/` *(after enabling GitHub Pages, see below)*

An interactive dashboard that rebuilds a published Blinkit customer-churn case study with
q-commerce-native metrics, and adds the question the original never asked: **what do
sponsored listings cost in retention?**

> All data is **synthetic**, generated with a stated causal structure so every method can be
> checked against ground truth. This project is not affiliated with Blinkit or Eternal Ltd.

## Why rebuild it

A case-competition deck on Blinkit churn reported a Random Forest at 99.5% accuracy with
`BillingDelay` (45% importance), `SupportCalls` and `AgreementDuration` as top drivers, and
recommended EMIs, grace periods and billing reminders. Those features come from a
subscription-churn dataset. Blinkit customers pay at checkout and sign no contracts, so the
model explained a business that doesn't exist, and near-perfect accuracy was a leakage signal.

This project starts from the right unit of data (orders, deliveries, stockouts, ad impressions)
and the right churn definition (no order in the final 28 days).

## What the dashboard shows

| Section | Question | Finding (synthetic data) |
|---|---|---|
| Cohort retention | Where do users drop off? | ~68% of signups order in week 0, ~47% in week 1. The week 0→1 drop is the largest. |
| First-3-order experience | What predicts churn? | 2+ late deliveries in the first 3 orders: churn 57.5% → 68.1%. Flash-sale signups churn 79.7% vs 58.0% for referrals. |
| Support calls | Are tickets a churn driver? | Raw data says ticket-raisers churn *less* (volume confound). Controlled for order count and failures, tickets barely matter. They are a symptom. |
| Sponsored listings | How much ad load is too much? | Randomized arms: 6+ slots earn 13x the ad revenue per order of 0–1 slots but lift churn 64.6% → 76.0%. At a ₹25 commerce margin, 2–3 slots maximise contribution per user; below ~₹10 margin, heavier ad load wins. |

Filters (city tier, acquisition channel) and the margin slider recompute everything in the browser.

## Method notes

- **Fixed exposure window.** Experience features use each user's first 3 orders. Lifetime
  "late share" is biased: one-order users can only score 0% or 100%, and heavy users accumulate
  incidents because they order more.
- **Observational vs causal.** Delivery and stockout effects are observational. Ad load was
  randomly assigned, so that comparison is causal.
- **Activation vs churn.** Users who signed up but never ordered are excluded from churn: they
  never activated, which is a different funnel problem.

## Repo layout

```
generate_data.py          simulate users, orders, support tickets (seeded, reproducible)
sql/01_user_features.sql  user-level feature table (window functions, first-3-order features)
sql/02_cohort_retention.sql
sql/03_churn_drivers.sql
sql/04_ad_load_tradeoff.sql
sql/05_support_calls_confounding.sql
build.py                  load into SQLite, run all SQL, bake results into the dashboard
dashboard_template.html   dashboard source
docs/index.html           built dashboard (served by GitHub Pages)
data/                     generated CSVs
```

## Run it

```bash
pip install -r requirements.txt
python generate_data.py   # writes data/*.csv
python build.py           # runs every query, prints results, writes docs/index.html
```

## Publish on GitHub Pages

Repo **Settings → Pages → Build and deployment → Deploy from a branch → `main` / `/docs`**.
