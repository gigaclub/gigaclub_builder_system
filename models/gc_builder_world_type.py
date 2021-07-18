from odoo import fields, models, api
from odoo.exceptions import ValidationError


class GCBuilderWorldType(models.Model):
    _name = 'gc.builder.world.type'
    _description = 'GigaClub Builder World Type Model'

    name = fields.Char(required=True)
    default = fields.Boolean()

    _sql_constraints = [
        ("name_unique", "UNIQUE(name)", "NAME must be unique!")
    ]

    @api.constrains("default")
    def _check_default(self):
        for rec in self:
            if rec.default and self.search_count([("default", "=", True)]) > 1:
                raise ValidationError("default must be unique!")

    @api.model
    def get_all_world_types(self):
        return [
            {
                "id": x.id,
                "name": x.name,
                "default": x.default
            }
            for x in self.search([])
        ]
