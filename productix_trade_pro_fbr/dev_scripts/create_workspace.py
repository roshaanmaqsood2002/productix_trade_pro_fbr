import json
import frappe

APP = "productix_trade_pro_fbr"
WS = "ProductiX Trade Pro FBR"


def card(label, filters=None):
    if frappe.db.exists("Number Card", label):
        return
    frappe.get_doc({
        "doctype": "Number Card", "label": label, "type": "Document Type",
        "document_type": "TPF Invoice", "function": "Count",
        "filters_json": json.dumps(filters or []),
        "is_public": 1, "is_standard": 1,
        "module": frappe.get_module_list(APP)[0],
        "show_percentage_stats": 0,
    }).insert(ignore_permissions=True)


def run():
    module = frappe.get_module_list(APP)[0]

    card("TPF Total Invoices")
    card("TPF Submitted to FBR", [["TPF Invoice", "status", "=", "Submitted to FBR", False]])
    card("TPF Failed Invoices", [["TPF Invoice", "status", "=", "Failed", False]])
    card("TPF Draft Invoices", [["TPF Invoice", "status", "=", "Draft", False]])

    if not frappe.db.exists("Dashboard Chart", "TPF Invoices by Status"):
        frappe.get_doc({
            "doctype": "Dashboard Chart", "chart_name": "TPF Invoices by Status",
            "chart_type": "Group By", "document_type": "TPF Invoice",
            "group_by_type": "Count", "group_by_based_on": "status",
            "type": "Bar", "is_public": 1, "is_standard": 1, "module": module,
            "filters_json": "[]", "dynamic_filters_json": "[]",
        }).insert(ignore_permissions=True)

    if frappe.db.exists("Workspace", WS):
        print("skip workspace (exists)")
        return

    cards = ["TPF Total Invoices", "TPF Submitted to FBR", "TPF Failed Invoices", "TPF Draft Invoices"]
    shortcuts = [("TPF Invoice", "TPF Invoice"), ("TPF Client", "TPF Client"),
                 ("TPF Buyer", "TPF Buyer"), ("TPF Product", "TPF Product"),
                 ("TPF FBR Log", "TPF FBR Log")]

    content = [{"id": "h1", "type": "header",
                "data": {"text": '<span class="h4"><b>Overview</b></span>', "col": 12}}]
    content += [{"id": f"n{i}", "type": "number_card", "data": {"number_card_name": c, "col": 3}}
                for i, c in enumerate(cards)]
    content.append({"id": "c1", "type": "chart",
                    "data": {"chart_name": "TPF Invoices by Status", "col": 12}})
    content.append({"id": "h2", "type": "header",
                    "data": {"text": '<span class="h4"><b>Shortcuts</b></span>', "col": 12}})
    content += [{"id": f"s{i}", "type": "shortcut", "data": {"shortcut_name": s[0], "col": 3}}
                for i, s in enumerate(shortcuts)]

    frappe.get_doc({
        "doctype": "Workspace", "name": WS, "label": WS, "title": WS,
        "module": module, "public": 1, "is_hidden": 0, "icon": "receipt",
        "content": json.dumps(content),
        "number_cards": [{"number_card_name": c, "label": c} for c in cards],
        "charts": [{"chart_name": "TPF Invoices by Status", "label": "Invoices by Status"}],
        "shortcuts": [{"label": s[0], "type": "DocType", "link_to": s[1], "doc_view": "List"}
                      for s in shortcuts],
    }).insert(ignore_permissions=True)
    frappe.db.commit()
    print("created workspace")