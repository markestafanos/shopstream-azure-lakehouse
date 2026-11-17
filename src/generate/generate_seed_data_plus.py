"""ShopStream seed data, extended for Mark's build.

Runs the DataVidhya course generator unchanged, so customers.csv, products.csv
and orders_2026_h1.csv match the course lessons exactly (1,000 / 197 / 13,717).
Then it adds, without touching the course's random sequence:

  customers.csv        + phone, street_address, postcode, date_of_birth
                         (the 4 PII columns masked with Unity Catalog)
  orders_2026_h2.csv   Jul-Dec 2026 order lines, a second file for COPY INTO
                         to pick up incrementally (same dirt: duplicates,
                         -1 quantities, mixed-case statuses)

Run: python3 generate_seed_data_plus.py   (no installs). Output goes to ./data
"""
import csv, os, random, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data")
os.makedirs(OUT, exist_ok=True)

spec = importlib.util.spec_from_file_location("course", os.path.join(HERE, "course_generate_seed_data.py"))
course = importlib.util.module_from_spec(spec)
spec.loader.exec_module(course)          # sets random.seed(42) like the course
course.OUT_DIR = OUT

customers = course.gen_customers()
products = course.gen_products()
orders_h1 = course.gen_orders(customers, products)

# ---- extra PII columns, own RNG so course data stays identical ----
pii = random.Random(7)
STREETS = ["George St", "Pitt St", "King St", "Oxford St", "Crown St", "Victoria Rd", "Parramatta Rd", "Military Rd"]
for c in customers:
    c["phone"] = f"04{pii.randint(10,99)} {pii.randint(100,999)} {pii.randint(100,999)}"
    c["street_address"] = f"{pii.randint(1,250)} {pii.choice(STREETS)}"
    c["postcode"] = f"{pii.randint(2000,2770)}"
    c["date_of_birth"] = f"{pii.randint(1960,2005)}-{pii.randint(1,12):02d}-{pii.randint(1,28):02d}"

# ---- second half of 2026, own RNG ----
h2 = random.Random(2026)
rows, line_id = [], int(orders_h1[-1]["order_line_id"][1:]) + 1
last_order = max(int(r["order_id"][1:]) for r in orders_h1)
for i in range(last_order + 1, last_order + 1 + 8000):
    cust = h2.choice(customers)
    ts = f"2026-{h2.randint(7,12):02d}-{h2.randint(1,28):02d} {h2.randint(0,23):02d}:{h2.randint(0,59):02d}:{h2.randint(0,59):02d}"
    status = h2.choice(course.ORDER_STATUSES)
    if h2.random() < 0.08: status = status.upper()
    for _ in range(h2.choices([1,2,3,4], weights=[55,27,12,6])[0]):
        p = h2.choice(products)
        row = {"order_line_id": f"L{line_id:07d}", "order_id": f"O{i:06d}", "customer_id": cust["customer_id"],
               "product_id": p["product_id"], "quantity": h2.choices([1,2,3,-1], weights=[70,20,8,2])[0],
               "unit_price": p["unit_price"], "order_ts": ts, "status": status,
               "coupon_code": h2.choice(course.COUPONS) or ""}
        rows.append(row); line_id += 1
        if h2.random() < 0.015: rows.append(dict(row))

def write(name, data):
    with open(os.path.join(OUT, name), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=data[0].keys()); w.writeheader(); w.writerows(data)
    print(f"wrote {len(data):>6} rows -> data/{name}")

write("customers.csv", customers)
write("products.csv", products)
write("orders_2026_h1.csv", orders_h1)
write("orders_2026_h2.csv", rows)
