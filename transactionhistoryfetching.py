import pandas as pd
import requests
import json
import time

API_KEY = "cqt_rQJw4wGmyJTf4PtYtMyQXR83w4xp"

INPUT_CSV = "Wallet id - Sheet1.csv"

# Load wallets
df = pd.read_csv(INPUT_CSV)
wallets = df.iloc[:, 0].dropna().unique().tolist()

all_data = {}

# Function to get transactions
def fetch(wallet):
    url = f"https://api.covalenthq.com/v1/1/address/{wallet}/transactions_v2/"
    try:
        response = requests.get(url, params={"key": API_KEY})
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error {response.status_code} for {wallet}")
            return None
    except Exception as e:
        print(f"⚠️ Exception for {wallet}: {e}")
        return None

# Loop over wallets
for wallet in wallets:
    print(f"🔄 Fetching {wallet}...")
    result = fetch(wallet)
    if result:
        all_data[wallet] = result
    time.sleep(1)  # to avoid rate limits

# Save full data to JSON
with open("all_compound_wallet_data.json", "w") as f:
    json.dump(all_data, f)

print("✅ Saved all wallet JSON responses to all_compound_wallet_data.json")

# import json

# try:
#     with open("all_compound_wallet_data.json", "r") as f:
#         data = json.load(f)
#     print("✅ JSON is valid. Wallets fetched:", len(data))
# except Exception as e:
#     print("❌ Invalid JSON:", e)

