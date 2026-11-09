import json
from datetime import datetime

BASE = "apps/productix_trade_pro_fbr/productix_trade_pro_fbr/productix_trade_pro_fbr/doctype"


def add(name, fields):
    p = f"{BASE}/{name}/{name}.json"
    d = json.load(open(p))
    have = {f["fieldname"] for f in d["fields"]}
    for f in fields:
        if f["fieldname"] in have:
            continue
        d["fields"].append(f)
        d.setdefault("field_order", []).append(f["fieldname"])
    d["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    with open(p, "w") as fh:
        json.dump(d, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


add("tpf_invoice_item", [
    {"fieldname": "sale_type", "fieldtype": "Data", "label": "Sale Type",
     "default": "Goods at standard rate (default)"},
    {"fieldname": "further_tax", "fieldtype": "Currency", "label": "Further Tax"},
    {"fieldname": "sro_schedule_no", "fieldtype": "Data", "label": "SRO Schedule No"},
    {"fieldname": "sro_item_serial_no", "fieldtype": "Data", "label": "SRO Item Serial No"},
])

add("tpf_invoice", [
    {"fieldname": "scenario_id", "fieldtype": "Data", "label": "FBR Sandbox Scenario ID",
     "description": "Sandbox only. Leave blank: SN001 for registered buyers, SN002 for unregistered."},
    {"fieldname": "reference_invoice_no", "fieldtype": "Data",
     "label": "Reference FBR Invoice No", "depends_on": "eval:doc.invoice_type=='Debit Note'",
     "description": "Original FBR invoice number (debit notes only)."},
])
print("done")