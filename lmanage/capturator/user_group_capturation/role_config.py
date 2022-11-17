import logging
import coloredlogs
from time import sleep

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')


class LookerPermissionSet():
    def __init__(self, permissions, name):
        self.permissions = permissions
        self.name = name


class LookerModelSet():
    def __init__(self, models, name):
        self.models = models
        self.name = name


class LookerRoles():
    def __init__(self, permission_set, model_set, team, name):
        self.permission_set = permission_set
        self.model_set = model_set
        self.team = team
        self.name = name


class ExtractRoleInfo():
    def __init__(self, sdk):
        self.sdk = sdk
        self.role_base = self.get_all_roles()

    def get_all_roles(self):
        sdk = self.sdk

        response = sdk.all_roles()

        return response

    def extract_permission_sets(self):
        response = []
        for role in self.role_base:
            perm_set = LookerPermissionSet(
                permissions=role.permission_set.permissions,
                name=role.permission_set.name)
            response.append(perm_set)
        return response

    def extract_model_sets(self):
        response = []
        for role in self.role_base:
            model_set = LookerModelSet(
                models=role.model_set.models, name=role.model_set.name)
            response.append(model_set)
        return response

    def extract_role_info(self):
        response = []
        for role in self.role_base:
            groups = None
            while groups is None:
                try:
                    groups = self.sdk.role_groups(role_id=role.id)
                except:
                    sleep_no = 3
                    sleep(sleep_no)
                    logger.info(f'looker froze, sleeping for {sleep_no}')
            role_groups = [group.name for group in groups]

            lookerrole = LookerRoles(permission_set=role.permission_set.name,
                                     model_set=role.model_set.name, team=role_groups, name=role.name)
            response.append(lookerrole)

        return response
