from odoo import fields, models, api


class GCBuilderTask(models.Model):
    _name = 'gc.builder.task'
    _description = 'GigaClub Builder Task'

    name = fields.Char(required=True)
    description = fields.Text()
    build_width = fields.Integer(defualt=0)
    build_length = fields.Integer(default=0)

    world_ids = fields.One2many(comodel_name="gc.builder.world", inverse_name="task_id")

    def return_task(self, task_id):
        return {
            "id": task_id.id,
            "name": task_id.name,
            "description": task_id.description,
            "build_width": task_id.build_width,
            "build_length": task_id.build_length,
            "world_ids": [
                {
                    "id": w.id
                }
                for w in task_id.world_ids
            ]
        }

    @api.model
    def get_all_tasks(self):
        return [
            self.return_task(x)
            for x in self.search([])
        ]

    @api.model
    def get_task(self, id):
        task_id = self.browse(id)
        return self.return_task(task_id)
