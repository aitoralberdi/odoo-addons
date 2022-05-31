# Copyright 2022 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class FleetVehicleVariant(models.Model):
    _name = 'fleet.vehicle.variant'
    _description = 'Vehicle variant'

    name = fields.Char(string='Description')
