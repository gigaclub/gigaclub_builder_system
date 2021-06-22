from odoo import fields, models, api


class GCBuilderTask(models.Model):
    _name = 'gc.builder.task'

    name = fields.Char()
    description = fields.Text()

    world_ids = fields.One2many(comodel_name="gc.builder.world", inverse_name="task_id")
    user_ids = fields.Many2many(comodel_name="gc.user")
    team_ids = fields.Many2many(comodel_name="gc.builder.team")
