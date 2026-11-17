"""Writes data/customers_update_2026_12.csv: 20 customers who moved house.
Used to test SCD Type 2 history in silver.customers. Run after generate_seed_data_plus.py."""
import csv, os, random
HERE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(HERE, "data", "customers.csv")
rows = list(csv.DictReader(open(src)))
rng = random.Random(1212)
streets = ["Bondi Rd", "Macquarie St", "Elizabeth St", "Liverpool St", "Pacific Hwy"]
moved = rng.sample(rows, 20)
for r in moved:
    r["street_address"] = f"{rng.randint(1, 300)} {rng.choice(streets)}"
    r["postcode"] = str(rng.randint(2000, 2770))
out = os.path.join(HERE, "data", "customers_update_2026_12.csv")
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(moved)
print(f"wrote {len(moved)} rows -> data/customers_update_2026_12.csv")
