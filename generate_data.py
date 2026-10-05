"""
Generate a synthetic quick-commerce event dataset (users + orders).

Everything here is SIMULATED. The causal structure is set from public reporting on
q-commerce retention (early-life churn, discount-driven acquisition, delivery
reliability, stockouts) so the analysis has something realistic to find.
It is not Blinkit data.

Built-in "experiment": each user is randomly assigned a sponsored-listing ad load
arm (slots per session). Random assignment means the ad-load vs churn comparison
can be read causally, unlike observational drivers.
"""
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)

START = pd.Timestamp("2026-01-05")       # Monday
N_WEEKS = 26                              # observation window
SIGNUP_WEEKS = 20                         # last 6 weeks only for follow-up
FEE_POLICY_WEEK = 14                      # small-basket delivery fee introduced
N_USERS = 12000

tiers = rng.choice(["Metro", "Tier-2", "Tier-3"], N_USERS, p=[0.55, 0.30, 0.15])
channels = rng.choice(["Organic", "Flash sale", "Referral", "Paid social"],
                      N_USERS, p=[0.40, 0.30, 0.15, 0.15])
ad_arms = rng.choice(["0-1", "2-3", "4-5", "6+"], N_USERS)  # randomized
arm_slots = {"0-1": 0.5, "2-3": 2.5, "4-5": 4.5, "6+": 6.5}
signup_week = rng.integers(0, SIGNUP_WEEKS, N_USERS)

tier_delay = {"Metro": 0.0, "Tier-2": 2.5, "Tier-3": 5.0}          # extra mins
tier_oos = {"Metro": 0.06, "Tier-2": 0.11, "Tier-3": 0.17}
chan_churn = {"Organic": 0.00, "Flash sale": 0.06, "Referral": -0.01, "Paid social": 0.02}
arm_churn = {"0-1": 0.0, "2-3": 0.003, "4-5": 0.015, "6+": 0.045}
chan_rate = {"Organic": 1.3, "Flash sale": 1.0, "Referral": 1.4, "Paid social": 1.1}

users, orders, tickets = [], [], []
oid = 0
for u in range(N_USERS):
    tier, ch, arm, sw = tiers[u], channels[u], ad_arms[u], int(signup_week[u])
    habit = rng.gamma(2.0, 0.5)           # personal order-frequency multiplier
    for w in range(sw, N_WEEKS):
        tenure = w - sw
        rate = chan_rate[ch] * habit * (1.25 if tenure == 0 else 1.0)
        n = rng.poisson(rate)
        late_n = oos_n = fee_n = 0
        for _ in range(n):
            day = rng.integers(0, 7)
            hour = rng.choice(np.arange(24), p=np.array(
                [1,1,1,1,1,2,3,5,7,7,6,6,6,5,5,5,6,8,9,9,8,6,4,2]) / 114)
            ts = START + pd.Timedelta(weeks=w, days=int(day), hours=int(hour),
                                      minutes=int(rng.integers(0, 60)))
            basket = float(np.round(rng.lognormal(5.9, 0.55), 0))   # ~₹365 median
            peak = hour in (18, 19, 20)
            mins = rng.lognormal(np.log(11 + tier_delay[tier] + (3 if peak else 0)), 0.32)
            late = mins > 20
            oos = rng.random() < tier_oos[tier] * (1.4 if peak else 1.0)
            fee = 0
            if w >= FEE_POLICY_WEEK and basket < 199:
                fee = 30
            elif basket < 99:
                fee = 25
            discount = 0
            if ch == "Flash sale" and tenure == 0:
                discount = round(min(basket * 0.5, 150))
            impr = int(rng.poisson(arm_slots[arm] * 3))             # ~3 screens/session
            clicks = int(rng.binomial(impr, 0.025)) if impr else 0
            ad_rev = round(impr * 0.18 + clicks * 4.0, 2)            # ₹ CPM-ish + CPC
            orders.append((oid, u, ts, w, basket, fee, discount, round(mins, 1),
                           int(late), int(oos), impr, clicks, ad_rev))
            # support tickets are a CONSEQUENCE of failures, not a cause
            p_ticket = 0.02 + 0.30 * late + 0.25 * oos
            if rng.random() < p_ticket:
                tickets.append((len(tickets), u, oid, ts,
                                "late" if late else ("stockout" if oos else "other")))
            late_n += late; oos_n += oos; fee_n += fee > 0
            oid += 1
        # weekly churn hazard
        h = 0.018 + chan_churn[ch] + arm_churn[arm]
        h += 0.16 if tenure == 0 else (0.04 if tenure < 4 else 0.0)
        if n:
            h += 0.18 * (late_n / n) + 0.14 * (oos_n / n) + 0.05 * (fee_n / n)
        else:
            h += 0.03
        h *= 0.85 if tier == "Metro" else 1.0
        if rng.random() < min(h, 0.95):
            break
    users.append((u, START + pd.Timedelta(weeks=sw), sw, tier, ch, arm))

pd.DataFrame(users, columns=["user_id", "signup_date", "signup_week", "city_tier",
                             "acq_channel", "ad_load_arm"]).to_csv(OUT / "users.csv", index=False)
pd.DataFrame(orders, columns=["order_id", "user_id", "order_ts", "week", "basket_value",
                              "delivery_fee", "discount", "delivery_mins", "is_late",
                              "had_stockout", "ad_impressions", "ad_clicks", "ad_revenue"]
             ).to_csv(OUT / "orders.csv.gz", index=False, compression="gzip")
pd.DataFrame(tickets, columns=["ticket_id", "user_id", "order_id", "created_ts", "reason"]
             ).to_csv(OUT / "support_tickets.csv", index=False)
print(f"users={len(users)} orders={len(orders)} tickets={len(tickets)}")
