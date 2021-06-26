from odoo import fields, models, api


class GCBuilderTask(models.Model):
    _name = 'gc.builder.task'
    _description = 'GigaClub Builder Task'

    name = fields.Char()
    description = fields.Text()

    world_ids = fields.One2many(comodel_name="gc.builder.world", inverse_name="task_id")
