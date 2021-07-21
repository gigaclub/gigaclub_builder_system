from odoo import fields, models, api
from odoo.exceptions import ValidationError


class GCUser(models.Model):
    _inherit = "gc.user"

    world_ids = fields.Many2many(comodel_name="gc.builder.world", relation="builder_user_builder_world_rel")
    world_manager_ids = fields.Many2many(comodel_name="gc.builder.world", relation="builder_manager_user_builder_world_rel")

    @api.constrains("world_ids", "world_manager_ids")
    def _check_team_user_manager_id(self):
        for rec in self:
            if rec.world_ids and rec.world_manager_ids:
                raise ValidationError("world managers should not be users")
