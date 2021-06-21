from odoo import fields, models, api


class ModelName(models.Model):
    _inherit  = "gc.user"

    gc_team_id = fields.Many2one(comodel_name="gc.team")
