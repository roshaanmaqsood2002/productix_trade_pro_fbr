frappe.ui.form.on("TPF Buyer", {
    refresh(frm) {
        if (frm.is_new()) return;
        frm.add_custom_button(__("Check Registration with FBR"), () => {
            frappe.call({
                method: "productix_trade_pro_fbr.api.fbr.check_buyer_registration",
                args: { buyer: frm.doc.name },
                freeze: true,
                freeze_message: __("Asking FBR..."),
                callback: (r) => {
                    if (r.message) {
                        frappe.show_alert({
                            message: __("FBR says: {0}", [r.message.registration_type]),
                            indicator: "green",
                        });
                        frm.reload_doc();
                    }
                },
            });
        });
    },
});