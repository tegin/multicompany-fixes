# Copyright 2018 Creu Blanca
# Copyright 2018 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ("pos.order", [("account_move", "=", self.id)]),
        ]
        return res
