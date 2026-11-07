import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class TPFInvoice(Document):
    def validate(self):
        self.block_edit_after_submission()
        self.validate_links()
        self.calculate_totals()

    def block_edit_after_submission(self):
        before = self.get_doc_before_save()
        if before and before.status == "Submitted to FBR":
            frappe.throw(_("This invoice was already submitted to FBR and cannot be edited."))

    def validate_links(self):
        client = frappe.db.get_value("TPF Client", self.client, ["company", "is_active"], as_dict=True)
        if not client:
            frappe.throw(_("Client not found."))
        if not client.is_active:
            frappe.throw(_("Client is not active."))
        self.company = client.company

        buyer_client = frappe.db.get_value("TPF Buyer", self.buyer, "client")
        if buyer_client != self.client:
            frappe.throw(_("Buyer does not belong to the selected client."))

        for row in self.items:
            if row.product and frappe.db.get_value("TPF Product", row.product, "client") != self.client:
                frappe.throw(_("Row {0}: product does not belong to this client.").format(row.idx))

    def calculate_totals(self):
        net = tax = 0.0
        for row in self.items:
            row.value_excl_tax = flt(row.quantity) * flt(row.rate)
            row.sales_tax = row.value_excl_tax * flt(row.tax_rate) / 100
            row.total = row.value_excl_tax + row.sales_tax
            net += row.value_excl_tax
            tax += row.sales_tax
        self.total_excl_tax = net
        self.total_sales_tax = tax
        self.grand_total = net + tax

    def on_trash(self):
        if self.status == "Submitted to FBR":
            frappe.throw(_("Submitted invoices cannot be deleted."))