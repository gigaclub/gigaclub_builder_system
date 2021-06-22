from odoo import fields, models, api


class GCUser(models.Model):
    _inherit = "gc.user"

    team_id = fields.Many2one(comodel_name="gc.builder.team")
    world_ids = fields.Many2many(comodel_name="gc.builder.world")
