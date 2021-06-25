from odoo import fields, models, api
from odoo.exceptions import ValidationError


class GCBuilderTeam(models.Model):
    _name = 'gc.builder.team'

    name = fields.Char(required=True)
    description = fields.Text()

    user_ids = fields.One2many(comodel_name="gc.user", inverse_name="team_user_id", inverse="_inverse_users")
    manager_ids = fields.One2many(comodel_name="gc.user", inverse_name="team_manager_id", inverse="_inverse_users")
    world_ids = fields.Many2many(comodel_name="gc.builder.world")
    task_ids = fields.Many2many(comodel_name="gc.builder.task")

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'name must be unique!')
    ]

    def _inverse_users(self):
        for rec in self:
            if len(rec.manager_ids) == 0 and len(rec.user_ids) > 0:
                user_id = rec.user_ids[0]
                rec.user_ids[0] = None
                rec.manager_ids |= user_id
            if len(rec.user_ids) == 0 and len(rec.manager_ids) == 0:
                rec.unlink()

    # Status Codes:
    # 3: User already in team
    # 2: Team with name already exists
    # 1: Team could not be created
    # 0: Team created successfully
    @api.model
    def create_team(self, player_uuid, name, description=False):
        user_id = self.env["gc.user"].search([("mc_uuid", "=", player_uuid)])
        if user_id.team_user_id or user_id.team_manager_id:
            return 3
        if bool(self.search_count([("name", "=", name)])):
            return 2
        team_id = self.create({
            "name": name,
            "description": description,
            "manager_ids": [(4, user_id.id)]
        })
        if not team_id:
            return 1
        return 0

    # Status Codes:
    # 3: User has no team
    # 2: Team does not exist
    # 1: User is not manager of this team
    # 0: Success
    @api.model
    def edit_team(self, player_uuid, name, new_name, new_description=False):
        user_id = self.env["gc.user"].search([("mc_uuid", "=", player_uuid)])
        if not user_id.team_user_id and not user_id.team_manager_id:
            return 3
        team_id = self.search([("name", "=", name)])
        if not team_id:
            return 2
        if user_id not in team_id.manager_ids:
            return 1
        team_id.write({
            "name": new_name,
            "description": new_description if new_description else team_id.description,
        })
        return 0

    # Status Codes:
    # 1: User has no team
    # 0: Success
    @api.model
    def leave_team(self, player_uuid):
        user_id = self.env["gc.user"].search([("mc_uuid", "=", player_uuid)])
        if not user_id.team_user_id and not user_id.team_manager_id:
            return 1
        if user_id.team_manager_id:
            user_id.team_manager_id = False
        elif user_id.team_user_id:
            user_id.team_user_id = False
        self.env[self._name].search([])._inverse_users()
        return 0

    # Status Codes:
    # 3: Team does not exist
    # 2: User is not manager
    # 1: User is not user of this team
    # 0: Success
    @api.model
    def add_member(self, player_uuid, player_uuid_to_add):
        user_id = self.env["gc.user"].search([("mc_uuid", "=", player_uuid)])
        team_id = user_id.team_user_id or user_id.team_manager_id
        if not team_id:
            return 3
        if user_id not in team_id.manager_ids:
            return 2
        user_id_to_add = self.env["gc.user"].search([("mc_uuid", "=", player_uuid_to_add)])
        if user_id_to_add in team_id.user_ids:
            return 1
        team_id.user_ids |= user_id_to_add
        return 0

    # Status Codes:
    # 3: Team does not exist
    # 2: User is not manager
    # 1: User is not user of this team
    # 0: Success
    @api.model
    def kick_member(self, player_uuid, player_uuid_to_kick):
        user_id = self.env["gc.user"].search([("mc_uuid", "=", player_uuid)])
        team_id = user_id.team_user_id or user_id.team_manager_id
        if not team_id:
            return 3
        if user_id not in team_id.manager_ids:
            return 2
        user_id_to_kick = self.env["gc.user"].search([("mc_uuid", "=", player_uuid_to_kick)])
        if user_id_to_kick not in team_id.user_ids:
            return 1
        team_id.user_ids = [(3, user_id_to_kick.id)]
        return 0

    # Status Codes:
    # 4: Team does not exist
    # 3: User is not manager
    # 2: User to kick is not in a team
    # 1: User to kick is not in this team
    # 0: Success
    @api.model
    def promote_member(self, player_uuid, player_uuid_to_promote):
        user_id = self.env["gc.user"].search([("mc_uuid", "=", player_uuid)])
        team_id = user_id.team_user_id or user_id.team_manager_id
        if not team_id:
            return 4
        if user_id not in team_id.manager_ids:
            return 3
        user_id_to_promote = self.env["gc.user"].search([("mc_uuid", "=", player_uuid_to_promote)])
        if not user_id_to_promote.team_user_id:
            return 2
        if user_id_to_promote.team_user_id != team_id:
            return 1
        team_id.user_ids = [(3, user_id_to_promote.id)]
        team_id.manager_ids |= user_id_to_promote
        return 0

    # Status Codes:
    # 4: Team does not exist
    # 3: User is not manager
    # 2: User to kick is not a team
    # 1: User to kick is not in this team
    # 0: Success
    @api.model
    def demote_member(self, player_uuid, player_uuid_to_demote):
        user_id = self.env["gc.user"].search([("mc_uuid", "=", player_uuid)])
        team_id = user_id.team_user_id or user_id.team_manager_id
        if not team_id:
            return 4
        if user_id not in team_id.manager_ids:
            return 3
        user_id_to_demote = self.env["gc.user"].search([("mc_uuid", "=", player_uuid_to_demote)])
        if not user_id_to_demote.team_manager_id:
            return 2
        if user_id_to_demote.team_manager_id != team_id:
            return 1
        team_id.manager_ids = [(3, user_id_to_demote.id)]
        team_id.user_ids |= user_id_to_demote
        return 0


