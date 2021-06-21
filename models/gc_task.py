from odoo import fields, models, api


class GCTask(models.Model):
    _name = 'gc.task'

    name = fields.Char()
    description = fields.Text()

    world_ids = fields.One2many(comodel_name="gc.world", inverse_name="task_id")
