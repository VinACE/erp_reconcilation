#!/usr/bin/env python3
import pandas as pd
import pdfplumber
import json
import sys
from collections import Counter

ERP_FILE = "erp_data (2).xlsx"
BANK_FILE = "bank_statement (2).pdf"

# --- Load ERP Data ---
def load_erp(path):
    df = pd.read_excel(path)
    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]
    return df

# --- Load Bank Data ---
def load_bank(path):
    records = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if not table:
                continue
            headers = [h.strip().lower() for h in table[0]]
            for row in table[1:]:
                if not row or len(row) < 4:
                    continue
                record = dict(zip(headers, row))
                try:
                    record["amount"] = float(record["amount"])
                except Exception:
                    continue
                records.append(record)
    return pd.DataFrame(records)

# --- Reconciliation Logic ---
def reconcile(erp_df, bank_df):
    results = {
        "matched": [],
        "amount_mismatched": [],
        "missing_in_bank": [],
        "missing_in_erp": [],
        "duplicates": []
    }

    # ERP keyed by Ref/Invoice ID if available
    erp_lookup = {str(row.get("ref id") or row.get("id")): row for _, row in erp_df.iterrows()}
    bank_lookup = {str(row.get("ref id") or row.get("id")): row for _, row in bank_df.iterrows()}

    # Detect matches and mismatches
    for ref, erp_row in erp_lookup.items():
        if ref in bank_lookup:
            bank_row = bank_lookup[ref]
            if abs(float(erp_row["amount"]) - float(bank_row["amount"])) < 0.01:
                results["matched"].append((dict(erp_row), dict(bank_row)))
            else:
                results["amount_mismatched"].append((dict(erp_row), dict(bank_row)))
        else:
            results["missing_in_bank"].append(dict(erp_row))

    # Transactions in bank but not ERP
    for ref, bank_row in bank_lookup.items():
        if ref not in erp_lookup:
            results["missing_in_erp"].append(dict(bank_row))

    # Find duplicates in Bank
    counts = Counter(bank_df["ref id"])
    for ref, count in counts.items():
        if count > 1:
            dupes = bank_df[bank_df["ref id"] == ref].to_dict(orient="records")
            results["duplicates"].append({ref: dupes})

    return results

# --- Main Entry ---
if __name__ == "__main__":
    try:
        erp_df = load_erp(ERP_FILE)
        bank_df = load_bank(BANK_FILE)
        reconciliation = reconcile(erp_df, bank_df)

        print("ERP vs Bank Reconciliation Report")
        print("=================================")

        print(f"\n✅ Matched: {len(reconciliation['matched'])}")
        print(f"⚠️ Amount Mismatches: {len(reconciliation['amount_mismatched'])}")
        print(f"❌ Missing in Bank: {len(reconciliation['missing_in_bank'])}")
        print(f"❌ Missing in ERP: {len(reconciliation['missing_in_erp'])}")
        print(f"🔁 Duplicates in Bank: {len(reconciliation['duplicates'])}")

        print("\n\n--- JSON OUTPUT ---")
        print(json.dumps(reconciliation, indent=2, default=str))
        sys.stdout.flush()
    except Exception as e:
        print(f"Error during reconciliation: {e}", file=sys.stderr)
        sys.exit(1)
