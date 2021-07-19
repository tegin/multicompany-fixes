# Copyright 2018 ForgeFlow, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase

_logger = logging.getLogger(__name__)


class TestAccountBankStatement(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        employees_group = cls.env.ref("base.group_user")
        multi_company_group = cls.env.ref("base.group_multi_company")
        account_user_group = cls.env.ref("account.group_account_user")
        account_manager_group = cls.env.ref("account.group_account_manager")
        cls.journal_model = cls.env["account.journal"]
        cls.statement_model = cls.env["account.bank.statement"]
        manager_account_test_group = cls.create_full_access(
            ["account.journal", "account.account", "res.partner"]
        )
        cls.company = cls.env["res.company"].create({"name": "Test company"})
        cls.company_2 = cls.env["res.company"].create(
            {"name": "Test company 2", "parent_id": cls.company.id}
        )
        cls.env.user.company_ids += cls.company
        cls.env.user.company_ids += cls.company_2

        cls.user = (
            cls.env["res.users"]
            .with_user(cls.env.user)
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Test User",
                    "login": "test_user",
                    "email": "test@oca.com",
                    "groups_id": [
                        (
                            6,
                            0,
                            [
                                employees_group.id,
                                account_user_group.id,
                                account_manager_group.id,
                                multi_company_group.id,
                                manager_account_test_group.id,
                            ],
                        )
                    ],
                    "company_id": cls.company.id,
                    "company_ids": [(4, cls.company.id), (4, cls.company_2.id)],
                }
            )
        )

        cls.cash_journal = cls.journal_model.with_user(cls.user).create(
            {
                "name": "Cash Journal 1 - Test",
                "code": "test_cash_1",
                "type": "cash",
                "company_id": cls.company.id,
            }
        )
        cls.statement = cls.statement_model.with_user(cls.user).create(
            {"journal_id": cls.cash_journal.id, "company_id": cls.company.id}
        )

    @classmethod
    def create_full_access(cls, list_of_models):
        manager_account_test_group = (
            cls.env["res.groups"].sudo().create({"name": "group_manager_product_test"})
        )
        for model in list_of_models:
            model_id = cls.env["ir.model"].sudo().search([("model", "=", model)])
            if model_id:
                access = (
                    cls.env["ir.model.access"]
                    .sudo()
                    .create(
                        {
                            "name": "full_access_%s" % model.replace(".", "_"),
                            "model_id": model_id.id,
                            "perm_read": True,
                            "perm_write": True,
                            "perm_create": True,
                            "perm_unlink": True,
                        }
                    )
                )
                access.group_id = manager_account_test_group
        return manager_account_test_group

    def test_constrains(self):
        with self.assertRaises(UserError):
            self.statement.company_id = self.company_2
        self.statement.company_id = self.company

        partner = (
            self.env["res.partner"]
            .with_user(self.user)
            .create(
                {
                    "name": "Partner Test",
                    "company_id": self.company.id,
                    "is_company": True,
                }
            )
        )

        line = (
            self.env["account.bank.statement.line"]
            .with_user(self.user)
            .create(
                {
                    "name": "Line 1 - Test",
                    "statement_id": self.statement.id,
                    "company_id": self.company.id,
                    "partner_id": partner.id,
                    "amount": 5.0,
                }
            )
        )

        with self.assertRaises(UserError):
            line.company_id = self.company_2.id
        line.company_id = self.company.id
