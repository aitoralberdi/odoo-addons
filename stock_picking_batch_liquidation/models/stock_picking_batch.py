# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import pytz


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    inventory_ids = fields.One2many(
        string="Inventory adjustment",
        comodel_name="stock.inventory",
        inverse_name="batch_id")
    account_move_ids = fields.One2many(
        string="Account Moves",
        comodel_name="account.move",
        inverse_name="batch_id")
    account_move_count = fields.Integer(
        string="Account Move",
        compute="_compute_account_move_count")
    liquidation_contract_id = fields.Many2one(
        string="Liquidation Contract",
        comodel_name="liquidation.contract")
    chick_units = fields.Float(
        string="Chick Units",
        compute="_compute_chick_units",
        store=True)
    liquidation_min = fields.Float(
        string="Min. to be Liquidated per Chicken")
    liquidation_max = fields.Float(
       string="Max. to be Liquidated per Chicken")
    output_units = fields.Float(
        string="Output Units",
        compute="_compute_outputs_units",
        store=True)
    output_amount = fields.Float(
        string="Output Import",
        compute="_compute_outputs_units",
        store=True)
    average_age = fields.Float(
        string="Average Age",
        compute="_compute_average_age",
        store=True)
    meat_kilos = fields.Float(
        string="Meat Kilos",
        compute="_compute_outputs_units",
        store=True)
    growth_speed = fields.Float(
        string="Growth Speed",
        compute="_compute_growth_speed",
        store=True)
    cancellation_percentage = fields.Float(
        string="Cancellation %",
        compute="_compute_cancellation_percentage",
        store=True)
    consume_feed = fields.Float(
        string="Consume Feep",
        compute="_compute_consume_feed")
    conversion = fields.Float(
        string="Conversion",
        compute="_compute_conversion",
        store=True,
        digits="Feep Decimal Precision")
    feed = fields.Integer(
        string="FEEP",
        compute="_compute_feed",
        store=True)
    feed_price = fields.Float(
        string="FEEP Price",
        compute="_compute_feed_price",
        store=True,
        digits="Feep Decimal Precision")
    correction_factor = fields.Float(
        string="Correction Factor")
    amount = fields.Float(
        string="Amount",
        compute="_compute_amount",
        store=True,
        digits="Standard Cost Decimal Precision")
    amount_feed = fields.Float(
        string="Amount FEEP",
        compute="_compute_amount_feed",
        store=True,
        digits="Feep Decimal Precision")
    result = fields.Float(
        string="Result",
        compute="_compute_result",
        store=True)
    difference = fields.Float(
        string="Difference Pay/Charge",
        compute="_compute_difference",
        store=True)
    liquidation_line_ids = fields.One2many(
        string="Liquidation Lines",
        comodel_name="liquidation.line",
        inverse_name="batch_id")
    min = fields.Float(
        string="Min. to Liquidate",
        compute="_compute_min",
        store=True)
    max = fields.Float(
        string="Max. to Liquidate",
        compute="_compute_max",
        store=True)
    farm_day = fields.Integer(
        string="Farm Days",
        compute="_compute_farm_day",
        store=True)
    entry_area = fields.Float(
        string="Entry/M2",
        compute="_compute_entry_area",
        store=True)
    output_area = fields.Float(
        string="Out/M2",
        compute="_compute_output_area",
        store=True)
    meat_area = fields.Float(
        string="Kg Meat/M2",
        compute="_compute_meat_area",
        store=True)
    cancellation_area = fields.Float(
        string="Cancellations/M2",
        compute="_compute_cancellation_area",
        store=True)
    liquidation_amount = fields.Float(
        string="Liquidation Amount",
        compute="_compute_liquidation_amount",
        store="True")
    account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account")
    analytic_line_ids = fields.One2many(
        string="Analytic Lines",
        comodel_name="account.analytic.line",
        inverse_name="batch_id")
    mother_id = fields.Many2one(
        string="Mother",
        comodel_name="stock.picking.batch",
        compute="_compute_mother_id",
        store=True)

    @api.depends("move_line_ids", "move_line_ids.product_id",
                 "move_line_ids.lot_id", "move_line_ids.lot_id.batch_id",
                 "move_line_ids.location_dest_id", "location_id")
    def _compute_mother_id(self):
        for batch in self:
            mother = False
            chick_entry_line = batch.move_line_ids.filtered(
                lambda c: c.product_id.one_day_chicken and (
                    c.location_dest_id == batch.location_id and c.lot_id and (
                        c.lot_id.batch_id)))
            if chick_entry_line:
                mother = chick_entry_line[:1].lot_id.batch_id.id
            batch.mother_id = mother

    @api.depends('picking_ids', 'picking_ids.move_line_ids',
                 'picking_ids.move_lines', 'picking_ids.move_lines.state',
                 "inventory_ids", "inventory_ids.move_ids",
                 "inventory_ids.move_ids.move_line_ids")
    def _compute_move_ids(self):
        result = super(StockPickingBatch, self)._compute_move_ids()
        for batch in self:
            batch.move_line_ids = self.env["stock.move.line"].search([
                ("mother_id", "=", batch.id)])
        return result

    def _compute_account_move_count(self):
        for record in self:
            record.account_move_count = len(record.account_move_ids)

    @api.depends("min", "max", "liquidation_line_ids",
                 "liquidation_line_ids.amount")
    def _compute_liquidation_amount(self):
        for line in self:
            line.liquidation_amount = 0
            liquidation_amount = sum(line.liquidation_line_ids.mapped(
                "amount"))
            if line.liquidation_line_ids and liquidation_amount != 0:
                if liquidation_amount > line.max:
                    liquidation_amount = line.max
                if liquidation_amount < line.min:
                    liquidation_amount = line.min
            line.liquidation_amount = liquidation_amount

    @api.depends("chick_units", "output_units", "warehouse_id",
                 "warehouse_id.farm_area")
    def _compute_cancellation_area(self):
        for line in self:
            line.cancellation_area = 0
            if line.warehouse_id.farm_area != 0:
                line.cancellation_area = (
                    line.chick_units - line.output_units) / (
                        line.warehouse_id.farm_area)

    @api.depends("meat_kilos", "warehouse_id", "warehouse_id.farm_area")
    def _compute_meat_area(self):
        for line in self:
            line.meat_area = 0
            if line.warehouse_id.farm_area != 0:
                line.meat_area = line.meat_kilos / line.warehouse_id.farm_area

    @api.depends("output_units", "warehouse_id", "warehouse_id.farm_area")
    def _compute_output_area(self):
        for line in self:
            line.output_area = 0
            if line.warehouse_id.farm_area != 0:
                line.output_area = (
                    line.output_units / line.warehouse_id.farm_area)

    @api.depends("chick_units", "warehouse_id", "warehouse_id.farm_area")
    def _compute_entry_area(self):
        for line in self:
            line.entry_area = 0
            if line.warehouse_id.farm_area != 0:
                line.entry_area = (
                    line.chick_units / line.warehouse_id.farm_area)

    @api.depends("entry_date", "move_line_ids", "move_line_ids.date")
    def _compute_farm_day(self):
        for line in self:
            line.farm_day = 0
            try:
                move_type = self.env.ref(
                    "stock_picking_batch_liquidation.move_type3")
            except Exception:
                move_type = False
            if line.move_line_ids and move_type:
                move_lines = line.move_line_ids.filtered(
                    lambda c: c.move_type_id == move_type and (
                        c.state == "done")).mapped("date")
                if move_lines:
                    date = max(move_lines)
                    timezone = pytz.timezone(self._context.get('tz') or 'UTC')
                    date = date.replace(
                        tzinfo=pytz.timezone('UTC')).astimezone(timezone)
                    dif = date.date() - line.entry_date
                    line.farm_day = dif.days - 1

    @api.depends("liquidation_max", "output_units")
    def _compute_max(self):
        for line in self:
            line.max = line.liquidation_max * line.output_units

    @api.depends("liquidation_min", "output_units")
    def _compute_min(self):
        for line in self:
            line.min = line.liquidation_min * line.output_units

    @api.depends("result", "amount_feed")
    def _compute_difference(self):
        for line in self:
            line.difference = line.result - line.amount_feed

    @api.depends("amount", "amount_feed")
    def _compute_result(self):
        for line in self:
            line.result = line.amount * line.amount_feed

    @api.depends("output_units", "feed_price")
    def _compute_amount_feed(self):
        for line in self:
            line.amount_feed = line.output_units * line.feed_price

    @api.depends("feed", "liquidation_contract_id",
                 "liquidation_contract_id.feed_rate_ids")
    def _compute_feed_price(self):
        for line in self:
            line.feed_price = 0
            if (
                line.liquidation_contract_id) and (
                    line.liquidation_contract_id.feed_rate_ids):
                feed_line = (
                    line.liquidation_contract_id.feed_rate_ids.filtered(
                        lambda c: c.feed == line.feed))
                if feed_line and len(feed_line) == 1:
                    line.feed_price = feed_line.price

    @api.depends("growth_speed", "correction_factor")
    def _compute_amount(self):
        for line in self:
            line.amount = 0
            if line.correction_factor != 0:
                line.amount = line.growth_speed / line.correction_factor

    @api.depends("growth_speed", "conversion", "cancellation_percentage")
    def _compute_feed(self):
        for line in self:
            line.feed = 0
            if line.conversion != 0:
                feed = line.growth_speed * (
                    100 - line.cancellation_percentage) / (
                        line.conversion * 10)
                line.feed = round(feed, 0)

    @api.depends("meat_kilos", "conversion")
    def _compute_conversion(self):
        for line in self:
            line.conversion = 0
            if line.meat_kilos != 0:
                line.conversion = line.consume_feed / line.meat_kilos

    def _compute_consume_feed(self):
        for line in self:
            line.consume_feed = 0
            try:
                move_type = self.env.ref(
                    "stock_picking_batch_liquidation.move_type5")
            except Exception:
                move_type = False
            if line.move_line_ids and move_type:
                out_qty = sum(line.move_line_ids.filtered(
                    lambda c: c.move_type_id == move_type and (
                        c.state == "done") and c.location_id == (
                            line.location_id) and not c.picking_id).mapped(
                                "qty_done"))
                if out_qty:
                    line.consume_feed = out_qty

    @api.depends("output_units", "chick_units")
    def _compute_cancellation_percentage(self):
        for line in self:
            line.cancellation_percentage = 0
            if line.chick_units != 0:
                line.cancellation_percentage = (
                    100 - (line.output_units * 100) / line.chick_units)

    @api.depends("meat_kilos", "output_units", "average_age")
    def _compute_growth_speed(self):
        for line in self:
            line.growth_speed = 0
            if line.output_units != 0 and line.average_age != 0:
                line.growth_speed = line.meat_kilos * 1000 / (
                    line.output_units * line.average_age)

    @api.depends("output_units", "output_amount")
    def _compute_average_age(self):
        for line in self:
            line.average_age = 0
            if line.output_units != 0:
                line.average_age = line.output_amount / line.output_units

    @api.depends("move_line_ids", "move_line_ids.qty_done",
                 "move_line_ids.product_id",
                 "move_line_ids.product_id.categ_id",
                 "move_line_ids.product_id.categ_id.move_type_id",
                 "move_line_ids.state",
                 "move_line_ids.amount",
                 "move_line_ids.download_unit")
    def _compute_outputs_units(self):
        for line in self:
            line.output_units = 0
            line.output_amount = 0
            line.meat_kilos = 0
            try:
                move_type = self.env.ref(
                    "stock_picking_batch_liquidation.move_type3")
            except Exception:
                move_type = False
            if line.move_line_ids and move_type:
                line.output_units = sum(line.move_line_ids.filtered(
                    lambda c: c.move_type_id == move_type and (
                        c.state == "done") and c.location_id == (
                            line.location_id) and c.picking_id).mapped(
                                "download_unit"))
                line.output_amount = sum(line.move_line_ids.filtered(
                    lambda c: c.move_type_id == move_type and (
                        c.state == "done") and c.location_id == (
                            line.location_id) and c.picking_id).mapped(
                                "amount_days"))
                line.meat_kilos = sum(line.move_line_ids.filtered(
                    lambda c: c.move_type_id == move_type and (
                        c.state == "done") and c.location_id == (
                            line.location_id) and c.picking_id).mapped(
                                "qty_done"))

    @api.depends("move_line_ids", "move_line_ids.qty_done",
                 "move_line_ids.product_id",
                 "move_line_ids.product_id.one_day_chicken",
                 "move_line_ids.state")
    def _compute_chick_units(self):
        for line in self:
            line.chick_units = 0
            if line.move_line_ids:
                entries = sum(line.move_line_ids.filtered(
                    lambda c: c.product_id.one_day_chicken and (
                        c.state == "done" and (
                            c.location_dest_id == line.location_id)
                        )).mapped("qty_done"))
                outputs = sum(line.move_line_ids.filtered(
                    lambda c: c.product_id.one_day_chicken and (
                        c.state == "done") and c.location_id == (
                            line.location_id) and c.picking_id).mapped(
                                "qty_done"))
                line.chick_units = entries - outputs

    @api.onchange("warehouse_id")
    def onchange_warehouse_id(self):
        if self.warehouse_id and self.warehouse_id.liquidation_contract_id:
            self.liquidation_contract_id = (
                self.warehouse_id.liquidation_contract_id)

    @api.onchange("liquidation_contract_id")
    def onchange_liquidation_contract_id(self):
        if self.liquidation_contract_id:
            self.liquidation_min = (
                self.liquidation_contract_id.liquidation_min)
            self.liquidation_max = (
                self.liquidation_contract_id.liquidation_max)
            self.correction_factor = (
                self.liquidation_contract_id.correction_factor)

    def action_view_inventory_ids(self):
        context = self.env.context.copy()
        context.update({
            "default_batch_id": self.id})
        if self.location_id:
            context.update({
                "default_location_ids": [(4, self.location_id.id)]})
        if self.location_change_id:
            context.update({
                "default_location_ids": [
                    (4, self.location_id.id),
                    (4, self.location_change_id.id)]})
        return {
            "name": _("Inventory adjustment"),
            "view_mode": "tree,form",
            "res_model": "stock.inventory",
            "domain": [("id", "in", self.inventory_ids.ids)],
            "type": "ir.actions.act_window",
            "context": context
        }

    def action_view_account_move(self):
        context = self.env.context.copy()
        return {
            "name": _("Account Move"),
            "view_mode": "tree,form",
            "res_model": "account.move",
            "domain": [("id", "in", self.account_move_ids.ids)],
            "type": "ir.actions.act_window",
            "context": context
        }

    def action_do_liquidation(self):
        self.ensure_one()
        self.liquidation_line_ids.unlink()
        self.onchange_warehouse_id()
        if not (
            self.liquidation_contract_id) and not (
                self.liquidation_contract_id.feed_rate_ids):
            raise ValidationError(
                _("The contract or the contract FEEP rates are missing.")
                )
        if self.batch_type == "breeding":
            if not self.account_id:
                self.account_id = self.env["account.analytic.account"].create(
                    {"name": self.name,
                     "company_id": self.company_id.id}).id
            for line in (
                self.liquidation_contract_id.contract_line_ids.filtered(
                    "obligatory")):
                price = 0
                unit = 0
                quantity = 0
                amount = 0
                n = 1
                movelines = self.move_line_ids.filtered(
                    lambda c: c.move_type_id == line.move_type_id and (
                        c.state == "done" and c.picking_id))
                if line.quantity_type == "unit" and movelines:
                    unit = sum(movelines.mapped("download_unit"))
                if line.quantity_type == "kg" and movelines:
                    quantity = sum(movelines.mapped("qty_done"))
                if line.quantity_type == "fixed":
                    quantity = 1
                if line.price_type == "feed":
                    price = self.feed_price
                if line.price_type == "correction":
                    price = abs(self.difference)
                if line.price_type == "contract":
                    price = line.price
                if line.price_type == "average" and (
                    movelines) and sum(
                        movelines.mapped("qty_done")) != 0:
                    price = sum(movelines.mapped("amount")) / sum(
                        movelines.mapped("qty_done"))
                if line.type == "charge":
                    n = -1
                if line.type == "variable":
                    dif = self.difference
                    if dif < 0:
                        n = -1
                if quantity != 0:
                    amount = n * quantity * price
                if unit != 0:
                    amount = n * unit * price
                liquidation_line = self.env["liquidation.line"].create({
                    "product_id": line.product_id.id,
                    "type": line.type,
                    "unit": unit,
                    "quantity": quantity,
                    "price": price,
                    "amount": amount,
                    "batch_id": self.id})
                liquidation_line.onchange_amount()
            if self.analytic_line_ids:
                self.analytic_line_ids.unlink()
            self.create_liquidation_analytic_lines()
            liquidated = self.env.ref(
                "stock_picking_batch_breeding.batch_stage5")
            self.write({
                "liquidation_date": fields.Date.today(),
                "stage_id": liquidated.id})

    def create_liquidation_analytic_lines(self):
        self.ensure_one()
        try:
            chick_type = self.env.ref(
                "stock_picking_batch_liquidation.move_type1")
            meat_type = self.env.ref(
                "stock_picking_batch_liquidation.move_type3")
            drug_type = self.env.ref(
                "stock_picking_batch_liquidation.move_type4")
            feed_type = self.env.ref(
                "stock_picking_batch_liquidation.move_type5")
            breeding_tag = self.env.ref(
                "stock_picking_batch_liquidation.account_analytic_tag_breeding")
        except Exception:
                chick_type = False
                drug_type = False
                feed_type = False
                breeding_tag = False
        self.env["account.analytic.line"].create({
            "name": "Ventas",
            "account_id": self.account_id.id,
            "tag_ids": [(4, breeding_tag.id)],
            "batch_id": self.id,
            "amount": sum(self.move_line_ids.filtered(
                lambda c: c.move_type_id == meat_type).mapped("amount")),
            "unit_amount": 1,})
        self.env["account.analytic.line"].create({
            "name": "Gtos. Generales",
            "account_id": self.account_id.id,
            "tag_ids": [(4, breeding_tag.id)],
            "batch_id": self.id,
            "amount": (-1) * sum(self.move_line_ids.filtered(
                lambda c: c.move_type_id == meat_type).mapped(
                    "qty_done")) * self.liquidation_contract_id.overhead,
            "unit_amount": 1})
        self.env["account.analytic.line"].create({
            "name": "Carga Pollos",
            "account_id": self.account_id.id,
            "tag_ids": [(4, breeding_tag.id)],
            "batch_id": self.id,
            "amount": (-1) * sum(self.move_line_ids.filtered(
                lambda c: c.move_type_id == meat_type).mapped(
                    "download_unit")) * self.liquidation_contract_id.chicken_load,
            "unit_amount": 1})
        self.env["account.analytic.line"].create({
            "name": "Liquidación",
            "account_id": self.account_id.id,
            "tag_ids": [(4, breeding_tag.id)],
            "batch_id": self.id,
            "amount": (-1) * self.liquidation_amount,
            "unit_amount": 1})
        self.env["account.analytic.line"].create({
            "name": "Medicamento",
            "account_id": self.account_id.id,
            "tag_ids": [(4, breeding_tag.id)],
            "batch_id": self.id,
            "amount": (-1) * sum(self.move_line_ids.filtered(
                lambda c: c.move_type_id == drug_type).mapped("amount")),
            "unit_amount": 1})
        self.env["account.analytic.line"].create({
            "name": "Pienso",
            "account_id": self.account_id.id,
            "tag_ids": [(4, breeding_tag.id)],
            "batch_id": self.id,
            "amount": (-1) * sum(self.move_line_ids.filtered(
                lambda c: c.move_type_id == feed_type).mapped("amount")),
            "unit_amount": 1})
        self.env["account.analytic.line"].create({
            "name": "Pollito",
            "account_id": self.account_id.id,
            "tag_ids": [(4, breeding_tag.id)],
            "batch_id": self.id,
            "amount": (-1) * (sum(self.move_line_ids.filtered(
                lambda c: c.move_type_id == chick_type and (
                    c.location_dest_id == self.location_id)).mapped(
                        "amount")) - sum(self.move_line_ids.filtered(
                            lambda c: c.move_type_id == chick_type and (
                                c.location_id == self.location_id)).mapped("amount"))),
            "unit_amount": 1,})

    def action_create_invoice(self):
        self.ensure_one()
        self.onchange_warehouse_id()
        if not (
            self.liquidation_contract_id) or not (
                self.liquidation_contract_id.invoice_product_id):
            raise ValidationError(
                _("The contract or the product to invoice of the " +
                  "contract are missing."))
        if not self.billing_date:
            raise ValidationError(
                _("You must first enter the billing date."))
        tax = []
        if self.tax_entity_id.property_account_position_id and self.liquidation_contract_id.invoice_product_id.supplier_taxes_id:
            for sup_tax in self.liquidation_contract_id.invoice_product_id.supplier_taxes_id:
                taxes = self.tax_entity_id.property_account_position_id.tax_ids.filtered(lambda c: c.tax_src_id.id == sup_tax.id)
                for line in taxes:
                    if line not in tax:
                        tax.append(line.tax_dest_id.id)
        else:
            for line in self.liquidation_contract_id.invoice_product_id.supplier_taxes_id:
                if line not in tax:
                    tax.append(line.id)
        if self.batch_type == "breeding":
            self.onchange_liquidation_contract_id()
            price = sum(self.liquidation_line_ids.mapped("amount"))
            if price > self.max:
                price = self.max
            if price < self.min:
                price = self.min
            self.env["account.move"].create({
                "partner_id": self.tax_entity_id.id,
                "move_type": "in_invoice",
                "batch_id": self.id,
                "date": self.billing_date,
                "invoice_date_due": self.billing_date,
                "invoice_date": self.billing_date,
                "invoice_line_ids": [(0, 0, {
                    "product_id": (
                        self.liquidation_contract_id.invoice_product_id.id),
                    "name": (
                        self.liquidation_contract_id.invoice_product_id.name),
                    "account_id": self.liquidation_contract_id.invoice_product_id.categ_id.property_account_expense_categ_id.id,
                    "quantity": 1,
                    "product_uom_id": self.liquidation_contract_id.invoice_product_id.uom_id.id,
                    "price_unit": price,
                    "tax_ids": [(6, 0, tax)]})]})
            invoiced = self.env.ref("stock_picking_batch_breeding.batch_stage6")
            self.write({
                "stage_id": invoiced.id})
