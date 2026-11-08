frappe.ui.form.on("TPF Invoice", {
    refresh(frm) {
        frm.set_query("buyer", () => ({ filters: { client: frm.doc.client } }));
        frm.set_query("product", "items", () => ({ filters: { client: frm.doc.client } }));

        if (!frm.is_new() && frm.doc.status !== "Submitted to FBR") {
            frm.add_custom_button(__("Submit to FBR"), () => {
                frappe.confirm(__("Submit this invoice to FBR?"), () => {
                    frappe.call({
                        method: "productix_trade_pro_fbr.api.fbr.submit_invoice",
                        args: { name: frm.doc.name },
                        freeze: true,
                        freeze_message: __("Submitting to FBR..."),
                        callback: () => frm.reload_doc(),
                        error: () => frm.reload_doc(),
                    });
                });
            }).addClass("btn-primary");
        }
    },
});

frappe.ui.form.on("TPF Invoice Item", {
    product(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (!row.product) return;
        frappe.db.get_value("TPF Product", row.product,
            ["product_name", "hs_code", "uom", "default_tax_rate"]).then(({ message }) => {
            frappe.model.set_value(cdt, cdn, {
                description: message.product_name,
                hs_code: message.hs_code,
                uom: message.uom,
                tax_rate: message.default_tax_rate,
            });
        });
    },
});