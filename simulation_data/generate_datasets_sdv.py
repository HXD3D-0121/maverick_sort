"""
Synthetic Dataset Generator for Enterprise AI Development Casebook
Uses SDV (Synthetic Data Vault) to generate statistically realistic data
that matches casebook business patterns and constraints.

Approach:
1. Generate small "seed" datasets with correct distributions using numpy/pandas
2. Fit SDV GaussianCopulaSynthesizer on each seed (learns correlations & distributions)
3. Sample target-scale datasets from trained models
4. Apply post-processing for referential integrity and business rules

Requirements: pip install sdv pandas numpy
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
import json

from sdv.metadata import Metadata
from sdv.single_table import GaussianCopulaSynthesizer
from sdv.constraints import (
    FixedCombinations,
    Inequality,
    ScalarInequality,
    create_custom_constraint_class,
)

random.seed(42)
np.random.seed(42)

OUTPUT_DIR = "generated_datasets_sdv"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# CONFIGURATION
# ============================================================================
N_SKUS = 300 #300
N_WAREHOUSES = 3 #3
N_CUSTOMERS = 200 #200
N_ORDERS = 5000 #5000
N_INVENTORY_BATCHES = 8000 #8000
N_SALES = 1800000 #18000
N_TERMINAL_INVENTORY = 6000 #6000

TODAY = datetime(2026, 5, 27)

# ============================================================================
# HELPER: Generate correlated seed data
# ============================================================================

def generate_products_seed(n=150):
    """Seed dataset for products with realistic distributions."""
    categories = np.random.choice(
        ["Western_Medicine", "TCM", "Medical_Devices", "Health_Supplements"],
        size=n, p=[0.30, 0.25, 0.35, 0.10]
    )
    
    data = []
    for i, cat in enumerate(categories):
        # Storage temperature depends on category
        if cat == "Medical_Devices":
            temp = np.random.choice(["ambient", "cool"], p=[0.9, 0.1])
        elif cat == "TCM":
            temp = np.random.choice(["ambient", "cool", "cold"], p=[0.4, 0.45, 0.15])
        elif cat == "Health_Supplements":
            temp = np.random.choice(["ambient", "cool", "cold"], p=[0.5, 0.3, 0.2])
        else:
            temp = np.random.choice(["ambient", "cool", "cold", "frozen"], p=[0.35, 0.30, 0.25, 0.10])
        
        # Shelf life depends on temperature
        if temp == "frozen":
            life = int(np.random.uniform(180, 730))
        elif temp == "cold":
            life = int(np.random.uniform(90, 365))
        elif temp == "cool":
            life = int(np.random.uniform(180, 730))
        else:
            life = int(np.random.uniform(365, 1095))
        
        # ABC class (Pareto)
        abc = np.random.choice(["A", "B", "C"], p=[0.10, 0.20, 0.70])
        
        # Price correlates with ABC class
        if abc == "A":
            price = round(np.random.lognormal(4.5, 0.8), 2)
        elif abc == "B":
            price = round(np.random.lognormal(3.5, 0.9), 2)
        else:
            price = round(np.random.lognormal(2.5, 1.0), 2)
        
        data.append({
            "sku_id": f"SKU_{i+1:05d}",
            "category": cat,
            "storage_temperature": temp,
            "shelf_life_days": life,
            "unit_price_rmb": price,
            "abc_class": abc,
            "near_expiry_managed": np.random.random() < 0.38,
            "batch_tracking_required": temp in ["cold", "frozen"] or np.random.random() < 0.4,
            "hazardous_or_controlled_flag": np.random.random() < 0.05,
            "unit_volume_liters": round(np.random.uniform(0.01, 2.0), 3),
            "unit_weight_kg": round(np.random.uniform(0.01, 1.5), 3),
            "manufacturer_id": f"MFG_{np.random.randint(1, 101):03d}",
        })
    return pd.DataFrame(data)


def generate_warehouses_seed(n=10):
    """Seed dataset for warehouses."""
    provinces = ["Jiangsu", "Zhejiang", "Guangdong", "Shandong", "Henan"]
    cities = {
        "Jiangsu": ["Nanjing", "Suzhou", "Wuxi"],
        "Zhejiang": ["Hangzhou", "Ningbo", "Wenzhou"],
        "Guangdong": ["Guangzhou", "Shenzhen", "Dongguan"],
        "Shandong": ["Jinan", "Qingdao", "Yantai"],
        "Henan": ["Zhengzhou", "Luoyang", "Kaifeng"],
    }
    data = []
    for i in range(n):
        prov = provinces[i % len(provinces)]
        city = cities[prov][i % len(cities[prov])]
        area = int(np.random.uniform(15000, 50000))
        ambient_bins = int(area * np.random.uniform(0.12, 0.20))
        cool_bins = int(area * np.random.uniform(0.04, 0.10))
        cold_bins = int(area * np.random.uniform(0.02, 0.06))
        frozen_bins = int(area * np.random.uniform(0.005, 0.02))
        controlled_bins = int(area * np.random.uniform(0.005, 0.015))
        
        data.append({
            "warehouse_id": f"WH_{i+1:03d}",
            "province": prov,
            "city": city,
            "warehouse_type": np.random.choice(["central", "regional"], p=[0.2, 0.8]),
            "total_area_sqm": area,
            "ambient_zone_bins": ambient_bins,
            "cool_zone_bins": cool_bins,
            "cold_zone_bins": cold_bins,
            "frozen_zone_bins": frozen_bins,
            "controlled_zone_bins": controlled_bins,
            "max_capacity_units": int(area * np.random.uniform(8, 12)),
            "active_pickers": int(np.random.uniform(40, 120)),
            "peak_picker_capacity": int(np.random.uniform(100, 300)),
            "next_day_delivery_rate_pct": round(np.random.uniform(88.0, 96.5), 1),
            "daily_order_capacity": int(np.random.uniform(8000, 15000)),
        })
    return pd.DataFrame(data)


def generate_customers_seed(n=100):
    """Seed dataset for customers."""
    types = np.random.choice(
        ["public_hospital", "chain_pharmacy", "independent_pharmacy", "primary_healthcare", "clinic"],
        size=n, p=[0.08, 0.12, 0.55, 0.20, 0.05]
    )
    provinces = ["Jiangsu", "Zhejiang", "Guangdong", "Shandong", "Henan", "Sichuan", "Hubei"]
    cities_map = {
        "Jiangsu": ["Nanjing", "Suzhou", "Wuxi"],
        "Zhejiang": ["Hangzhou", "Ningbo", "Wenzhou"],
        "Guangdong": ["Guangzhou", "Shenzhen", "Dongguan"],
        "Shandong": ["Jinan", "Qingdao", "Yantai"],
        "Henan": ["Zhengzhou", "Luoyang", "Kaifeng"],
        "Sichuan": ["Chengdu", "Mianyang", "Deyang"],
        "Hubei": ["Wuhan", "Yichang", "Xiangyang"],
    }
    data = []
    for i, ctype in enumerate(types):
        prov = np.random.choice(provinces)
        city = np.random.choice(cities_map[prov])
        
        if ctype == "public_hospital":
            patient_vol = int(np.random.uniform(5000, 50000))
            store_size = np.random.choice(["large", "medium"], p=[0.7, 0.3])
            order_freq = int(np.random.uniform(3, 8))
            service_level = np.random.choice([0.98, 0.99, 0.995])
            credit = "A"
        elif ctype == "chain_pharmacy":
            patient_vol = int(np.random.uniform(500, 3000))
            store_size = np.random.choice(["medium", "large", "small"], p=[0.5, 0.3, 0.2])
            order_freq = int(np.random.uniform(5, 12))
            service_level = np.random.choice([0.95, 0.97, 0.98])
            credit = np.random.choice(["A", "B"], p=[0.7, 0.3])
        elif ctype == "independent_pharmacy":
            patient_vol = int(np.random.uniform(100, 1500))
            store_size = np.random.choice(["small", "medium"], p=[0.7, 0.3])
            order_freq = int(np.random.uniform(10, 30))
            service_level = np.random.choice([0.90, 0.93, 0.95])
            credit = np.random.choice(["B", "C", "D"], p=[0.4, 0.4, 0.2])
        elif ctype == "primary_healthcare":
            patient_vol = int(np.random.uniform(200, 2000))
            store_size = np.random.choice(["small", "medium"], p=[0.7, 0.3])
            order_freq = int(np.random.uniform(7, 21))
            service_level = np.random.choice([0.92, 0.95, 0.97])
            credit = np.random.choice(["B", "C"], p=[0.5, 0.5])
        else:
            patient_vol = int(np.random.uniform(300, 2500))
            store_size = np.random.choice(["small", "medium"], p=[0.6, 0.4])
            order_freq = int(np.random.uniform(7, 14))
            service_level = np.random.choice([0.93, 0.95, 0.97])
            credit = np.random.choice(["A", "B"], p=[0.3, 0.7])
        
        data.append({
            "customer_id": f"CUST_{i+1:05d}",
            "customer_type": ctype,
            "province": prov,
            "city": city,
            "urban_rural_flag": np.random.choice(["urban", "rural"], p=[0.75, 0.25]),
            "store_size": store_size,
            "monthly_patient_volume": patient_vol,
            "average_order_frequency_days": order_freq,
            "service_level_target": round(service_level, 3),
            "credit_tier": credit,
            "b2b_registered": True,
            "active_status": np.random.choice(["active", "inactive"], p=[0.95, 0.05]),
        })
    return pd.DataFrame(data)


# ============================================================================
# SDV SYNTHESIS
# ============================================================================

def synthesize_products(seed_df, n_target):
    """Use SDV GaussianCopula to generate products preserving correlations."""
    metadata = Metadata.detect_from_dataframe(data=seed_df, table_name="products")
    # Override: treat string IDs as categorical so SDV samples from seed categories
    for col in ["near_expiry_managed", "batch_tracking_required", "hazardous_or_controlled_flag"]:
        metadata.update_column(table_name="products", column_name=col, sdtype="boolean")
    
    synthesizer = GaussianCopulaSynthesizer(metadata)
    synthesizer.fit(seed_df)
    
    df = synthesizer.sample(num_rows=n_target)
    
    # Post-processing: fix IDs, categories, enforce rules
    df["sku_id"] = [f"SKU_{i+1:05d}" for i in range(n_target)]
    df["category"] = df["category"].astype(str).str.replace(" ", "_")
    df["storage_temperature"] = df["storage_temperature"].astype(str)
    
    # Ensure near_expiry_managed ~38%
    current_pct = df["near_expiry_managed"].mean()
    if abs(current_pct - 0.38) > 0.05:
        n_to_flip = int(abs(0.38 * n_target - df["near_expiry_managed"].sum()))
        if current_pct < 0.38:
            idx = df[~df["near_expiry_managed"]].sample(n=min(n_to_flip, (~df["near_expiry_managed"]).sum())).index
            df.loc[idx, "near_expiry_managed"] = True
        else:
            idx = df[df["near_expiry_managed"]].sample(n=min(n_to_flip, df["near_expiry_managed"].sum())).index
            df.loc[idx, "near_expiry_managed"] = False
    
    # Ensure batch_tracking for cold/frozen
    cold_frozen = df["storage_temperature"].isin(["cold", "frozen"])
    df.loc[cold_frozen, "batch_tracking_required"] = True
    
    # Enforce shelf life rules
    for temp, (min_life, max_life) in {
        "frozen": (180, 730),
        "cold": (90, 365),
        "cool": (180, 730),
        "ambient": (365, 1095),
    }.items():
        mask = df["storage_temperature"] == temp
        df.loc[mask, "shelf_life_days"] = df.loc[mask, "shelf_life_days"].clip(min_life, max_life).astype(int)
    
    df["unit_price_rmb"] = df["unit_price_rmb"].clip(0.1, 50000).round(2)
    df["unit_volume_liters"] = df["unit_volume_liters"].clip(0.001, 10).round(3)
    df["unit_weight_kg"] = df["unit_weight_kg"].clip(0.001, 10).round(3)
    
    return df


def synthesize_warehouses(seed_df, n_target):
    """Generate warehouses using SDV."""
    metadata = Metadata.detect_from_dataframe(data=seed_df, table_name="warehouses")
    # Override: prevent PII anonymization of location fields
    for col in ["province", "city", "warehouse_type"]:
        metadata.update_column(table_name="warehouses", column_name=col, sdtype="categorical")
    
    synthesizer = GaussianCopulaSynthesizer(metadata)
    synthesizer.fit(seed_df)
    
    df = synthesizer.sample(num_rows=n_target)
    df["warehouse_id"] = [f"WH_{i+1:03d}" for i in range(n_target)]
    df["warehouse_type"] = df["warehouse_type"].astype(str)
    df["province"] = df["province"].astype(str)
    df["city"] = df["city"].astype(str)
    
    # Fix province-city pairs to be valid (vectorized)
    valid_cities = seed_df.groupby("province")["city"].apply(list).to_dict()
    df["_valid"] = df.apply(lambda r: r["city"] in valid_cities.get(r["province"], []), axis=1)
    invalid = ~df["_valid"]
    if invalid.any():
        sampled = seed_df.sample(n=invalid.sum(), replace=True).reset_index(drop=True)
        df.loc[invalid, "province"] = sampled["province"].values
        df.loc[invalid, "city"] = sampled["city"].values
    df = df.drop(columns=["_valid"])
    
    # Ensure capacity relationships
    for col in ["total_area_sqm", "ambient_zone_bins", "cool_zone_bins", 
                "cold_zone_bins", "frozen_zone_bins", "controlled_zone_bins",
                "max_capacity_units", "active_pickers", "peak_picker_capacity", "daily_order_capacity"]:
        df[col] = df[col].clip(1, None).astype(int)
    
    # peak > active
    mask = df["peak_picker_capacity"] < df["active_pickers"]
    df.loc[mask, "peak_picker_capacity"] = (df.loc[mask, "active_pickers"] * 2.5).astype(int)
    
    df["next_day_delivery_rate_pct"] = df["next_day_delivery_rate_pct"].clip(85, 99).round(1)
    
    return df


def synthesize_customers(seed_df, n_target):
    """Generate customers using SDV."""
    metadata = Metadata.detect_from_dataframe(data=seed_df, table_name="customers")
    # Override: prevent PII anonymization of location fields
    for col in ["province", "city", "customer_type", "urban_rural_flag", 
                "store_size", "credit_tier", "active_status"]:
        metadata.update_column(table_name="customers", column_name=col, sdtype="categorical")
    for col in ["b2b_registered"]:
        metadata.update_column(table_name="customers", column_name=col, sdtype="boolean")
    
    synthesizer = GaussianCopulaSynthesizer(metadata)
    synthesizer.fit(seed_df)
    
    df = synthesizer.sample(num_rows=n_target)
    df["customer_id"] = [f"CUST_{i+1:05d}" for i in range(n_target)]
    
    # Fix categoricals
    for col in ["customer_type", "province", "city", "urban_rural_flag", "store_size", "credit_tier", "active_status"]:
        df[col] = df[col].astype(str)
    
    # Fix province-city pairs to be valid (vectorized)
    valid_cities = seed_df.groupby("province")["city"].apply(list).to_dict()
    df["_valid"] = df.apply(lambda r: r["city"] in valid_cities.get(r["province"], []), axis=1)
    invalid = ~df["_valid"]
    if invalid.any():
        sampled = seed_df.sample(n=invalid.sum(), replace=True).reset_index(drop=True)
        df.loc[invalid, "province"] = sampled["province"].values
        df.loc[invalid, "city"] = sampled["city"].values
    df = df.drop(columns=["_valid"])
    
    df["monthly_patient_volume"] = df["monthly_patient_volume"].clip(10, 100000).astype(int)
    df["average_order_frequency_days"] = df["average_order_frequency_days"].clip(1, 90).astype(int)
    df["service_level_target"] = df["service_level_target"].clip(0.85, 0.999).round(3)
    df["b2b_registered"] = True
    
    return df


def generate_inventory_batches(products, warehouses, n_target):
    """Generate inventory batches with bin-temperature compatibility."""
    # Build bins per warehouse
    warehouse_bins = {}
    for _, wh in warehouses.iterrows():
        bins = []
        for zone, count in [
            ("ambient", wh["ambient_zone_bins"]),
            ("cool", wh["cool_zone_bins"]),
            ("cold", wh["cold_zone_bins"]),
            ("frozen", wh["frozen_zone_bins"]),
            ("controlled", wh["controlled_zone_bins"]),
        ]:
            count = min(int(count), 200)
            for b in range(count):
                bins.append((f"{wh['warehouse_id']}_{zone.upper()}_{b+1:03d}", zone))
        warehouse_bins[wh["warehouse_id"]] = bins
    
    sku_list = products["sku_id"].tolist()
    sku_temp = dict(zip(products["sku_id"], products["storage_temperature"]))
    sku_life = dict(zip(products["sku_id"], products["shelf_life_days"]))
    wh_list = warehouses["warehouse_id"].tolist()
    
    data = []
    for i in range(n_target):
        wh_id = np.random.choice(wh_list)
        sku_id = np.random.choice(sku_list)
        temp = sku_temp[sku_id]
        life = sku_life[sku_id]
        
        # Compatible bins
        bins = warehouse_bins[wh_id]
        compatible = [b for b, z in bins if z == temp]
        if not compatible:
            compatible = [b for b, z in bins]
        bin_id = np.random.choice(compatible)
        
        mfg_date = TODAY - timedelta(days=int(np.random.uniform(0, life * 0.9)))
        expiry = mfg_date + timedelta(days=int(life))
        received = mfg_date + timedelta(days=int(np.random.uniform(1, 14)))
        qty = int(np.random.lognormal(3, 1.2))
        reserved = int(qty * np.random.uniform(0, 0.3)) if np.random.random() < 0.3 else 0
        
        quality = "good"
        if expiry < TODAY:
            quality = np.random.choice(["expired", "expired", "quarantine"])
        elif (expiry - TODAY).days < 30:
            quality = np.random.choice(["good", "good", "near_expiry"])
        
        data.append({
            "inventory_id": f"INV_{i+1:07d}",
            "warehouse_id": wh_id,
            "bin_id": bin_id,
            "sku_id": sku_id,
            "batch_id": f"BATCH_{i+1:07d}",
            "manufacture_date": mfg_date.strftime("%Y-%m-%d"),
            "expiry_date": expiry.strftime("%Y-%m-%d"),
            "received_date": received.strftime("%Y-%m-%d"),
            "quantity_available": max(0, qty - reserved),
            "quantity_reserved": reserved,
            "quality_status": quality,
            "days_to_expiry": max(0, (expiry - TODAY).days),
        })
    return pd.DataFrame(data)


def generate_orders_and_lines(customers, products, n_orders_target):
    """Generate orders and order lines."""
    base_date = datetime(2026, 1, 10)
    # 7 days with spike on days 4-6
    daily = []
    for day in range(7):
        if day in [3, 4, 5]:
            daily.append(int(n_orders_target * 0.25))
        else:
            daily.append(int(n_orders_target * 0.083))
    while sum(daily) < n_orders_target:
        daily[3] += 1
    
    cust_list = customers["customer_id"].tolist()
    cust_type_map = dict(zip(customers["customer_id"], customers["customer_type"]))
    cust_prov = dict(zip(customers["customer_id"], customers["province"]))
    cust_city = dict(zip(customers["customer_id"], customers["city"]))
    sku_list = products["sku_id"].tolist()
    sku_temp = dict(zip(products["sku_id"], products["storage_temperature"]))
    sku_haz = dict(zip(products["sku_id"], products["hazardous_or_controlled_flag"]))
    
    orders = []
    order_lines = []
    line_id = 1
    order_id = 1
    
    for day, n_day in enumerate(daily):
        date = base_date + timedelta(days=day)
        for _ in range(n_day):
            cust = np.random.choice(cust_list)
            wh = f"WH_{np.random.randint(1, N_WAREHOUSES+1):03d}"
            order_time = date + timedelta(hours=np.random.randint(6, 22), minutes=np.random.randint(0, 60))
            delivery = date + timedelta(days=1) if np.random.random() < 0.88 else date + timedelta(days=2)
            
            ctype = cust_type_map[cust]
            if ctype == "public_hospital":
                priority = np.random.choice(["normal", "high", "high", "urgent"], p=[0.3, 0.4, 0.2, 0.1])
            else:
                priority = np.random.choice(["normal", "normal", "normal", "high", "urgent"], 
                                            p=[0.6, 0.15, 0.10, 0.10, 0.05])
            
            orders.append({
                "order_id": f"ORD_{order_id:07d}",
                "customer_id": cust,
                "warehouse_id": wh,
                "order_datetime": order_time.strftime("%Y-%m-%d %H:%M:%S"),
                "required_delivery_date": delivery.strftime("%Y-%m-%d"),
                "province": cust_prov[cust],
                "city": cust_city[cust],
                "priority_level": priority,
                "order_status": np.random.choice(["pending", "picking", "picked", "dispatched", "delivered"],
                                                 p=[0.1, 0.2, 0.3, 0.25, 0.15]),
            })
            
            n_skus = int(np.random.choice([1, 2, 3, 4, 5, 6, 10, 15], 
                                          p=[0.05, 0.10, 0.25, 0.25, 0.20, 0.08, 0.04, 0.03]))
            skus = np.random.choice(sku_list, size=min(n_skus, len(sku_list)), replace=False)
            for sku in skus:
                qty = int(np.random.lognormal(1.5, 0.8))
                if ctype == "public_hospital":
                    qty = int(qty * np.random.uniform(2, 5))
                special = sku_temp[sku] in ["cold", "frozen"] or sku_haz[sku]
                order_lines.append({
                    "order_line_id": f"OL_{line_id:09d}",
                    "order_id": f"ORD_{order_id:07d}",
                    "sku_id": sku,
                    "quantity_ordered": max(1, qty),
                    "special_handling_required": special,
                    "substitution_allowed": np.random.choice([True, False], p=[0.3, 0.7]),
                })
                line_id += 1
            order_id += 1
    
    return pd.DataFrame(orders), pd.DataFrame(order_lines)


def generate_historical_sales(products, customers, n_target):
    """Generate 18-month daily sales with seasonality, promotions, stockouts, policy shock."""
    start_date = datetime(2024, 6, 1)
    dates = [start_date + timedelta(days=i) for i in range(547)]
    
    # Demand profiles
    patterns = ["stable_chronic", "winter_flu", "spring_allergy", "random_long_tail",
                "policy_sensitive", "promotion_sensitive", "emergency_spike"]
    pattern_p = [0.25, 0.15, 0.10, 0.25, 0.10, 0.10, 0.05]
    
    sku_profiles = {}
    for _, sku in products.iterrows():
        pat = np.random.choice(patterns, p=pattern_p)
        base = np.random.uniform(0.5, 5.0)
        if sku["abc_class"] == "A":
            base *= 3
        elif sku["abc_class"] == "B":
            base *= 1.5
        sku_profiles[sku["sku_id"]] = {"pattern": pat, "baseline": base, "price": sku["unit_price_rmb"]}
    
    # Sample active customer-SKU pairs
    n_pairs = min(3000, len(customers) * len(products) // 5)
    pairs = []
    for _ in range(n_pairs):
        cust = customers.sample(1).iloc[0]
        sku = products.sample(1).iloc[0]
        pairs.append((cust["customer_id"], cust["customer_type"], cust["province"], 
                      sku["sku_id"], sku_profiles[sku["sku_id"]]))
    
    records = []
    for date in dates:
        month = date.month
        for cust_id, ctype, prov, sku_id, profile in pairs:
            mult = 1.0
            if profile["pattern"] == "winter_flu" and month in [11, 12, 1, 2]:
                mult = np.random.uniform(2.0, 4.0)
            elif profile["pattern"] == "spring_allergy" and month in [3, 4, 5]:
                mult = np.random.uniform(1.5, 3.0)
            elif profile["pattern"] == "emergency_spike" and np.random.random() < 0.01:
                mult = np.random.uniform(3.0, 8.0)
            
            if date.weekday() >= 5:
                mult *= 0.7
            
            promo = np.random.random() < 0.03
            if promo:
                mult *= np.random.uniform(1.3, 2.0)
            
            if profile["pattern"] == "policy_sensitive" and date > datetime(2025, 7, 1):
                mult *= np.random.uniform(0.4, 0.7)
            
            if profile["pattern"] == "random_long_tail" and np.random.random() < 0.6:
                continue
            
            demand = profile["baseline"] * mult
            if ctype == "public_hospital":
                demand *= np.random.uniform(3, 8)
            elif ctype == "independent_pharmacy":
                demand *= np.random.uniform(0.3, 1.0)
            
            units = int(np.random.poisson(max(0.1, demand)))
            if units <= 0:
                continue
            
            stockout = np.random.random() < 0.05
            if stockout:
                units = int(units * np.random.uniform(0.3, 0.8))
            
            price = profile["price"] * np.random.uniform(0.95, 1.05)
            discount = round(np.random.uniform(0, 0.15), 2) if promo else 0.0
            revenue = round(units * price * (1 - discount), 2)
            
            records.append({
                "date": date.strftime("%Y-%m-%d"),
                "sku_id": sku_id,
                "customer_id": cust_id,
                "customer_type": ctype,
                "region": prov,
                "channel": "B2B",
                "units_sold": units,
                "sales_revenue_rmb": revenue,
                "unit_price_rmb": round(price, 2),
                "discount_rate": discount,
                "stockout_flag": stockout,
                "promotion_flag": promo,
            })
    
    df = pd.DataFrame(records)
    if len(df) > n_target:
        df = df.sample(n=n_target, random_state=42)
    return df.sort_values(["date", "sku_id", "customer_id"]).reset_index(drop=True)


def generate_terminal_inventory(products, customers, historical_sales, n_target):
    """Generate terminal inventory snapshots."""
    sales_summary = historical_sales.groupby(["customer_id", "sku_id"]).agg({
        "units_sold": "sum",
        "date": "count"
    }).reset_index()
    sales_summary.columns = ["customer_id", "sku_id", "total_units_sold", "active_days"]
    sales_summary["ads_30d"] = sales_summary["total_units_sold"] / 18.0
    
    sku_abc = dict(zip(products["sku_id"], products["abc_class"]))
    
    records = []
    for _ in range(n_target):
        cust = customers.sample(1).iloc[0]
        sku = products.sample(1).iloc[0]
        
        match = sales_summary[(sales_summary["customer_id"] == cust["customer_id"]) & 
                              (sales_summary["sku_id"] == sku["sku_id"])]
        ads = match.iloc[0]["ads_30d"] if len(match) > 0 else np.random.uniform(0, 2)
        
        abc = sku_abc.get(sku["sku_id"], "C")
        if abc == "A":
            on_hand = int(np.random.lognormal(3, 0.8))
        elif abc == "B":
            on_hand = int(np.random.lognormal(2.5, 1.0))
        else:
            on_hand = int(np.random.lognormal(2, 1.2))
        
        reserved = int(on_hand * np.random.uniform(0, 0.2)) if np.random.random() < 0.2 else 0
        available = max(0, on_hand - reserved)
        
        dos = available / ads if ads > 0.5 else np.random.uniform(30, 300)
        reorder_point = int(ads * np.random.uniform(7, 14))
        safety_stock = int(ads * np.random.uniform(3, 10))
        if cust["customer_type"] in ["independent_pharmacy", "primary_healthcare"]:
            safety_stock = int(safety_stock * 1.5)
        
        near_expiry = int(on_hand * np.random.uniform(0, 0.1)) if np.random.random() < 0.15 else 0
        last_replenish = TODAY - timedelta(days=int(np.random.uniform(1, 60)))
        
        records.append({
            "customer_id": cust["customer_id"],
            "sku_id": sku["sku_id"],
            "inventory_date": TODAY.strftime("%Y-%m-%d"),
            "on_hand_units": on_hand,
            "reserved_units": reserved,
            "average_daily_sales_30d": round(ads, 2),
            "days_of_supply": round(dos, 1),
            "reorder_point": reorder_point,
            "safety_stock": safety_stock,
            "last_replenishment_date": last_replenish.strftime("%Y-%m-%d"),
            "near_expiry_units": near_expiry,
        })
    
    return pd.DataFrame(records)


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("SDV-Based Synthetic Dataset Generator")
    print("=" * 60)
    
    print("\n[1/8] Generating seed data for SDV models...")
    seed_products = generate_products_seed(n=150)
    seed_warehouses = generate_warehouses_seed(n=10)
    seed_customers = generate_customers_seed(n=100)
    print(f"  Seeds: products={len(seed_products)}, warehouses={len(seed_warehouses)}, customers={len(seed_customers)}")
    
    print("\n[2/8] Synthesizing products with SDV GaussianCopula...")
    products = synthesize_products(seed_products, N_SKUS)
    products.to_csv(f"{OUTPUT_DIR}/products.csv", index=False)
    print(f"  -> {len(products)} rows")
    
    print("\n[3/8] Synthesizing warehouses with SDV GaussianCopula...")
    warehouses = synthesize_warehouses(seed_warehouses, N_WAREHOUSES)
    warehouses.to_csv(f"{OUTPUT_DIR}/warehouses.csv", index=False)
    print(f"  -> {len(warehouses)} rows")
    
    print("\n[4/8] Synthesizing customers with SDV GaussianCopula...")
    customers = synthesize_customers(seed_customers, N_CUSTOMERS)
    customers.to_csv(f"{OUTPUT_DIR}/customers.csv", index=False)
    print(f"  -> {len(customers)} rows")
    
    print("\n[5/8] Generating inventory batches...")
    inventory = generate_inventory_batches(products, warehouses, N_INVENTORY_BATCHES)
    inventory.to_csv(f"{OUTPUT_DIR}/inventory_batches.csv", index=False)
    print(f"  -> {len(inventory)} rows")
    
    print("\n[6/8] Generating orders & order lines...")
    orders, order_lines = generate_orders_and_lines(customers, products, N_ORDERS)
    orders.to_csv(f"{OUTPUT_DIR}/orders.csv", index=False)
    order_lines.to_csv(f"{OUTPUT_DIR}/order_lines.csv", index=False)
    print(f"  -> {len(orders)} orders, {len(order_lines)} lines")
    
    print("\n[7/8] Generating historical sales...")
    sales = generate_historical_sales(products, customers, N_SALES)
    sales.to_csv(f"{OUTPUT_DIR}/historical_sales.csv", index=False)
    print(f"  -> {len(sales)} rows")
    
    print("\n[8/8] Generating terminal inventory...")
    terminal_inv = generate_terminal_inventory(products, customers, sales, N_TERMINAL_INVENTORY)
    terminal_inv.to_csv(f"{OUTPUT_DIR}/terminal_inventory.csv", index=False)
    print(f"  -> {len(terminal_inv)} rows")
    
    print("\n" + "=" * 60)
    print(f"All datasets saved to ./{OUTPUT_DIR}/")
    print("=" * 60)
    
    # Summary
    print("\nSummary of generated files:")
    for f in os.listdir(OUTPUT_DIR):
        path = os.path.join(OUTPUT_DIR, f)
        size_kb = os.path.getsize(path) / 1024
        df = pd.read_csv(path)
        print(f"  {f:30s} {len(df):>8,} rows  {size_kb:>8.1f} KB")
