import frappe
from frappe.utils import add_months, flt, get_first_day, getdate, nowdate


def _period_start(period, today):
    if period == "This Month":
        return get_first_day(today)
    if period == "Last 3 Months":
        return get_first_day(add_months(today, -2))
    if period == "This Year":
        return getdate(f"{today.year}-01-01")
    if period == "All Time":
        return None
    return get_first_day(add_months(today, -5))  # Last 6 Months


@frappe.whitelist()
def get_dashboard_data(company=None, period="Last 6 Months"):
    today = getdate(nowdate())
    start = _period_start(period, today)

    filters = {}
    cfilters = {}
    if company:
        filters["company"] = company
        cfilters["company"] = company
    if start:
        filters["invoice_date"] = [">=", start]

    # get_list applies permission_query_conditions + User Permissions (company isolation)
    invoices = frappe.get_list(
        "TPF Invoice",
        filters=filters,
        fields=["name", "client", "buyer", "invoice_date", "status",
                "total_excl_tax", "total_sales_tax", "grand_total", "fbr_error"],
        order_by="invoice_date desc, creation desc",
        limit_page_length=0,
    )

    counts = {"Draft": 0, "Submitted to FBR": 0, "Failed": 0}
    net = tax = 0.0
    by_buyer = {}
    by_month = {}

    for inv in invoices:
        counts[inv.status] = counts.get(inv.status, 0) + 1
        if inv.status == "Failed":
            continue
        net += flt(inv.total_excl_tax)
        tax += flt(inv.total_sales_tax)
        by_buyer[inv.buyer] = by_buyer.get(inv.buyer, 0) + flt(inv.grand_total)
        key = str(get_first_day(inv.invoice_date))
        m = by_month.setdefault(key, {"value": 0.0, "tax": 0.0})
        m["value"] += flt(inv.grand_total)
        m["tax"] += flt(inv.total_sales_tax)

    # month buckets for the chart (max 12)
    chart_start = start or get_first_day(add_months(today, -11))
    months = []
    cur = get_first_day(chart_start)
    while cur <= today:
        months.append(cur)
        cur = add_months(cur, 1)
    months = months[-12:]

    labels = [m.strftime("%b %Y") for m in months]
    monthly_value = [round(by_month.get(str(m), {}).get("value", 0), 2) for m in months]
    monthly_tax = [round(by_month.get(str(m), {}).get("tax", 0), 2) for m in months]

    def buyer_name(b):
        return frappe.db.get_value("TPF Buyer", b, "buyer_name") or b

    def client_name(c):
        return frappe.db.get_value("TPF Client", c, "client_name") or c

    top_buyers = [
        {"name": buyer_name(b), "value": round(v, 2)}
        for b, v in sorted(by_buyer.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    recent = [{
        "name": i.name, "buyer": buyer_name(i.buyer), "client": client_name(i.client),
        "date": str(i.invoice_date), "total": flt(i.grand_total), "status": i.status,
    } for i in invoices[:8]]

    failures = [{
        "name": i.name, "buyer": buyer_name(i.buyer), "error": (i.fbr_error or "")[:140],
    } for i in invoices if i.status == "Failed"][:5]

    done = counts["Submitted to FBR"] + counts["Failed"]
    success_rate = round(counts["Submitted to FBR"] * 100.0 / done, 1) if done else 0

    clients = len(frappe.get_list("TPF Client", filters=cfilters, pluck="name", limit_page_length=0))
    buyers = len(frappe.get_list("TPF Buyer", filters=cfilters, pluck="name", limit_page_length=0))

    return {
        "kpis": {
            "total": len(invoices), "submitted": counts["Submitted to FBR"],
            "failed": counts["Failed"], "draft": counts["Draft"],
            "net": round(net, 2), "tax": round(tax, 2),
            "success_rate": success_rate, "clients": clients, "buyers": buyers,
        },
        "status": {"labels": ["Draft", "Submitted to FBR", "Failed"],
                   "values": [counts["Draft"], counts["Submitted to FBR"], counts["Failed"]]},
        "monthly": {"labels": labels, "value": monthly_value, "tax": monthly_tax},
        "top_buyers": top_buyers, "recent": recent, "failures": failures,
    }