import pandas as pd
from joblib import load

# === Step 1: Load all wallet addresses ===
wallet_df = pd.read_csv("Wallet id - Sheet1.csv", header=None, names=["wallet_id"])
wallet_df["wallet_id"] = wallet_df["wallet_id"].str.lower().str.strip()

# === Step 2: Load extracted features ===
features_df = pd.read_csv("wallet_level_features.csv")
features_df["wallet_id"] = features_df["wallet"].str.lower().str.strip()

# === Step 3: Patch missing model columns ===
# Rename 'Redeem' → 'RedeemUnderlying'
features_df["RedeemUnderlying"] = features_df["Redeem"]
features_df["LiquidationCall"] = 0  # Not extracted, fill as 0

# === Step 4: Load trained model ===
model = load("xgboost_credit_model.pkl")
print("✅ Model loaded.")

# === Step 5: Select columns for model ===
feature_cols = [
    'total_txn_count', 'avg_txn_value_usd', 'active_days',
    'Borrow', 'Deposit', 'LiquidationCall', 'RedeemUnderlying', 'Repay',
    'borrow_to_deposit_ratio', 'repay_to_borrow_ratio', 'activity_days_span'
]

# Ensure all required columns exist
missing_cols = set(feature_cols) - set(features_df.columns)
if missing_cols:
    raise Exception(f"❌ Missing required feature columns: {missing_cols}")

# === Step 6: Predict risk scores ===
X = features_df[feature_cols]
features_df["score"] = model.predict(X, validate_features=False).round().astype(int)


# ✅ Clamp scores to range [0, 1000]
features_df["score"] = features_df["score"].clip(lower=0, upper=1000)

# === Step 7: Merge with full wallet list ===
result_df = wallet_df.merge(features_df[["wallet_id", "score"]], on="wallet_id", how="left")

# Fill missing scores (inactive wallets) with 0
result_df["score"] = result_df["score"].fillna(0).astype(int)


# === Step 8: Save Final Output ===
result_df.to_csv("wallet_credit_scores.csv", index=False)
print("✅ Saved to wallet_credit_scores.csv with", len(result_df), "wallets.")

