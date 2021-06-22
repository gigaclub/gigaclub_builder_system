from odoo import fields, models, api


class GCBuilderTeam(models.Model):
    _name = 'gc.builder.team'

    name = fields.Char(required=True)
    description = fields.Text()

    user_ids = fields.One2many(comodel_name="gc.user", inverse_name="team_id")
    manager_ids = fields.One2many(comodel_name="gc.user", inverse_name="team_id")
    world_ids = fields.Many2many(comodel_name="gc.builder.world")
    task_ids = fields.Many2many(comodel_name="gc.builder.task")

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'name must be unique!')
    ]

    def is_manager(self, user_id, team_id):
        return user_id in team_id.manager_ids

    def check_team(self, team_id):
        if not team_id.user_ids and team_id.manager_ids:
            team_id.unlink()
        if not team_id.manager_ids:
            team_id.manager_ids |= team_id.user_ids[0]

    # Status Codes:
    # 3: User already in team
    # 2: Team with name already exists
    # 1: Team could not be created
    # 0: Team created successfully
    @api.model
    def create_team(self, player_uuid, name, description=False):
        user_id = self.env["gc.user"].search([("mc_uuid", "=", player_uuid)])
        if user_id.team_id is not None:
            return 3
        if not bool(self.search_count([("name", "=", name)])):
            return 2
        team_id = self.create({
            "name": name,
            "description": description,
            "manager_ids": [(4, user_id)]
        })
        if not team_id:
            return 1
        return 0

    # Status Codes:
    # 4: User has no team
    # 3: Team does not exist
    # 2: User is not member of this team
    # 1: User is not manager of this team
    # 0: Success
    @api.model
    def edit_team(self, player_uuid, name, new_name, new_description=False):
        user_id = self.env["gc.user"].search([("mc_uuid", "=", player_uuid)])
        if not user_id.team_id:
            return 4
        team_id = self.search([("name", "=", name)])
        if not team_id:
            return 3
        if user_id.team_id is not team_id:
            return 2
        if not self.is_manager(user_id, team_id):
            return 1
        team_id.write({
            "name": new_name,
            "description": new_description,
        })
        return 0

    # Status Codes:
    # 1: User has no team
    # 0: Success
    @api.model
    def leave_team(self, player_uuid):
        user_id = self.env["gc.user"].search([("mc_uuid", "=", player_uuid)])
        if not user_id.team_id:
            return 1
        team_id = user_id.team_id
        user_id.team_id = False
        self.check_team(team_id)
        return 0


