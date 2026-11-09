import json
import re

import frappe
import requests
from frappe import _
from frappe.utils import flt

TIMEOUT = 30
REF_BASE = "https://gw.fbr.gov.pk/pdi/v1"
STATL_BASE = "https://gw.fbr.gov.pk/dist/v1"
DEFAULT_SALE_TYPE = "Goods at standard rate (default)"
REFERENCE_PATHS = {
    "provinces": "provinces",
    "uom": "uom",
    "hs_codes": "itemdesccode",
    "document_types": "doctypecode",
    "transaction_types": "transtypecode",
}


# ---------- helpers ----------
def _digits(value):
    return re.sub(r"\D", "", value or "")


def _config():
    s = frappe.get_single("TPF Settings")
    sandbox = (s.environment or "Sandbox") == "Sandbox"
    base = ((s.sandbox_base_url if sandbox else s.production_base_url) or "").strip().rstrip("/")
    if not base:
        frappe.throw(_("Set the FBR base URL in TPF Settings first."))
    return sandbox, base


def _token(client):
    t = (client.get_password("fbr_token", raise_exception=False) or "").strip()
    if t.lower().startswith("bearer "):
        t = t[7:].strip()
    if not t:
        frappe.throw(_("FBR token is missing on client {0}.").format(client.client_name))
    return t


def _request(method, url, token, payload=None):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json",
               "Accept": "application/json"}
    r = requests.request(method, url, json=payload, headers=headers, timeout=TIMEOUT)
    try:
        body = r.json()
    except ValueError:
        body = {"raw": (r.text or "")[:2000]}
    return r.status_code, body


def _log(invoice, company, action, status, http_status, request, response):
    frappe.get_doc({
        "doctype": "TPF FBR Log", "invoice": invoice, "company": company,
        "action": action, "status": status, "http_status": str(http_status),
        "request_payload": json.dumps(request, indent=2, default=str),
        "response": json.dumps(response, indent=2, default=str),
    }).insert(ignore_permissions=True)


def _fmt(code, msg):
    return f"[{code}] {msg}" if code else (msg or "")


def _fbr_errors(body):
    v = (body or {}).get("validationResponse")
    if not isinstance(v, dict):
        return [f"Unexpected FBR response: {json.dumps(body, default=str)[:300]}"]
    errors = []
    if str(v.get("statusCode")) != "00":
        errors.append(_fmt(v.get("errorCode"), v.get("error") or v.get("status")))
    for it in v.get("invoiceStatuses") or []:
        if str(it.get("statusCode")) != "00":
            errors.append("Item {}: {}".format(
                it.get("itemSNo"), _fmt(it.get("errorCode"), it.get("error") or it.get("status"))))
    if not errors and str(v.get("status", "")).lower() == "invalid":
        errors.append("FBR marked the invoice as invalid.")
    return errors


def _http_error(code, body):
    if code == 401:
        return ("HTTP 401 Unauthorized: FBR did not accept the token for this seller NTN/CNIC. "
                "Use the token issued for this exact seller and the selected environment.")
    return f"HTTP {code}: {json.dumps(body, default=str)[:300]}"


# ---------- payload ----------
def build_payload(inv, client, buyer, sandbox):
    registered = buyer.registration_type == "Registered"
    payload = {
        "invoiceType": inv.invoice_type,
        "invoiceDate": str(inv.invoice_date),
        "sellerNTNCNIC": _digits(client.ntn_cnic),
        "sellerBusinessName": client.client_name,
        "sellerProvince": client.province,
        "sellerAddress": client.address,
        "buyerNTNCNIC": _digits(buyer.ntn_cnic),
        "buyerBusinessName": buyer.buyer_name,
        "buyerProvince": buyer.province,
        "buyerAddress": buyer.address,
        "buyerRegistrationType": buyer.registration_type,
        "invoiceRefNo": (inv.reference_invoice_no or "") if inv.invoice_type == "Debit Note" else "",
        "items": [],
    }
    if sandbox:
        payload["scenarioId"] = inv.scenario_id or ("SN001" if registered else "SN002")
    for r in inv.items:
        payload["items"].append({
            "hsCode": r.hs_code,
            "productDescription": r.description,
            "rate": f"{flt(r.tax_rate):g}%",
            "uoM": r.uom,
            "quantity": flt(r.quantity),
            "totalValues": flt(r.total),
            "valueSalesExcludingST": flt(r.value_excl_tax),
            "fixedNotifiedValueOrRetailPrice": 0,
            "salesTaxApplicable": flt(r.sales_tax),
            "salesTaxWithheldAtSource": 0,
            "extraTax": 0,
            "furtherTax": flt(r.further_tax),
            "sroScheduleNo": r.sro_schedule_no or "",
            "fedPayable": 0,
            "discount": 0,
            "saleType": r.sale_type or DEFAULT_SALE_TYPE,
            "sroItemSerialNo": r.sro_item_serial_no or "",
        })
    return payload


def _pre_checks(inv, client, buyer):
    if not client.is_active:
        frappe.throw(_("Client is not active."))
    if buyer.client != inv.client:
        frappe.throw(_("Buyer does not belong to this invoice's client."))
    if not inv.items:
        frappe.throw(_("Add at least one item."))
    seller = _digits(client.ntn_cnic)
    if len(seller) not in (7, 13):
        frappe.throw(_("Seller NTN/CNIC must be 7 digits (NTN) or 13 digits (CNIC), without dashes."))
    if buyer.registration_type == "Registered" and not _digits(buyer.ntn_cnic):
        frappe.throw(_("A registered buyer needs an NTN/CNIC."))
    if seller == _digits(buyer.ntn_cnic):
        frappe.throw(_("Self-invoicing is not allowed (buyer and seller NTN/CNIC are the same)."))
    if inv.invoice_type == "Debit Note" and not inv.reference_invoice_no:
        frappe.throw(_("Reference FBR invoice number is required for a debit note."))


def _call_fbr(inv, action, url, token, payload):
    try:
        code, body = _request("POST", url, token, payload)
    except requests.RequestException as e:
        _log(inv.name, inv.company, action, "Failed", "-", payload, {"error": str(e)})
        return None, f"Network error: {e}"
    err = _http_error(code, body) if code != 200 else "; ".join(_fbr_errors(body))
    _log(inv.name, inv.company, action, "Failed" if err else "Success", code, payload, body)
    return body, (err or None)


def _fail(inv, message):
    inv.db_set({"status": "Failed", "fbr_error": message[:1000]})
    frappe.db.commit()
    frappe.throw(_("FBR rejected the invoice: {0}").format(message))


# ---------- whitelisted API ----------
@frappe.whitelist()
def submit_invoice(name):
    inv = frappe.get_doc("TPF Invoice", name)
    inv.check_permission("write")

    status = frappe.db.get_value("TPF Invoice", name, "status", for_update=True)
    if status == "Submitted to FBR":
        frappe.throw(_("Already submitted to FBR."))

    client = frappe.get_doc("TPF Client", inv.client)
    buyer = frappe.get_doc("TPF Buyer", inv.buyer)
    _pre_checks(inv, client, buyer)

    token = _token(client)
    sandbox, base = _config()
    sfx = "_sb" if sandbox else ""
    payload = build_payload(inv, client, buyer, sandbox)

    _body, err = _call_fbr(inv, "Validate", f"{base}/validateinvoicedata{sfx}", token, payload)
    if err:
        _fail(inv, err)

    body, err = _call_fbr(inv, "Post", f"{base}/postinvoicedata{sfx}", token, payload)
    if err:
        _fail(inv, err)

    number = (body or {}).get("invoiceNumber")
    if not number:
        _fail(inv, "FBR accepted the request but returned no invoice number.")

    inv.db_set({"status": "Submitted to FBR", "fbr_invoice_number": number, "fbr_error": ""})
    frappe.db.commit()
    return {"ok": True, "invoice_number": number}


@frappe.whitelist()
def check_buyer_registration(buyer):
    """Ask FBR whether a buyer NTN/CNIC is Registered or Unregistered."""
    b = frappe.get_doc("TPF Buyer", buyer)
    b.check_permission("write")
    client = frappe.get_doc("TPF Client", b.client)

    digits = _digits(b.ntn_cnic)
    if len(digits) not in (7, 9, 13):
        frappe.throw(_("Enter a valid 7/9 digit NTN or 13 digit CNIC first."))

    token = _token(client)
    payload = {"Registration_No": digits}
    url = f"{STATL_BASE}/Get_Reg_Type"
    try:
        code, body = _request("POST", url, token, payload)
        if code == 405:  # the spec text says GET; community clients use POST
            code, body = _request("GET", url, token, payload)
    except requests.RequestException as e:
        _log(None, client.company, "Buyer Lookup", "Failed", "-", payload, {"error": str(e)})
        frappe.throw(_("Could not reach FBR: {0}").format(e))

    reg = str((body or {}).get("REGISTRATION_TYPE") or "").strip().lower()
    reg_type = {"registered": "Registered", "unregistered": "Unregistered"}.get(reg)
    ok = code == 200 and reg_type is not None
    _log(None, client.company, "Buyer Lookup", "Success" if ok else "Failed", code, payload, body)
    if not ok:
        frappe.throw(_(_http_error(code, body) if code != 200 else "FBR returned an unexpected response."))

    b.db_set({"registration_type": reg_type, "fbr_verified": 1 if reg_type == "Registered" else 0})
    return {"registration_type": reg_type}


@frappe.whitelist()
def fetch_reference(client, kind):
    """Fetch FBR reference data (provinces, uom, hs_codes, ...) with a client's token."""
    c = frappe.get_doc("TPF Client", client)
    c.check_permission("read")
    path = REFERENCE_PATHS.get(kind)
    if not path:
        frappe.throw(_("Unknown reference type. Use one of: {0}").format(", ".join(REFERENCE_PATHS)))
    code, body = _request("GET", f"{REF_BASE}/{path}", _token(c))
    if code != 200:
        frappe.throw(_(_http_error(code, body)))
    return body