import logging
import coloredlogs
import looker_sdk
import ruamel.yaml
import sys
from user_group_capturation import role_config as rc
from user_attribute_capturation import capture_ua_permissions as cup
from folder_capturation import folder_config as fc
from folder_capturation import create_folder_yaml_structure as cfp
from utils import looker_object_constructors as loc

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')
logging.getLogger("looker_sdk").setLevel(logging.WARNING)


def main(**kwargs):
    div = '-------------------------------------------------------------------'

    ini_file = kwargs.get("ini_file")
    logger.info(div)
    logger.info('creating yaml configuration file')

    if ini_file:
        sdk = looker_sdk.init31(config_file=ini_file)
    else:
        sdk = looker_sdk.init31()

    yaml = ruamel.yaml.YAML()

###############################################################
# Capture Folder Config #######################################
###############################################################
    folder_structurelist = fc.CaptureFolderConfig(sdk=sdk).execute()
    yaml.register_class(loc.LookerFolder)
    with open('./instance_output_settings/folder.yaml', 'w') as file:
        file.write('# FOLDER_PERMISSIONS\n')
        yaml.dump(folder_structurelist, file)

    yaml.dump(folder_structurelist, sys.stdout)

    logger.info(div)
###############################################################
# Capture Roles ###############################################
###############################################################
    roles = rc.ExtractRoleInfo(sdk=sdk)

    pset_dict_yaml_format = roles.extract_permission_sets()
    mset_dict_yaml_format = roles.extract_model_sets()

    role_meta = roles.extract_role_info()
    test = {**pset_dict_yaml_format, **mset_dict_yaml_format, **role_meta}
    with open('./instance_output_settings/role.yaml', 'w') as file:
        file.write('# MODEL_SET_ROLES\n')
        yaml.dump(test, file)

###############################################################
# Capture User Attributes #####################################
###############################################################
    ua = cup.ExtractUserAttributes(sdk=sdk)
    metadata = ua.execute()
    with open('./instance_output_settings/ua.yaml', 'w') as file:
        file.write('# USER_ATTRIBUTES\n')
        yaml.dump(metadata, file)

    # FIND UNIQUE USER ATTRIBUTES AND ATTRIBUTE TO TEAM
    # cuap.CreateAndAssignUserAttributes(
    #     user_attributes=user_attribute_metadata, sdk=sdk).execute()

    # logger.info('Lmanage has finished configuring your Looker instance!')


if __name__ == "__main__":
    IP = ('/usr/local/google/home/hugoselbie/code_sample/py/ini/k8.ini')

    main(ini_file=IP)
