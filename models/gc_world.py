from odoo import fields, models, api


class GCWorld(models.Model):
    _name = 'gc.world'

    name = fields.Char()
    team_id = fields.Many2one(comodel_name="gc.user")
    task_id = fields.Many2one(comodel_name="gc.task")
