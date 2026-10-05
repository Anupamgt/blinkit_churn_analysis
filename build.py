"""
Load CSVs into SQLite, run every query in sql/, print results, and bake the
user feature table into docs/index.html (single self-contained page for GitHub Pages).
"""
import json, sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
DB = ROOT / "data" / "qcommerce.db"

if DB.exists():
    DB.unlink()
con = sqlite3.connect(DB)
pd.read_csv(ROOT / "data/users.csv").to_sql("users", con, index=False)
pd.read_csv(ROOT / "data/orders.csv.gz").to_sql("orders", con, index=False)
pd.read_csv(ROOT / "data/support_tickets.csv").to_sql("support_tickets", con, index=False)

con.executescript((ROOT / "sql/01_user_features.sql").read_text())
for f in sorted((ROOT / "sql").glob("0[2-9]_*.sql")):
    df = pd.read_sql(f.read_text(), con)
    print(f"\n=== {f.name} ===")
    print(df.head(40).to_string(index=False))

uf = pd.read_sql("SELECT * FROM user_features", con)
print("\nactivated users:", len(uf), " churn:", round(uf.churned.mean() * 100, 1), "%")

# compact column arrays to keep the page small
tier_codes = ["Metro", "Tier-2", "Tier-3"]
chan_codes = ["Organic", "Flash sale", "Referral", "Paid social"]
arm_codes = ["0-1", "2-3", "4-5", "6+"]
payload = {
    "tiers": tier_codes, "channels": chan_codes, "arms": arm_codes,
    "cw": uf.cohort_week.tolist(),
    "t": uf.city_tier.map(tier_codes.index).tolist(),
    "c": uf.acq_channel.map(chan_codes.index).tolist(),
    "a": uf.ad_load_arm.map(arm_codes.index).tolist(),
    "n": uf.n_orders.tolist(),
    "g": uf.gmv.astype(int).tolist(),
    "l": uf.first3_late.fillna(0).astype(int).tolist(),
    "s": uf.first3_stockout.fillna(0).astype(int).tolist(),
    "k": uf.tickets.tolist(),
    "r": uf.ad_revenue.round(1).tolist(),
    "x": uf.churned.tolist(),
    "w": [sum(1 << int(v) for v in str(s).split(",") if int(v) < 31) for s in uf.active_weeks],
    "signups": pd.read_sql("SELECT city_tier, acq_channel, signup_week FROM users", con)
                 .assign(t=lambda d: d.city_tier.map(tier_codes.index),
                         c=lambda d: d.acq_channel.map(chan_codes.index))
                 [["t", "c", "signup_week"]].values.tolist(),
}
template = (ROOT / "dashboard_template.html").read_text()
html = template.replace("/*__DATA__*/null", json.dumps(payload, separators=(",", ":")))
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs/index.html").write_text(html)
print("wrote docs/index.html", round(len(html) / 1024), "KB")
