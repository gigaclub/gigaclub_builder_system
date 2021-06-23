from odoo import fields, models, api
from odoo.exceptions import ValidationError


class GCUser(models.Model):
    _inherit = "gc.user"

    team_manager_id = fields.Many2one(comodel_name="gc.builder.team")
    team_user_id = fields.Many2one(comodel_name="gc.builder.team")
    world_ids = fields.Many2many(comodel_name="gc.builder.world")

    @api.constrains("team_user_id", "team_manager_id")
    def _check_team_user_manager_id(self):
        for rec in self:
            if rec.team_user_id and rec.team_manager_id:
                raise ValidationError("managers should not be users")
