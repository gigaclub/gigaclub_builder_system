from odoo import fields, models, api
from odoo.exceptions import ValidationError


class GCBuilderWorld(models.Model):
    _name = 'gc.builder.world'
    _description = 'GigaClub Builder World'

    def _default_world_type_id(self):
        return self.env["gc.builder.world.type"].search([("default", "=", True)], limit=1)

    name = fields.Char()
    world_attachment_id = fields.Many2one(comodel_name="ir.attachment")
    world_type_id = fields.Many2one(comodel_name="gc.builder.world.type", default=_default_world_type_id)

    team_ids = fields.Many2many(comodel_name="gc.builder.team", relation="builder_team_builder_world_rel")
    team_manager_ids = fields.Many2many(comodel_name="gc.builder.team", relation="builder_manager_team_builder_world_rel")
    user_ids = fields.Many2many(comodel_name="gc.user", relation="builder_user_builder_world_rel")
    user_manager_ids = fields.Many2many(comodel_name="gc.user", relation="builder_manager_user_builder_world_rel")
    task_id = fields.Many2one(comodel_name="gc.builder.task", required=True)

    @api.constrains("user_ids", "user_manager_ids")
    def _check_user_and_managers(self):
        for rec in self:
            if set(rec.user_ids.ids) & set(rec.user_manager_ids.ids):
                raise ValidationError("Managers should not be users too!")

    @api.constrains("team_ids", "team_manager_ids")
    def _check_teams_and_team_managers(self):
        for rec in self:
            if set(rec.team_ids.ids) & set(rec.team_manager_ids.ids):
                raise ValidationError("Managers should not be users too!")

    @api.model
    def create_as_user(self, player_uuid, task_id, name, world_type):
        user_id = self.env["gc.user"].search([("mc_uuid", "=", player_uuid)])
        task_id = self.env["gc.builder.task"].browse(task_id)
        world_type_id = self.env["gc.builder.world.type"].search([("name", "=", world_type)])
        return self.create({
            "name": name,
            "task_id": task_id.id,
            "world_type_id": world_type_id.id,
            "user_manager_ids": [(4, user_id.id)]
        }).id

    @api.model
    def create_as_team(self, player_uuid, task_id, name, world_type):
        user_id = self.env["gc.user"].search([("mc_uuid", "=", player_uuid)])
        team_id = False
        if user_id.team_manager_id:
            team_id = user_id.team_manager_id
        elif user_id.team_user_id:
            team_id = user_id.team_user_id
        task_id = self.env["gc.builder.task"].browse(task_id)
        world_type_id = self.env["gc.builder.world.type"].search([("name", "=", world_type)])
        return self.create({
            "name": name,
            "task_id": task_id.id,
            "world_type_id": world_type_id.id,
            "team_manager_ids": [(4, team_id.id)]
        }).id

    # Status Codes:
    # 2: World does not exist
    # 1: User has no manager access to this world
    # 0: Success
    @api.model
    def add_user_to_world(self, player_uuid, player_uuid_to_add, world_id):
        user_id = self.env["gc.user"].search([("mc_uuid", "=", player_uuid)])
        world_id = self.browse(world_id)
        if not world_id:
            return 2
        if user_id not in world_id.user_manager_ids \
            or user_id not in world_id.team_manager_ids.mapped("user_ids") \
            or user_id not in world_id.team_manager_ids.mapped("manager_ids"):
            return 1
        user_id_to_add = self.env["gc.user"].search([("mc_uuid", "=", player_uuid_to_add)])
        world_id.user_ids |= user_id_to_add
        return 0

    # Status Codes:
    # 3: World does not exist
    # 2: User has no manager access to this world
    # 1: Team does not exist
    # 0: Success
    @api.model
    def add_team_to_world(self, player_uuid, team_name, world_id):
        user_id = self.env["gc.user"].search([("mc_uuid", "=", player_uuid)])
        world_id = self.browse(world_id)
        if not world_id:
            return 3
        if user_id not in world_id.user_manager_ids \
            or user_id not in world_id.team_manager_ids.mapped("user_ids") \
            or user_id not in world_id.team_manager_ids.mapped("manager_ids"):
            return 2
        team_id_to_add = self.env["gc.builder.team"].search([("name", "=", team_name)])
        if not team_id_to_add:
            return 1
        world_id.team_ids |= team_id_to_add
        return 0

    # Status Codes:
    # 2: World does not exist
    # 1: User has no manager access to this world
    # 0: Success
    @api.model
    def remove_user_from_world(self, player_uuid, player_uuid_to_remove, world_id):
        user_id = self.env["gc.user"].search([("mc_uuid", "=", player_uuid)])
        world_id = self.browse(world_id)
        if not world_id:
            return 2
        if user_id not in world_id.user_manager_ids \
            or user_id not in world_id.team_manager_ids.mapped("user_ids") \
            or user_id not in world_id.team_manager_ids.mapped("manager_ids"):
            return 1
        user_id_to_remove = self.env["gc.user"].search([("mc_uuid", "=", player_uuid_to_remove)])
        world_id.user_ids = [(3, user_id_to_remove.id)]
        return 0

    # Status Codes:
    # 3: World does not exist
    # 2: User has no manager access to this world
    # 1: Team does not exist
    # 0: Success
    @api.model
    def remove_team_from_world(self, player_uuid, team_name, world_id):
        user_id = self.env["gc.user"].search([("mc_uuid", "=", player_uuid)])
        world_id = self.browse(world_id)
        if not world_id:
            return 3
        if user_id not in world_id.user_manager_ids \
            or user_id not in world_id.team_manager_ids.mapped("user_ids") \
            or user_id not in world_id.team_manager_ids.mapped("manager_ids"):
            return 2
        team_id_to_remove = self.env["gc.builder.world"].search([("name", "=", team_name)])
        if not team_id_to_remove:
            return 1
        world_id.team_ids = [(3, team_id_to_remove.id)]

    # Status Codes:
    # 1: World does not exist
    # 0: Success
    @api.model
    def save_world(self, world_id, world_data):
        world_id = self.browse(world_id)
        if not world_id:
            return 1
        world_id.world_attachment_id = self.env["ir.attachment"].create({
            "name": world_id.name,
            "datas": world_data,
        })
        return 0

    # Status Codes:
    # 1: World does not exist
    # 0: Success
    @api.model
    def edit_world_type(self, world_id, world_type):
        world_id = self.browse(world_id)
        if not world_id:
            return 1
        world_type_id = self.env["gc.builder.world.type"].search([("name", "=", world_type)])
        world_id.write({
            "world_type_id": world_type_id.id
        })

    @api.model
    def get_world_data(self, world_id):
        world_id = self.browse(world_id)
        # TODO: This is not the final version.
        return world_id.world_attachment_id.datas

    def return_world(self, world_id):
        return {
            "name": world_id.name,
            "task_id": world_id.task_id.id,
            "world_type": world_id.world_type_id.name,
            "team_manager_ids": [
                {
                    "name": tm.name
                }
                for tm in world_id.team_manager_ids
            ],
            "team_ids": [
                {
                    "name": t.name
                }
                for t in world_id.team_ids
            ],
            "user_ids": [
                {
                    "mc_uuid": u.mc_uuid
                }
                for u in world_id.user_ids
            ],
            "user_manager_ids": [
                {
                    "mc_uuid": um.mc_uuid
                }
                for um in world_id.user_manager_ids
            ]
        }

    @api.model
    def get_all_worlds(self):
        return [
            self.return_world(x)
            for x in self.search([])
        ]

    @api.model
    def get_world(self, id):
        world_id = self.browse(id)
        return self.return_world(world_id)
