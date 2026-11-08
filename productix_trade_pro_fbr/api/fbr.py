import json
import requests
import frappe
from frappe import _

TIMEOUT = 30
DEFAULT_SCENARIO = "SN001"  # sandbox scenario; confirm per business type in FBR doc


def _config():
    s = frappe.get_single("TPF Settings")
    sandbox = s.environment == "Sandbox"
    base = (s.sandbox_base_url if sandbox else s.production_base_url) or ""
    if not base:
        frappe.throw(_("Set the FBR base URL in TPF Settings first."))
    return sandbox, base.rstrip("/"), (s.get("sandbox_scenario_id") or DEFAULT_SCENARIO)


def _log(invoice, company, action, status, http_status, request, response):
    frappe.get_doc({
        "doctype": "TPF FBR Log", "invoice": invoice, "company": company,
        "action": action, "status": status, "http_status": str(http_status),
        "request_payload": json.dumps(request, indent=2, default=str),
        "response": json.dumps(response, indent=2, default=str),
    }).insert(ignore_permissions=True)


def build_payload(inv, client, buyer, sandbox, scenario):
    payload = {
        "invoiceType": inv.invoice_type,
        "invoiceDate": str(inv.invoice_date),
        "sellerNTNCNIC": client.ntn_cnic,
        "sellerBusinessName": client.client_name,
        "sellerProvince": client.province,
        "sellerAddress": client.address,
        "buyerNTNCNIC": buyer.ntn_cnic,
        "buyerBusinessName": buyer.buyer_name,
        "buyerProvince": buyer.province,
        "buyerAddress": buyer.address,
        "buyerRegistrationType": buyer.registration_type,
        "invoiceRefNo": inv.name,
        "items": [],
    }
    if sandbox:
        payload["scenarioId"] = scenario
    for r in inv.items:
        payload["items"].append({
            "hsCode": r.hs_code,
            "productDescription": r.description,
            "rate": f"{int(r.tax_rate)}%" if float(r.tax_rate).is_integer() else f"{r.tax_rate}%",
            "uoM": r.uom,
            "quantity": r.quantity,
            "totalValues": r.total,
            "valueSalesExcludingST": r.value_excl_tax,
            "fixedNotifiedValueOrRetailPrice": 0,
            "salesTaxApplicable": r.sales_tax,
            "salesTaxWithheldAtSource": 0,
            "extraTax": "",
            "furtherTax": 0,
            "sroScheduleNo": "",
            "fedPayable": 0,
            "discount": 0,
            "saleType": "Goods at standard rate (default)",
            "sroItemSerialNo": "",
        })
    return payload


def _post(url, token, payload):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    try:
        body = r.json()
    except ValueError:
        body = {"raw": r.text[:2000]}
    return r.status_code, body


def _validation_error(body):
    v = body.get("validationResponse") or body
    if str(v.get("statusCode", "")) == "00":
        return None
    msgs = [v.get("error")] if v.get("error") else []
    for it in v.get("invoiceStatuses") or []:
        if it.get("error"):
            msgs.append(f"Item {it.get('itemSNo')}: {it.get('error')}")
    return "; ".join(m for m in msgs if m) or json.dumps(body)[:500]


@frappe.whitelist()
def submit_invoice(name):
    inv = frappe.get_doc("TPF Invoice", name)
    inv.check_permission("write")

    status = frappe.db.get_value("TPF Invoice", name, "status", for_update=True)
    if status == "Submitted to FBR":
        frappe.throw(_("Already submitted to FBR."))

    client = frappe.get_doc("TPF Client", inv.client)
    buyer = frappe.get_doc("TPF Buyer", inv.buyer)
    token = client.get_password("fbr_token", raise_exception=False)
    if not token:
        frappe.throw(_("FBR token is missing on client {0}.").format(client.client_name))

    sandbox, base, scenario = _config()
    sfx = "_sb" if sandbox else ""
    payload = build_payload(inv, client, buyer, sandbox, scenario)

    try:
        # 1) validate
        code, body = _post(f"{base}/validateinvoicedata{sfx}", token, payload)
        err = _validation_error(body) if code == 200 else f"HTTP {code}"
        _log(inv.name, inv.company, "Validate", "Failed" if err else "Success", code, payload, body)
        if err:
            return _fail(inv, err)

        # 2) post
        code, body = _post(f"{base}/postinvoicedata{sfx}", token, payload)
        err = _validation_error(body) if code == 200 else f"HTTP {code}"
        _log(inv.name, inv.company, "Post", "Failed" if err else "Success", code, payload, body)
        if err:
            return _fail(inv, err)

        inv.db_set({"status": "Submitted to FBR",
                    "fbr_invoice_number": body.get("invoiceNumber"),
                    "fbr_error": ""})
        frappe.db.commit()
        return {"ok": True, "invoice_number": body.get("invoiceNumber")}
    except requests.RequestException as e:
        _log(inv.name, inv.company, "Post", "Failed", "-", payload, {"error": str(e)})
        return _fail(inv, f"Network error: {e}")


def _fail(inv, message):
    inv.db_set({"status": "Failed", "fbr_error": message[:1000]})
    frappe.db.commit()
    frappe.throw(_("FBR rejected the invoice: {0}").format(message))