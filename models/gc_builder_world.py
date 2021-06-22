from odoo import fields, models, api


class GCBuilderWorld(models.Model):
    _name = 'gc.builder.world'

    name = fields.Char()
    team_ids = fields.Many2many(comodel_name="gc.builder.team")
    user_ids = fields.Many2many(comodel_name="gc.user")
    task_id = fields.Many2one(comodel_name="gc.builder.task")
