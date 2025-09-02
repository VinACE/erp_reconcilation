# erp_reconciliation_mcp.py
from mcp.server.fastmcp import FastMCP
import pandas as pd
from typing import List, Dict

mcp = FastMCP(name="ERP Reconciliation MCP")

ERP_FILE = "erp_data.xlsx"
BANK_FILE = "bank_statement.csv"  # converted from PDF

def load_erp_data() -> List[Dict]:
    df = pd.read_excel(ERP_FILE)
    return df.to_dict(orient="records")

def load_bank_data() -> List[Dict]:
    df = pd.read_csv(BANK_FILE)
    return df.to_dict(orient="records")

@mcp.resource("resource://erp/transactions")
def get_erp_transactions() -> List[Dict]:
    """Retrieve ERP transactions as structured data."""
    return load_erp_data()

@mcp.resource("resource://bank/transactions")
def get_bank_transactions() -> List[Dict]:
    """Retrieve Bank transactions as structured data."""
    return load_bank_data()

# 🔹 Your updated reconciliation function
@mcp.tool()
def reconcile_transactions() -> List[Dict]:
    """Match ERP and Bank data and flag discrepancies."""
    erp = load_erp_data()
    bank = load_bank_data()
    erp_df = pd.DataFrame(erp)
    bank_df = pd.DataFrame(bank)

    # Normalize column names
    erp_df = erp_df.rename(columns={"Amount": "Amount"})
    bank_df = bank_df.rename(columns={"Debit/Credit": "Amount"})

    # Extract invoice ID from description
    bank_df["Invoice ID"] = bank_df["Description"].str.extract(r"(INV-\d+)")

    # Merge
    merged = pd.merge(
        erp_df,
        bank_df,
        how="outer",
        on="Invoice ID",
        suffixes=("_erp", "_bank"),
        indicator=True
    )

    import math
    def amounts_match(a, b, tol=0.01):
        if pd.isna(a) or pd.isna(b):
            return False
        return math.isclose(float(a), float(b), rel_tol=tol, abs_tol=tol)

    merged["Status_flag"] = merged.apply(lambda row: (
        "Missing in ERP" if row["_merge"] == "right_only" else
        "Missing in Bank" if row["_merge"] == "left_only" else
        ("Amount mismatch" if not amounts_match(row["Amount_erp"], row["Amount_bank"]) else "Match")
    ), axis=1)

    return merged[["Invoice ID", "Amount_erp", "Amount_bank", "Status_flag"]].to_dict(orient="records")

if __name__ == "__main__":
    mcp.run_stdio()
