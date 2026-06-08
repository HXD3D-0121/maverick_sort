import csv
import random
import os
from datetime import datetime, timedelta

output_dir = r'C:\Users\27081\Desktop\2025-2026学年\2025-2026学年春学期\Digital Innovation\Code for Course Assignment\demo_data_v2'
os.makedirs(output_dir, exist_ok=True)

random.seed(2024)

TEMP_ZONES = ['Ambient', 'Cool', 'Cold', 'Frozen', 'Deep Frozen']
CLIENT_TYPES = ['Public Hospital', 'Chain Pharmacy', 'Independent Pharmacy', 'Primary Healthcare']
PRIORITIES = ['Standard', 'Urgent', 'Critical']
STATUSES = ['Pending Dispatch', 'Picking in Progress', 'Completed', 'Exception']
TIME_WINDOWS = ['Night (0-6h)', 'Early (6-8h)', 'Morning Peak (8-12h)', 'Afternoon (12-16h)', 'Evening Peak (16-20h)', 'Late (20-24h)']
SEVERITIES = ['critical', 'warning', 'info']

# 1. orders.csv - 120 rows (different count)
with open(os.path.join(output_dir, 'orders.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['order_id','client_type','sku_count','temperature','deadline_hours','priority','volume','status','timestamp','time_window'])
    for i in range(1, 121):
        client = random.choice(CLIENT_TYPES)
        temp = random.choices(TEMP_ZONES, weights=[25,30,20,15,10])[0]
        deadline = round(random.uniform(1.5, 20.0), 1)
        priority = random.choices(PRIORITIES, weights=[50,35,15])[0]
        if deadline < 5: priority = 'Critical'
        elif deadline < 10: priority = 'Urgent'
        volume = random.randint(5, 150)
        status = random.choices(STATUSES, weights=[35,35,25,5])[0]
        hour = random.choices([2,6,9,13,17,21], weights=[8,12,40,20,15,5])[0]
        ts = f'{hour:02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}'
        tw = TIME_WINDOWS[hour//4 if hour < 20 else 5]
        w.writerow([f'ORD-2026{i:04d}', client, random.randint(1,10), temp, deadline, priority, volume, status, ts, tw])

# 2. inventory.csv - 25 rows
medicines = [
    ('INS-001','Insulin Glargine','Cold Chain Insulin','Cold'),
    ('INS-002','Insulin Aspart','Cold Chain Insulin','Cold'),
    ('INS-003','Insulin Lispro','Cold Chain Insulin','Cold'),
    ('VAC-001','Influenza Vaccine','Vaccine','Frozen'),
    ('VAC-002','HPV Vaccine','Vaccine','Frozen'),
    ('VAC-003','COVID-19 Vaccine','Vaccine','Frozen'),
    ('ANT-001','Amoxicillin Capsules','Antibiotic','Ambient'),
    ('ANT-002','Azithromycin Tablets','Antibiotic','Ambient'),
    ('ANT-003','Cefixime Capsules','Antibiotic','Ambient'),
    ('HBP-001','Amlodipine Tablets','Hypertension','Ambient'),
    ('HBP-002','Valsartan Capsules','Hypertension','Ambient'),
    ('HBP-003','Losartan Tablets','Hypertension','Ambient'),
    ('DM-001','Metformin Tablets','Diabetes','Ambient'),
    ('DM-002','Dapagliflozin Tablets','Diabetes','Ambient'),
    ('DM-003','Sitagliptin Tablets','Diabetes','Ambient'),
    ('COOL-001','Interferon Alfa','Biologic','Cool'),
    ('COOL-002','Erythropoietin','Biologic','Cool'),
    ('COOL-003','Monoclonal Antibody','Biologic','Cool'),
    ('DF-001','mRNA Vaccine','Vaccine','Deep Frozen'),
    ('DF-002','CAR-T Cell Therapy','Biologic','Deep Frozen'),
    ('COLD-003','Growth Hormone','Hormone','Cold'),
    ('AMB-003','Paracetamol Tablets','OTC','Ambient'),
    ('AMB-004','Ibuprofen Capsules','OTC','Ambient'),
    ('AMB-005','Aspirin Tablets','OTC','Ambient'),
    ('FRZ-003','Pneumococcal Vaccine','Vaccine','Frozen'),
]
with open(os.path.join(output_dir, 'inventory.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['sku','name','category','temperature_zone','stock_qty','expiry_date'])
    for sku, name, cat, temp in medicines:
        stock = random.randint(100, 5000)
        days = random.randint(5, 600)
        expiry = (datetime(2026, 6, 8) + timedelta(days=days)).strftime('%Y-%m-%d')
        w.writerow([sku, name, cat, temp, stock, expiry])

# 3. tasks.csv - 40 rows
skus = ['Insulin Glargine','Amoxicillin','Influenza Vaccine','Amlodipine','Metformin','Interferon Alfa','Paracetamol','Ibuprofen','Cefixime','Losartan']
zones = ['Zone A','Zone B','Zone C','Zone D','Zone E']
workers = [f'Worker-{i:02d}' for i in range(1, 13)]
with open(os.path.join(output_dir, 'tasks.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['task_id','source_zone','target_client','sku_checklist','priority','status','assigned_worker','est_duration_min'])
    for i in range(1, 41):
        checklist = ';'.join([f'{random.choice(skus)} x{random.randint(1,5)}' for _ in range(random.randint(1,3))])
        priority = random.choices(['Standard','Urgent','Critical'], weights=[45,40,15])[0]
        status = random.choices(['Pending','Active Picking','Completed','Exception'], weights=[25,45,25,5])[0]
        w.writerow([f'TSK-{i:05d}', random.choice(zones), random.choice(CLIENT_TYPES), checklist, priority, status, random.choice(workers), random.randint(5,60)])

# 4. workers.csv - 12 rows
shifts = ['Morning (6-14h)','Afternoon (14-22h)','Night (22-6h)']
emp_types = ['Full-Time','Temporary','Peak Season']
with open(os.path.join(output_dir, 'workers.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['worker_id','zone','shift','employment_type'])
    for i in range(1, 13):
        w.writerow([f'Worker-{i:02d}', random.choice(zones), random.choice(shifts), random.choices(emp_types, weights=[55,30,15])[0]])

# 5. sla_history.csv - 48 rows (different values)
with open(os.path.join(output_dir, 'sla_history.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['period','client_category','orders_fulfilled','orders_total','on_time_rate','next_day_rate','temp_compliance_rate','exception_rate'])
    for month in range(1, 13):
        period = f'2026-{month:02d}'
        base = random.randint(10000, 20000)
        for client in CLIENT_TYPES:
            total = random.randint(int(base*0.7), int(base*1.3))
            ot = round(random.uniform(88.0, 98.5), 1)
            nd = round(min(ot + random.uniform(0.3, 4.0), 99.9), 1)
            tc = round(random.uniform(95.0, 99.9), 1)
            exc = round(random.uniform(0.2, 4.0), 1)
            fulfilled = int(total * ot / 100)
            w.writerow([period, client, fulfilled, total, ot, nd, tc, exc])

# 6. alerts.csv - 20 rows
alert_msgs = {
    'Temperature Deviation': ['Cold chain threshold exceeded in Zone C', 'Frozen zone temperature rose above -18C', 'Cool zone fluctuation detected'],
    'Capacity Overload': ['Wave capacity exceeded by 20%', 'Picking queue backlog reached 120 tasks', 'Loading dock at full capacity'],
    'Deadline Risk': ['15 urgent orders risk missing deadline', 'Hospital delivery window closing in 30 min', 'Emergency stock request pending'],
    'Inefficient Batch': ['Wave contains only 2 orders', 'Batch covers 8 regions - high cost', 'Single-SKU wave detected'],
    'Too Many Zones': ['Wave mixes 6 temperature zones', 'Cross-zone path exceeds 1000 meters', 'GSP compliance risk in mixed batch'],
    'Low Stock': ['Critical stock below 50 units', 'Reorder point triggered for 3 SKUs', 'Safety stock depleted'],
}
with open(os.path.join(output_dir, 'alerts.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['alert_id','type','severity','message','timestamp','zone','acknowledged'])
    for i in range(1, 21):
        atype = random.choice(list(alert_msgs.keys()))
        sev = random.choices(SEVERITIES, weights=[25,45,30])[0]
        msg = random.choice(alert_msgs[atype])
        ts = f'{random.randint(0,23):02d}:{random.randint(0,59):02d}:00'
        w.writerow([f'ALT-{i:03d}', atype, sev, msg, ts, random.choice(zones), random.choice(['True','False'])])

print('Done! Files in:', output_dir)
for fn in sorted(os.listdir(output_dir)):
    fp = os.path.join(output_dir, fn)
    with open(fp) as fh:
        lines = len(fh.readlines()) - 1
    print(f'  {fn}: {lines} data rows')
