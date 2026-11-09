import frappe
from frappe.utils import nowdate
from productix_trade_pro_fbr.dev_scripts.create_test_data import TENANT_A, TENANT_B

R = []
OPA, OPB, ADM, NOP = "opa@test.com", "opb@test.com", "adma@test.com", "nop@test.com"


def check(label, ok):
    R.append((label, bool(ok)))


def listed(doctype, user):
    frappe.set_user(user)
    try:
        return set(frappe.get_list(doctype, pluck="name", limit_page_length=0))
    finally:
        frappe.set_user("Administrator")


def can(doctype, ptype, user, name=None):
    return frappe.has_permission(doctype, ptype, doc=name, user=user)


def attempt(user, doc):
    """True if the insert is accepted. Always rolled back."""
    frappe.set_user(user)
    try:
        frappe.get_doc(doc).insert()
        return True
    except Exception:
        return False
    finally:
        frappe.set_user("Administrator")
        frappe.db.rollback()


def inv_doc(client, buyer, company):
    return {"doctype": "TPF Invoice", "client": client, "buyer": buyer, "company": company,
            "invoice_date": nowdate(),
            "items": [{"description": "Perm test", "hs_code": "1234.5678", "uom": "Pcs",
                       "quantity": 1, "rate": 100, "tax_rate": 18}]}


def run():
    frappe.set_user("Administrator")
    by = lambda dt, co: set(frappe.get_all(dt, filters={"company": co}, pluck="name"))

    # 1. List isolation
    for dt in ["TPF Client", "TPF Buyer", "TPF Product", "TPF Invoice"]:
        a, b = by(dt, TENANT_A), by(dt, TENANT_B)
        check(f"{dt}: both tenants have data", a and b)
        check(f"{dt}: operator A sees only tenant A", listed(dt, OPA) == a)
        check(f"{dt}: operator B sees only tenant B", listed(dt, OPB) == b)
        check(f"{dt}: admin A sees only tenant A", listed(dt, ADM) == a)
        check(f"{dt}: user with no company permission sees nothing", not listed(dt, NOP))

    inv_a = sorted(by("TPF Invoice", TENANT_A))[0]
    inv_b = sorted(by("TPF Invoice", TENANT_B))[0]
    cl_a = sorted(by("TPF Client", TENANT_A))[0]
    cl_b = sorted(by("TPF Client", TENANT_B))[0]
    by_a = frappe.db.get_value("TPF Buyer", {"client": cl_a})
    by_b = frappe.db.get_value("TPF Buyer", {"client": cl_b})

    # 2. Direct access by name
    check("operator A can read own invoice", can("TPF Invoice", "read", OPA, inv_a))
    check("operator A cannot read tenant B invoice", not can("TPF Invoice", "read", OPA, inv_b))
    check("operator A cannot edit tenant B invoice", not can("TPF Invoice", "write", OPA, inv_b))
    check("operator B cannot read tenant A invoice", not can("TPF Invoice", "read", OPB, inv_a))
    check("no-permission user cannot read any invoice", not can("TPF Invoice", "read", NOP, inv_a))

    # 3. Role rules
    check("operator cannot delete invoices", not can("TPF Invoice", "delete", OPA, inv_a))
    check("TPF Admin can delete own-tenant invoices", can("TPF Invoice", "delete", ADM, inv_a))
    check("TPF Admin cannot delete other-tenant invoices", not can("TPF Invoice", "delete", ADM, inv_b))
    check("operator cannot edit TPF Settings", not can("TPF Settings", "write", OPA))
    check("TPF Admin cannot edit TPF Settings", not can("TPF Settings", "write", ADM))
    check("operator cannot create FBR logs", not can("TPF FBR Log", "create", OPA))
    check("operator cannot edit FBR logs", not can("TPF FBR Log", "write", OPA))
    roles = set(frappe.get_roles(OPA))
    check("operator has no System Manager role", "System Manager" not in roles and "TPF Admin" not in roles)

    # 4. Server-side write attempts (rolled back)
    check("CONTROL: operator A can create invoice for own client", attempt(OPA, inv_doc(cl_a, by_a, TENANT_A)))
    check("operator A cannot create invoice for tenant B client", not attempt(OPA, inv_doc(cl_b, by_b, TENANT_B)))
    check("operator A cannot spoof company to use tenant B client", not attempt(OPA, inv_doc(cl_b, by_b, TENANT_A)))
    check("operator A cannot mix own client with tenant B buyer", not attempt(OPA, inv_doc(cl_a, by_b, TENANT_A)))
    check("operator A cannot create a client in tenant B", not attempt(OPA, {
        "doctype": "TPF Client", "company": TENANT_B, "client_name": "Intruder",
        "ntn_cnic": "9999999"}))

    # 5. Whitelisted API
    from productix_trade_pro_fbr.api.fbr import submit_invoice
    frappe.set_user(OPB)
    try:
        submit_invoice(inv_a)
        denied = False
    except frappe.PermissionError:
        denied = True
    except Exception:
        denied = False
    finally:
        frappe.set_user("Administrator")
        frappe.db.rollback()
    check("operator B cannot submit tenant A invoice via API", denied)

    # 6. Dashboard and report
    from productix_trade_pro_fbr.api.dashboard import get_dashboard_data
    from productix_trade_pro_fbr.productix_trade_pro_fbr.report.tpf_sales_by_client.tpf_sales_by_client import execute

    frappe.set_user(OPA)
    try:
        d = get_dashboard_data(period="All Time")
        check("dashboard: operator A total equals tenant A count", d["kpis"]["total"] == len(by("TPF Invoice", TENANT_A)))
        check("dashboard: operator A sees 0 when filtering tenant B",
              get_dashboard_data(company=TENANT_B, period="All Time")["kpis"]["total"] == 0)
        _cols, rows = execute({})
        check("report: operator A sees only tenant A rows", rows and {r["company"] for r in rows} == {TENANT_A})
    finally:
        frappe.set_user("Administrator")
    frappe.set_user(NOP)
    try:
        check("report: no-permission user sees no rows", execute({})[1] == [])
    finally:
        frappe.set_user("Administrator")

    for label, ok in R:
        print(("PASS  " if ok else "FAIL  ") + label)
    print(f"\n{sum(ok for _l, ok in R)}/{len(R)} passed")