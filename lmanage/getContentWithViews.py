import warnings
import concurrent.futures
from coloredlogger import ColoredLogger
import configparser as ConfigParser
import looker_sdk
from lmanage.utils import create_df as create_df
warnings.simplefilter(action='ignore', category=FutureWarning)
logger = ColoredLogger()


def get_content_id_title(sdk):
    '''
    Function captures all metadata for dashboard's and looks and outputs a list of content id, content type, title
    '''
    content_metadata = []
    dashboard_content = sdk.all_dashboards()
    look_content = sdk.all_looks()

    logger.success('Downloading all Content')
    for dashboards in range(0, len(dashboard_content)):
        response = {}
        response['content_type'] = 'dashboard'
        response['dashboard_title'] = dashboard_content[dashboards].title
        response['dashboard_id'] = dashboard_content[dashboards].id
        content_metadata.append(response)

    for looks in range(0, len(look_content)):
        response = {}
        response['content_type'] = 'look'
        response['look_title'] = look_content[looks].title
        response['look_id'] = look_content[looks].id
        content_metadata.append(response)
    # logger.wtf(content_metadata)
    return content_metadata


def get_dashboards(sdk):
    """Accepts an instance reference and pulls all relevant dashboard info via the Looker API.
    This info includes dashboard element info such as title and field data, which we can then
    use to determine which dashboards and dashboard elements reference a table of interest.
    Returns a list that can be used to compare to views of interest.
    """

    # initialize an empty dict container that will hold the final returned objects
    dash_element_fields = []

    dashboards = sdk.all_dashboards(fields="title, id")

    for dash in dashboards:
        dash_entry = {"id": dash.id, "title": dash.title, "elements": []}
        elements = sdk.dashboard_dashboard_elements(
            dash.id, fields="id, title, query, look")

        for elem in elements:
            # element field info will either be in a query or a look. we try both
            try:
                fields = elem.query.fields
            except AttributeError:
                fields = elem.look.query.fields

            tables = parse_sql(sdk, qid=elem.query_id)

            title = elem.title or elem.look.title

            elem_entry = {"id": elem.id, "title": title,
                          "fields": fields, "tables": tables}
            dash_entry["elements"].append(elem_entry)

        dash_element_fields.append(dash_entry)

    return dash_element_fields


def dashboard_info(looker_content, sdk):
    db_metadata = sdk.dashboard_dashboard_elements(
        dashboard_id=looker_content.get('dashboard_id'))

    for element in range(0, len(db_metadata)):
        response = {}
        response['content_type'] = content.get('content_type')
        response['title'] = content.get('dashboard_title')
        response['dash_elem_id'] = db_metadata[element].id
        response['content_id'] = db_metadata[element].dashboard_id
        response['tables'] = parse_sql(
            sdk, qid=db_metadata[element].query_id)

    return response


def find_content_views(looker_content: list, sdk):
    '''
    Function loops through inputted list and isolates used fields and filters in specific content
    and exports as a list of dictionaries for easy pandas input. Filter fields are parsed and added to
    field output.
    '''
    element_info = []
    logger.success('Created element info list')
    for content in looker_content:
        if content.get('content_type') == 'dashboard':
            db_metadata = sdk.dashboard_dashboard_elements(
                dashboard_id=content.get('dashboard_id'))
            # logger.wtf(db_metadata)

            try:
                for element in range(0, len(db_metadata)):
                    response = {}
                    response['content_type'] = content.get('content_type')
                    response['title'] = content.get('dashboard_title')
                    response['dash_elem_id'] = db_metadata[element].id
                    response['content_id'] = db_metadata[element].dashboard_id
                    response['tables'] = parse_sql(
                        sdk, qid=db_metadata[element].query_id)

                    element_info.append(response)
            except TypeError:
                response = {}
                response['content_type'] = content.get('content_type')
                response['title'] = content.get('dashboard_title')
                response['dash_elem_id'] = db_metadata.id
                response['content_id'] = db_metadata.dashboard_id
                response['tables'] = parse_sql(
                    sdk, qid=db_metadata[element].query_id)

                element_info.append(response)

        elif content.get('content_type') == 'look':
            look_metadata = sdk.look(look_id=content.get('look_id'))
            response = {}
            response['content_type'] = content.get('content_type')
            response['title'] = content.get('look_title')
            response['content_id'] = content.get('look_id')
            response['tables'] = parse_sql(sdk, qid=look_metadata.query_id)

            element_info.append(response)
    logger.success('Adding elements to Pandas Df')
    # logger.wtf(element_info)
    return element_info


def parse_sql(sdk, qid: int):
    logger.success("Parsing SQL from Queries")
    try:
        sql = sdk.run_query(query_id=qid, result_format='sql')
        split_new_lines = sql.split('\n')
        # logger.wtf(split_new_lines)
        string_check = ["FROM", "LEFT", "INNER", "CROSS", "UNION", "AS"]
        froms = []
        for string in string_check:
            for sql in split_new_lines:
                sql = sql.strip()
                if sql.startswith(string):
                    froms.append(sql)
        # logger.wtf(froms)
        select_tables = [table.partition("AS")[2] for table in froms]
        response = list(set([x.partition("ON")[0].strip()
                             for x in select_tables if len(x) > 0]))
        return(response)
    except looker_sdk.error.SDKError:
        return('No Content')


def df_export(data, file_path):
    '''
    Pandas code to create a dataframe, explode the list of fields, split that column into fields and
    views
    '''
    df = create_df.create_df(data)
    df = df.explode(column='tables')
    df.to_csv(file_path)
    logger.success(df.head(30))
    logger.wtf(df.head(30))
    return df


def main(**kwargs):
    ini_file = kwargs.get("ini_file")
    file_path = kwargs.get("file_path")

    sdk = looker_sdk.init31(config_file=ini_file)

    # content_metadata = get_content_id_title(sdk=sdk)
    # print(dashboard_info(content_metadata[0], sdk))
    # logger.wtf(content_metadata)
    # map(content_metadatjk)
    # for content in content_metadata:
    #     for k,v in content.items:
    #         if k=='dashboard':

    # data = find_content_views(looker_content=content_metadata, sdk=sdk)
    # df_export(data, file_path=file_path)


if __name__ == '__main__':
    main(ini_file='/usr/local/google/home/hugoselbie/code_sample/py/projects/ini/looker.ini',
         file_path='./test.py')