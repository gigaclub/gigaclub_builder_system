from odoo import fields, models, api


class GCTeam(models.Model):
    _name = 'gc.team'

    name = fields.Char()
    description = fields.Text()

    gc_user_ids = fields.One2many(comodel_name="gc.user", inverse_name="gc_team_id")
