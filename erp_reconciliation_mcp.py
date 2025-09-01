# erp_reconciliation_mcp.py
from mcp.server.fastmcp import FastMCP
import pandas as pd
from typing import List, Dict

# Create the MCP server
mcp = FastMCP(name="ERP Reconciliation MCP")

# Load files (adjust paths as needed)
ERP_FILE = "erp_data.xlsx"
BANK_FILE = "bank_statement.csv"  # converted from PDF

def load_erp_data() -> List[Dict]:
    df = pd.read_excel(ERP_FILE)
    return df.to_dict(orient="records")

def load_bank_data() -> List[Dict]:
    df = pd.read_csv(BANK_FILE)
    return df.to_dict(orient="records")

# Define tools/resources using MCP SDK decorators
@mcp.resource("erp://transactions")
def get_erp_transactions() -> List[Dict]:
    """Retrieve ERP transactions as structured data."""
    return load_erp_data()

@mcp.resource("bank://transactions")
def get_bank_transactions() -> List[Dict]:
    """Retrieve Bank transactions as structured data."""
    return load_bank_data()

@mcp.tool()
def reconcile_transactions() -> List[Dict]:
    """Match ERP and Bank data and flag discrepancies."""
    erp = load_erp_data()
    bank = load_bank_data()
    erp_df = pd.DataFrame(erp)
    bank_df = pd.DataFrame(bank)

    merged = pd.merge(
        erp_df,
        bank_df,
        how="outer",
        left_on="Invoice ID",
        right_on="Description",
        suffixes=("_erp", "_bank"),
        indicator=True
    )

    merged["Status_flag"] = merged.apply(lambda row: (
        "Missing in ERP" if row["_merge"] == "right_only" else
        "Missing in Bank" if row["_merge"] == "left_only" else
        ("Amount mismatch" if row["Amount_erp"] != row["Amount_bank"] else "Match")
    ), axis=1)

    return merged.to_dict(orient="records")

if __name__ == "__main__":
    mcp.run()  # launches using default transport (e.g. stdio or HTTP)
