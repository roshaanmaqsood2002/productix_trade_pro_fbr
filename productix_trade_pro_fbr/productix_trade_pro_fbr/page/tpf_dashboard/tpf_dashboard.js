const TPF_CSS = `
.tpf-dash { padding: 4px 0 24px; }
.tpf-hero { background: linear-gradient(120deg, #0f2a5e 0%, #1d4ed8 55%, #0d9488 100%);
  color: #fff; border-radius: 14px; padding: 22px 26px; margin-bottom: 18px;
  display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px; }
.tpf-hero h2 { margin: 0 0 4px; font-size: 22px; font-weight: 700; color: #fff; }
.tpf-hero p { margin: 0; opacity: .85; font-size: 13px; }
.tpf-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.tpf-btn { background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.35); color: #fff;
  padding: 7px 14px; border-radius: 8px; font-size: 13px; cursor: pointer; transition: .15s; }
.tpf-btn:hover { background: rgba(255,255,255,.3); }
.tpf-kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 14px; margin-bottom: 18px; }
.tpf-kpi { background: var(--card-bg, #fff); border: 1px solid var(--border-color, #e5e7eb);
  border-top: 4px solid var(--c); border-radius: 12px; padding: 14px 16px; cursor: default;
  box-shadow: 0 1px 3px rgba(0,0,0,.05); transition: transform .15s, box-shadow .15s; }
.tpf-kpi.click { cursor: pointer; }
.tpf-kpi.click:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,.1); }
.tpf-kpi .lbl { font-size: 12px; color: var(--text-muted, #6b7280); text-transform: uppercase; letter-spacing: .04em; }
.tpf-kpi .val { font-size: 28px; font-weight: 700; color: var(--text-color, #111827); margin: 4px 0 2px; line-height: 1.15; }
.tpf-kpi .sub { font-size: 12px; color: var(--c); }
.tpf-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 14px; margin-bottom: 14px; }
.tpf-grid.three { grid-template-columns: 1.4fr 1fr 1fr; }
@media (max-width: 992px) { .tpf-grid, .tpf-grid.three { grid-template-columns: 1fr; } }
.tpf-card { background: var(--card-bg, #fff); border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 12px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,.05); min-width: 0; }
.tpf-card h4 { margin: 0 0 12px; font-size: 14px; font-weight: 600; color: var(--text-color, #111827); }
.tpf-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.tpf-table th { text-align: left; color: var(--text-muted, #6b7280); font-weight: 500; font-size: 11px;
  text-transform: uppercase; padding: 6px 8px; border-bottom: 1px solid var(--border-color, #e5e7eb); }
.tpf-table td { padding: 9px 8px; border-bottom: 1px solid var(--border-color, #f1f5f9); color: var(--text-color, #111827); }
.tpf-table td.num, .tpf-table th.num { text-align: right; }
.tpf-table a { color: #2563eb; font-weight: 500; }
.tpf-badge { padding: 2px 9px; border-radius: 999px; font-size: 11px; font-weight: 600; }
.tpf-badge.Draft { background: #fef3c7; color: #92400e; }
.tpf-badge.Submitted { background: #dcfce7; color: #166534; }
.tpf-badge.Failed { background: #fee2e2; color: #991b1b; }
.tpf-empty { color: var(--text-muted, #6b7280); font-size: 13px; padding: 24px 0; text-align: center; }
.tpf-bar { display: flex; align-items: center; gap: 10px; margin: 9px 0; font-size: 13px; }
.tpf-bar .nm { flex: 0 0 38%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--text-color); }
.tpf-bar .tr { flex: 1; height: 8px; background: var(--border-color, #e5e7eb); border-radius: 99px; overflow: hidden; }
.tpf-bar .fl { height: 100%; background: linear-gradient(90deg, #2563eb, #0d9488); border-radius: 99px; }
.tpf-bar .am { flex: 0 0 auto; font-weight: 600; color: var(--text-color); }
.tpf-fail { padding: 8px 0; border-bottom: 1px solid var(--border-color, #f1f5f9); font-size: 13px; }
.tpf-fail .e { color: #b91c1c; font-size: 12px; margin-top: 2px; }
`;

frappe.pages["tpf-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Trade Pro FBR"),
		single_column: true,
	});
	wrapper.tpf_dashboard = new TPFDashboard(page);
};

frappe.pages["tpf-dashboard"].on_page_show = function (wrapper) {
	if (wrapper.tpf_dashboard) wrapper.tpf_dashboard.refresh();
};

class TPFDashboard {
	constructor(page) {
		this.page = page;
		frappe.dom.set_style(TPF_CSS, "tpf-dashboard-style");
		this.$root = $('<div class="tpf-dash"></div>').appendTo(this.page.main);

		this.company = page.add_field({
			fieldname: "company", label: __("Company"), fieldtype: "Link",
			options: "Company", change: () => this.refresh(),
		});
		this.period = page.add_field({
			fieldname: "period", label: __("Period"), fieldtype: "Select",
			options: ["This Month", "Last 3 Months", "Last 6 Months", "This Year", "All Time"].join("\n"),
			default: "Last 6 Months", change: () => this.refresh(),
		});
		page.set_secondary_action(__("Refresh"), () => this.refresh(), "refresh");
		this.refresh();
	}

	refresh() {
		frappe.call({
			method: "productix_trade_pro_fbr.api.dashboard.get_dashboard_data",
			args: {
				company: this.company.get_value() || null,
				period: this.period.get_value() || "Last 6 Months",
			},
			callback: (r) => r.message && this.render(r.message),
		});
	}

	money(v) {
		return format_currency(v || 0);
	}

	render(d) {
		const k = d.kpis;
		const esc = frappe.utils.escape_html;
		const cards = [
			{ l: "Total Invoices", v: k.total, s: `${k.buyers} buyers`, c: "#2563eb", f: null },
			{ l: "Submitted to FBR", v: k.submitted, s: `${k.success_rate}% success rate`, c: "#16a34a", f: "Submitted to FBR" },
			{ l: "Failed", v: k.failed, s: "needs attention", c: "#dc2626", f: "Failed" },
			{ l: "Draft", v: k.draft, s: "not yet submitted", c: "#d97706", f: "Draft" },
			{ l: "Net Sales", v: this.money(k.net), s: "excl. sales tax", c: "#0d9488", f: null },
			{ l: "Sales Tax", v: this.money(k.tax), s: "collected", c: "#7c3aed", f: null },
			{ l: "Active Clients", v: k.clients, s: "registered sellers", c: "#0891b2", f: null },
		];

		const kpiHtml = cards.map((c) => `
			<div class="tpf-kpi ${c.f ? "click" : ""}" style="--c:${c.c}" data-status="${c.f || ""}">
				<div class="lbl">${__(c.l)}</div>
				<div class="val">${c.v}</div>
				<div class="sub">${c.s}</div>
			</div>`).join("");

		const maxBuyer = Math.max(1, ...d.top_buyers.map((b) => b.value));
		const buyersHtml = d.top_buyers.length
			? d.top_buyers.map((b) => `
				<div class="tpf-bar"><span class="nm" title="${esc(b.name)}">${esc(b.name)}</span>
				<span class="tr"><span class="fl" style="display:block;width:${(b.value / maxBuyer) * 100}%"></span></span>
				<span class="am">${this.money(b.value)}</span></div>`).join("")
			: `<div class="tpf-empty">${__("No data yet")}</div>`;

		const recentHtml = d.recent.length
			? `<table class="tpf-table"><thead><tr>
				<th>${__("Invoice")}</th><th>${__("Buyer")}</th><th>${__("Date")}</th>
				<th class="num">${__("Total")}</th><th>${__("Status")}</th></tr></thead><tbody>` +
			d.recent.map((r) => `<tr>
				<td><a href="/app/tpf-invoice/${encodeURIComponent(r.name)}">${esc(r.name)}</a></td>
				<td>${esc(r.buyer)}</td><td>${frappe.datetime.str_to_user(r.date)}</td>
				<td class="num">${this.money(r.total)}</td>
				<td><span class="tpf-badge ${r.status.split(" ")[0]}">${esc(r.status)}</span></td></tr>`).join("") +
			`</tbody></table>`
			: `<div class="tpf-empty">${__("No invoices in this period")}</div>`;

		const failHtml = d.failures.length
			? d.failures.map((f) => `<div class="tpf-fail">
				<a href="/app/tpf-invoice/${encodeURIComponent(f.name)}">${esc(f.name)}</a> · ${esc(f.buyer)}
				<div class="e">${esc(f.error || __("No error message saved"))}</div></div>`).join("")
			: `<div class="tpf-empty">${__("No failed invoices 🎉")}</div>`;

		this.$root.html(`
			<div class="tpf-hero">
				<div><h2>${__("Trade Pro FBR")}</h2>
				<p>${__("Sales tax invoices, FBR submissions and tenant activity at a glance")}</p></div>
				<div class="tpf-actions">
					<button class="tpf-btn" data-new="TPF Invoice">+ ${__("New Invoice")}</button>
					<button class="tpf-btn" data-new="TPF Buyer">+ ${__("New Buyer")}</button>
					<button class="tpf-btn" data-new="TPF Client">+ ${__("New Client")}</button>
				</div>
			</div>
			<div class="tpf-kpis">${kpiHtml}</div>
			<div class="tpf-grid">
				<div class="tpf-card"><h4>${__("Sales by Month")}</h4><div id="tpf-monthly"></div></div>
				<div class="tpf-card"><h4>${__("Invoices by Status")}</h4><div id="tpf-status"></div></div>
			</div>
			<div class="tpf-grid three">
				<div class="tpf-card"><h4>${__("Recent Invoices")}</h4>${recentHtml}</div>
				<div class="tpf-card"><h4>${__("Top Buyers")}</h4>${buyersHtml}</div>
				<div class="tpf-card"><h4>${__("Recent FBR Failures")}</h4>${failHtml}</div>
			</div>`);

		this.$root.find("[data-new]").on("click", (e) =>
			frappe.new_doc($(e.currentTarget).data("new")));
		this.$root.find(".tpf-kpi.click").on("click", (e) => {
			const s = $(e.currentTarget).data("status");
			if (s) frappe.set_route("List", "TPF Invoice", { status: s });
		});

		this.draw_charts(d);
	}

	draw_charts(d) {
		const monthly = d.monthly;
		if (monthly.value.some((v) => v)) {
			new frappe.Chart("#tpf-monthly", {
				type: "bar", height: 260,
				data: {
					labels: monthly.labels,
					datasets: [
						{ name: __("Total"), values: monthly.value },
						{ name: __("Sales Tax"), values: monthly.tax },
					],
				},
				colors: ["#2563eb", "#7c3aed"],
				barOptions: { spaceRatio: 0.45 },
			});
		} else {
			$("#tpf-monthly").html(`<div class="tpf-empty">${__("No sales in this period")}</div>`);
		}

		if (d.status.values.some((v) => v)) {
			new frappe.Chart("#tpf-status", {
				type: "donut", height: 260,
				data: { labels: d.status.labels, datasets: [{ values: d.status.values }] },
				colors: ["#f59e0b", "#16a34a", "#dc2626"],
			});
		} else {
			$("#tpf-status").html(`<div class="tpf-empty">${__("No invoices yet")}</div>`);
		}
	}
}	