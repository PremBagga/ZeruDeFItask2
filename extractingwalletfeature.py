import json
import pandas as pd
import os
from datetime import datetime

# Load JSON file of all wallet transactions
with open("all_compound_wallet_data.json") as f:
    all_data = json.load(f)

records = []

for wallet, data in all_data.items():
    if not data or "data" not in data or "items" not in data["data"]:
        continue

    for tx in data["data"]["items"]:
        timestamp = tx.get("block_signed_at")
        if not timestamp:
            continue

        # Try primary decoded method
        method = tx.get("decoded", {}).get("name", "").lower()

        # Fallback: Check in log_events
        if not method:
            for log in tx.get("log_events", []):
                # log_method = log.get("decoded", {}).get("name")
                log_method = (log.get("decoded") or {}).get("name")
                if log_method:
                    method = log_method.lower()
                    break

        # Normalize methods
        if method in ["borrow", "repayborrow", "repay", "mint", "redeem"]:
            records.append({
                "wallet": wallet,
                "method": method,
                "timestamp": timestamp,
                "value": tx.get("value", 0)
            })

# Convert to DataFrame
df = pd.DataFrame(records)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Flag method types
df["Borrow"] = df["method"] == "borrow"
df["Repay"] = df["method"].isin(["repay", "repayborrow"])
df["Deposit"] = df["method"] == "mint"
df["Redeem"] = df["method"] == "redeem"

# Aggregate per wallet
agg_df = df.groupby("wallet").agg(
    total_txn_count=("method", "count"),
    avg_txn_value_usd=("value", lambda x: pd.to_numeric(x, errors="coerce").mean()),
    active_days=("timestamp", lambda x: x.dt.date.nunique()),
    first_txn=("timestamp", "min"),
    last_txn=("timestamp", "max"),
    Borrow=("Borrow", "sum"),
    Repay=("Repay", "sum"),
    Deposit=("Deposit", "sum"),
    Redeem=("Redeem", "sum")
).reset_index()

# Add derived ratios and activity span
agg_df["borrow_to_deposit_ratio"] = agg_df["Borrow"] / agg_df["Deposit"].replace(0, 1)
agg_df["repay_to_borrow_ratio"] = agg_df["Repay"] / agg_df["Borrow"].replace(0, 1)
agg_df["activity_days_span"] = (agg_df["last_txn"] - agg_df["first_txn"]).dt.days + 1

# Save features to CSV
agg_df.to_csv("wallet_level_features.csv", index=False)
print("✅ Saved wallet-level features to wallet_level_features.csv")
