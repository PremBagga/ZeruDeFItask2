# ZeruDeFItask2

# 📘 Explanation — Risk Scoring for DeFi Wallets (Assignment 2)

## 🎯 Objective

Develop a risk scoring model that assigns each wallet address a **score from 0 to 1000**, based solely on their historical activity on the Compound V2/V3 protocols.

---

## 📥 Data Collection Method

* **Source:** Covalent Unified Blockchain API
* **Target Protocol:** Compound V2 / V3
* **Method:**

  * Queried transaction histories using Covalent’s `/v1/{chain_id}/address/{address}/transactions_v3/` endpoint.
  * Parsed and filtered transactions with method names: `borrow`, `repay`, `mint`, `redeem` (and variants).
  * Used `log_events` as fallback for methods that were not decoded directly.
  * Stored and aggregated JSON data for **103 wallets**.

---

## 🧱 Feature Selection Rationale

From raw transactions, we engineered wallet-level features that are indicative of risk in decentralized lending:

| Feature                   | Description                                               |
| ------------------------- | --------------------------------------------------------- |
| `total_txn_count`         | Number of transactions involving Compound actions         |
| `avg_txn_value_usd`       | Mean value of wallet’s interactions                       |
| `active_days`             | Unique days with activity                                 |
| `Borrow`                  | Count of borrow transactions                              |
| `Repay`                   | Count of repay transactions                               |
| `Deposit`                 | Count of mint (supply) transactions                       |
| `RedeemUnderlying`        | Count of withdrawals                                      |
| `LiquidationCall`         | Count of liquidations (filled with 0 due to lack of logs) |
| `borrow_to_deposit_ratio` | High value = over-leveraged behavior                      |
| `repay_to_borrow_ratio`   | High value = responsible borrowing                        |
| `activity_days_span`      | Duration between first and last interaction               |

These features reflect both **engagement** and **risk-taking behavior**.

---

## 📊 Scoring Method

### Model Used:

* **Type:** XGBoost Regressor
* **Input:** Engineered features listed above
* **Output:** Continuous score (0 to 1000)

### Preprocessing:

* No normalization needed (XGBoost handles raw numeric features)
* Missing values filled with defaults (e.g., 0 for liquidation)
* Predicted values **clipped to \[0, 1000]** to satisfy constraints

### Training:

* Model trained on Aave V2 wallet data with pseudo-labels
* Applied to new Compound wallet dataset without retraining

---

## ✅ Justification of Risk Indicators

| Risk Indicator                 | Explanation                                         |
| ------------------------------ | --------------------------------------------------- |
| Low `repay_to_borrow_ratio`    | Indicates poor repayment discipline                 |
| High `borrow_to_deposit_ratio` | Suggests risk of over-leverage and default          |
| Presence of `LiquidationCall`  | Sign of failed risk management (not repaid in time) |
| High `Deposit`, No Borrow      | Lender-only wallet, considered safe                 |
| Long `activity_days_span`      | Indicates stable historical engagement              |
| Low `total_txn_count`          | Often represents bot/sybil or dormant wallet        |

---

## 📦 Final Deliverables

* ✅ **wallet\_credit\_scores.csv** (with 103 entries)
* ✅ Columns:

| wallet\_id                                 | score |
| ------------------------------------------ | ----- |
| 0xfaa0768bde629806739c3a4620656c5d26f44ef2 | 732   |

* ✅ Reusable and scalable Python scripts for:

  * Transaction fetching
  * Feature extraction
  * Risk scoring

---

**Date:** July 25, 2025

**Author:** Prem Venkatesh Bagga
