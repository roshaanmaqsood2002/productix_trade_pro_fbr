import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 160},
        {"label": _("Client"), "fieldname": "client", "fieldtype": "Link", "options": "TPF Client", "width": 160},
        {"label": _("Invoices"), "fieldname": "invoices", "fieldtype": "Int", "width": 90},
        {"label": _("Submitted"), "fieldname": "submitted", "fieldtype": "Int", "width": 90},
        {"label": _("Failed"), "fieldname": "failed", "fieldtype": "Int", "width": 90},
        {"label": _("Net Value"), "fieldname": "net", "fieldtype": "Currency", "width": 130},
        {"label": _("Sales Tax"), "fieldname": "tax", "fieldtype": "Currency", "width": 130},
        {"label": _("Total"), "fieldname": "total", "fieldtype": "Currency", "width": 130},
    ]

    conditions = ["1=1"]
    values = {}

    if filters.get("from_date"):
        conditions.append("invoice_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions.append("invoice_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]
    if filters.get("company"):
        conditions.append("company = %(company)s")
        values["company"] = filters["company"]

    # Company isolation: non-admin users only see companies they are permitted on
    from productix_trade_pro_fbr.permissions import _is_super, _allowed_companies
    if not _is_super(frappe.session.user):
        allowed = _allowed_companies(frappe.session.user)
        if not allowed:
            return columns, []
        conditions.append("company in %(allowed)s")
        values["allowed"] = tuple(allowed)

    data = frappe.db.sql(
        f"""
        select company, client,
               count(name) as invoices,
               coalesce(sum(status = 'Submitted to FBR'), 0) as submitted,
               coalesce(sum(status = 'Failed'), 0) as failed,
               coalesce(sum(total_excl_tax), 0) as net,
               coalesce(sum(total_sales_tax), 0) as tax,
               coalesce(sum(grand_total), 0) as total
        from `tabTPF Invoice`
        where {' and '.join(conditions)}
        group by company, client
        order by company, client
        """,
        values,
        as_dict=True,
    )
    return columns, data