# Copyright 2023 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        result = super(AccountMove, self).action_post()
        if self.partner_id and (
            self.partner_id.account_sequence_id) and (
                self.move_type == "in_invoice"):
            self.ref = self.partner_id.account_sequence_id.next_by_id()
        return result
