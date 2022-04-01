import logging
import coloredlogs
from looker_sdk import models
import looker_sdk

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


def get_unique_groups(
        parsed_yaml: dict,
        yaml_folders: list) -> list:
    """
    Takes all inputs from yaml file in the team section and extracts them returning a list of groups that has to be created.
    """
    temp_list = []
    for k, v in parsed_yaml.items():
        if 'team' in v.keys():
            team_list = parsed_yaml[k]['team']
            for team in team_list:
                temp_list.append(team)

    for folder_element in yaml_folders:
        for folder in folder_element:
            if isinstance(folder.get('team_edit'), list):
                edit_group = folder.get('team_edit')
                for group in edit_group:
                    temp_list.append(group)
            if isinstance(folder.get('team_view'), list):
                view_group = folder.get('team_view')
                for group in view_group:
                    temp_list.append(group)
            else:
                pass

    final_return = list(set(temp_list))
    logger.info('retrieved unique groups from yaml file')
    logger.debug(f'unique groups to create {final_return}')
    return final_return


def create_group_if_not_exists(
        sdk: looker_sdk,
        group_name: str) -> dict:
    """ Create a Looker Group and add Group attributes

    :group_name: Name of a Looker group to create.
    :rtype: Looker Group object.
    """
    # get group if exists
    try:
        logger.info(f'Creating group "{group_name}"')
        group = sdk.create_group(
            body=models.WriteGroup(
                can_add_to_content_metadata=True,
                name=group_name
            )
        )
        return group
    except looker_sdk.error.SDKError as err:
        logger.debug(err.args[0])
        group = sdk.search_groups()
        return group[0]


def get_group_metadata(
        sdk: looker_sdk,
        unique_group_list: list) -> list:

    group_metadata = []

    for group_name in unique_group_list:
        group = create_group_if_not_exists(sdk, group_name)
        temp = {}
        temp['group_id'] = group.id
        temp['group_name'] = group.name
        group_metadata.append(temp)

    return group_metadata


def sync_groups(
        sdk: looker_sdk,
        group_metadata_list: list,
        group_name_list: list) -> str:

    all_groups = sdk.all_groups()
    group_dict = {group.name: group.id for group in all_groups}
    # Deleting Standard Groups
    del group_dict['All Users']

    for group_name in group_dict.keys():
        if group_name not in group_name_list:
            sdk.delete_group(group_id=group_dict[group_name])
            logger.info(
                f'deleting group {group_name} to sync with yaml config')

    return 'your groups are in sync with your yaml file'


# def search_group_id(sdk: looker_sdk, group_config: dict) -> list:
#     group_metadata = []
#     for group_name, group_info in group_config.items():
#         if 'folder' in group_name:
#             logger.debug(group_name)
#             folder_name = group_info['folder']['name']
#             group = create_group_if_not_exists(sdk, folder_name)
#             temp = {}
#             temp['group_id'] = group.id
#             temp['group_name'] = group.name
#             logger.info(f'creating folder {folder_name}')
#             try:
#                 folder = sdk.create_folder(
#                     body=models.Folder(
#                         name=folder_name,
#                         parent_id=1
#                     )
#                 )
#                 temp['folder_id'] = folder.id
#                 temp['content_metadata_id'] = folder.content_metadata_id
#             except looker_sdk.error.SDKError:
#                 logger.info('folder has already been created')
#                 folder = sdk.search_folders(name=folder_name)
#                 temp['folder_id'] = folder[0]['id']
#                 temp['content_metadata_id'] = folder[0]['content_metadata_id']
#             group_metadata.append(temp)

#         else:
#             group = create_group_if_not_exists(sdk, group_name)
#             logger.info(group)
#             temp = {}
#             temp['group_id'] = group.id
#             temp['group_name'] = group.name
#             group_metadata.append(temp)
#     return group_metadata
