import re
import pdfplumber
import json

def extract_invoice_id(text):
    """Extract clean invoice ID (e.g., INV0001) from a text string."""
    match = re.search(r'INV\d+', str(text).upper())
    return match.group(0) if match else None

def normalize_erp_records(erp_records):
    """Strip and normalize ERP invoice IDs, filter out cancelled ones."""
    normalized = []
    for rec in erp_records:
        invoice_id = rec.get("invoice id")
        if not invoice_id:
            continue
        clean_id = extract_invoice_id(invoice_id)
        if clean_id and rec.get("status", "").lower() != "cancelled":
            rec["invoice id"] = clean_id
            normalized.append(rec)
    return normalized

def normalize_bank_records(bank_records):
    """Extract invoice IDs from bank descriptions."""
    normalized = []
    for rec in bank_records:
        desc = rec.get("description", "")
        invoice_id = extract_invoice_id(desc)
        if invoice_id:
            rec["invoice id"] = invoice_id
        normalized.append(rec)
    return normalized

def reconcile(erp_records, bank_records):
    """Compare ERP and Bank records by invoice id and amount."""
    erp_dict = {rec["invoice id"]: rec for rec in erp_records}
    bank_dict = {rec["invoice id"]: rec for rec in bank_records if "invoice id" in rec}

    matched = []
    mismatched_amounts = []
    missing_in_bank = []
    missing_in_erp = []
    duplicates_in_bank = []

    seen = set()
    for inv, bank_rec in bank_dict.items():
        if inv in seen:
            duplicates_in_bank.append(bank_rec)
            continue
        seen.add(inv)

        erp_rec = erp_dict.get(inv)
        if not erp_rec:
            missing_in_erp.append(bank_rec)
        else:
            if float(erp_rec.get("amount", 0)) == float(bank_rec.get("amount", 0)):
                matched.append((erp_rec, bank_rec))
            else:
                mismatched_amounts.append((erp_rec, bank_rec))

    # Find ERP records not in bank
    for inv, erp_rec in erp_dict.items():
        if inv not in bank_dict:
            missing_in_bank.append(erp_rec)

    return {
        "matched": matched,
        "mismatched_amounts": mismatched_amounts,
        "missing_in_bank": missing_in_bank,
        "missing_in_erp": missing_in_erp,
        "duplicates_in_bank": duplicates_in_bank,
    }

if __name__ == "__main__":
    # Load ERP & Bank data (replace with your actual sources)
    with open("erp_data.json") as f:
        erp_records = json.load(f)
    with open("bank_data.json") as f:
        bank_records = json.load(f)

    erp_records = normalize_erp_records(erp_records)
    bank_records = normalize_bank_records(bank_records)

    results = reconcile(erp_records, bank_records)

    print("\n=== Reconciliation Summary ===")
    print(f"✅ Matched: {len(results['matched'])}")
    print(f"⚠️ Amount Mismatches: {len(results['mismatched_amounts'])}")
    print(f"❌ Missing in Bank: {len(results['missing_in_bank'])}")
    print(f"❌ Missing in ERP: {len(results['missing_in_erp'])}")
    print(f"🔁 Duplicates in Bank: {len(results['duplicates_in_bank'])}")
