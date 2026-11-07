import frappe

APP = "productix_trade_pro_fbr"
ROLES = ["TPF Admin", "TPF Operator"]
PROVINCES = "\nPunjab\nSindh\nKhyber Pakhtunkhwa\nBalochistan\nIslamabad Capital Territory\nGilgit Baltistan\nAzad Jammu and Kashmir"


def f(fieldname, fieldtype, label=None, **kw):
    d = {"fieldname": fieldname, "fieldtype": fieldtype,
         "label": label or fieldname.replace("_", " ").title()}
    d.update(kw)
    return d


def perms():
    return [
        {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "export": 1, "report": 1},
        {"role": "TPF Admin", "read": 1, "write": 1, "create": 1, "delete": 1, "export": 1, "report": 1},
        {"role": "TPF Operator", "read": 1, "write": 1, "create": 1, "delete": 0, "report": 1},
    ]


def make(name, fields, module, **kw):
    if frappe.db.exists("DocType", name):
        print(f"skip {name} (exists)")
        return
    doc = {"doctype": "DocType", "name": name, "module": module, "custom": 0,
           "fields": fields, "permissions": perms(),
           "sort_field": "modified", "sort_order": "DESC"}
    doc.update(kw)
    frappe.get_doc(doc).insert(ignore_permissions=True)
    print(f"created {name}")


def run():
    module = frappe.get_module_list(APP)[0]

    for r in ROLES:
        if not frappe.db.exists("Role", r):
            frappe.get_doc({"doctype": "Role", "role_name": r, "desk_access": 1}).insert(ignore_permissions=True)

    # 1. TPF Client
    make("TPF Client", [
        f("company", "Link", options="Company", reqd=1, in_list_view=1),
        f("client_name", "Data", reqd=1, in_list_view=1),
        f("ntn_cnic", "Data", "NTN / CNIC", reqd=1, in_list_view=1),
        f("business_type", "Select", options="\nManufacturer\nImporter\nDistributor\nWholesaler\nRetailer\nService Provider\nOther"),
        f("registration_type", "Select", options="Registered\nUnregistered", default="Registered"),
        f("province", "Select", options=PROVINCES),
        f("address", "Small Text"),
        f("fbr_token", "Password", "FBR API Token"),
        f("is_active", "Check", "Active", default="1"),
    ], module, autoname="TPF-CL-.#####", title_field="client_name",
        search_fields="client_name,ntn_cnic")

    # 2. TPF Buyer
    make("TPF Buyer", [
        f("client", "Link", options="TPF Client", reqd=1, in_list_view=1),
        f("company", "Link", options="Company", fetch_from="client.company", read_only=1),
        f("buyer_name", "Data", reqd=1, in_list_view=1),
        f("ntn_cnic", "Data", "NTN / CNIC", in_list_view=1),
        f("registration_type", "Select", options="Registered\nUnregistered", default="Registered"),
        f("province", "Select", options=PROVINCES),
        f("address", "Small Text"),
        f("fbr_verified", "Check", "FBR Verified", read_only=1),
    ], module, autoname="TPF-BY-.#####", title_field="buyer_name",
        search_fields="buyer_name,ntn_cnic")

    # 3. TPF Product
    make("TPF Product", [
        f("client", "Link", options="TPF Client", reqd=1, in_list_view=1),
        f("company", "Link", options="Company", fetch_from="client.company", read_only=1),
        f("product_name", "Data", reqd=1, in_list_view=1),
        f("hs_code", "Data", "HS Code", reqd=1, in_list_view=1),
        f("uom", "Data", "UoM", reqd=1),
        f("default_tax_rate", "Percent", default="18"),
    ], module, autoname="TPF-PR-.#####", title_field="product_name",
        search_fields="product_name,hs_code")

    # 4. TPF Invoice Item (child table, needs TPF Product to exist first)
    make("TPF Invoice Item", [
        f("product", "Link", options="TPF Product", in_list_view=1),
        f("description", "Small Text", reqd=1, in_list_view=1),
        f("hs_code", "Data", "HS Code", reqd=1, in_list_view=1),
        f("uom", "Data", "UoM", reqd=1),
        f("quantity", "Float", reqd=1, in_list_view=1, default="1"),
        f("rate", "Currency", reqd=1, in_list_view=1),
        f("tax_rate", "Percent", reqd=1, default="18"),
        f("value_excl_tax", "Currency", read_only=1),
        f("sales_tax", "Currency", read_only=1),
        f("total", "Currency", read_only=1, in_list_view=1),
    ], module, istable=1, editable_grid=1)

    # 5. TPF Invoice (uses the child table above)
    make("TPF Invoice", [
        f("client", "Link", options="TPF Client", reqd=1, in_list_view=1),
        f("company", "Link", options="Company", fetch_from="client.company", read_only=1),
        f("buyer", "Link", options="TPF Buyer", reqd=1, in_list_view=1),
        f("invoice_date", "Date", reqd=1, default="Today", in_list_view=1),
        f("invoice_type", "Select", options="Sale Invoice\nDebit Note", default="Sale Invoice"),
        f("status", "Select", options="Draft\nSubmitted to FBR\nFailed", default="Draft",
          read_only=1, in_list_view=1),
        f("items", "Table", options="TPF Invoice Item", reqd=1),
        f("total_excl_tax", "Currency", read_only=1),
        f("total_sales_tax", "Currency", read_only=1),
        f("grand_total", "Currency", read_only=1, in_list_view=1),
        f("fbr_invoice_number", "Data", "FBR Invoice Number", read_only=1),
        f("fbr_error", "Small Text", "Last FBR Error", read_only=1),
    ], module, autoname="TPF-INV-.YYYY.-.#####", title_field="buyer",
        search_fields="buyer,fbr_invoice_number")

    # 6. TPF FBR Log
    make("TPF FBR Log", [
        f("invoice", "Link", options="TPF Invoice", in_list_view=1),
        f("company", "Link", options="Company"),
        f("action", "Select", options="Validate\nPost\nBuyer Lookup", in_list_view=1),
        f("status", "Select", options="Success\nFailed", in_list_view=1),
        f("http_status", "Data"),
        f("request_payload", "Code", options="JSON"),
        f("response", "Code", options="JSON"),
    ], module, autoname="TPF-LOG-.#######")

    # 7. TPF Settings (single doctype)
    make("TPF Settings", [
        f("environment", "Select", options="Sandbox\nProduction", default="Sandbox"),
        f("sandbox_base_url", "Data", "Sandbox Base URL"),
        f("production_base_url", "Data", "Production Base URL"),
    ], module, issingle=1)

    frappe.db.commit()
