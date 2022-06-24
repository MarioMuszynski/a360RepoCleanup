import json
import logging
import os

import requests as requests

# Initialize logging
log_formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')
setlog = logging.getLogger('main_logger')
setlog.setLevel(level=logging.INFO)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_handler = logging.FileHandler("{0}/{1}.log".format(project_root, "log"))
file_handler.setFormatter(log_formatter)
setlog.addHandler(file_handler)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
setlog.addHandler(console_handler)


def wipe_repo():
    logger = logging.getLogger('main_logger')
    parent_folder_id = "16723"
    endpoint = f"https://sbdinc--sbx.cloud.automationanywhere.digital/v2/repository/folders/{parent_folder_id}/list"
    content_type = "application/json"
    token = get_token()
    headers = {"X-Authorization": token, "Content-Type": content_type}
    body_string = "{ \"page\": { \"offset\": 0, \"length\": 1000 }}"
    body_json = json.loads(body_string)
    files_left = 1
    while files_left > 0:
        token = get_token()
        headers = {"X-Authorization": token, "Content-Type": content_type}
        res = requests.post(endpoint, headers=headers, json=body_json)
        res.raise_for_status()
        status_code = res.status_code
        content = res.content
        first_array = json.loads(content)
        logger.info(first_array)
        files_left = len(first_array['list'])
        logger.info(f"File left: {files_left}")
        for index, k in enumerate(first_array['list']):
            file_id = first_array['list'][index]['id']
            file_name = first_array['list'][index]['name']
            file_type = first_array['list'][index]['type']
            logger.info(f"File type: {file_type}, Name: {file_name}, ID: {file_id}")
            if file_type == "application/vnd.aa.directory":
                logger.info("Attempting to delete folder")
                file_deleted = delete_file(headers, file_id, file_type)
                logger.info(f"Folder deleted: {file_deleted}")
                if not file_deleted:
                    logger.info("Folder not deleted - entering folder")
                    delete_files_in_sub(headers, file_id)
                    delete_file(headers, file_id, file_type)
            else:
                delete_file(headers, file_id, file_type)


def get_token():
    auth_endpoint = "https://sbdinc--sbx.cloud.automationanywhere.digital/v1/authentication"
    content_type = "application/json"
    headers = {"Content-Type": content_type}
    api_key = "][zLm0ZLNglnDf7^VuG7n9W{J?WFE=9KlF[b=SvU"
    body_json = {
        "username": "MXM1123",
        "apiKey": api_key
    }
    res = requests.post(auth_endpoint, data=json.dumps(body_json), headers=headers)
    token = json.loads(res.text)["token"]
    return token


def delete_files_in_sub(headers, folder_id):
    try:
        logger = logging.getLogger('main_logger')
        endpoint_get_files = f"https://sbdinc--sbx.cloud.automationanywhere.digital/v2/repository/folders/{folder_id}/list"
        body_string = "{ \"page\": { \"offset\": 0, \"length\": 1000 }}"
        body_json = json.loads(body_string)
        res = requests.post(endpoint_get_files, headers=headers, json=body_json)
        res.raise_for_status()
        status_code = res.status_code
        content = res.content
        second_array = json.loads(content)
        logger.info(second_array)
        for index, k in enumerate(second_array['list']):
            file_id = second_array['list'][index]['id']
            file_name = second_array['list'][index]['name']
            file_type = second_array['list'][index]['type']
            logger.info(f"File type: {file_type}, Name: {file_name}, ID: {file_id}")
            if file_type == "application/vnd.aa.directory":
                logger.info("Attempting to delete folder")
                file_deleted = delete_file(headers, file_id, file_type)
                logger.info(f"Folder deleted: {file_deleted}")
                if not file_deleted:
                    logger.info("Folder not deleted - entering folder")
                    delete_files_in_sub(headers, file_id)
                    delete_file(headers, file_id, file_type)
            else:
                delete_file(headers, file_id, file_type)
    except Exception as e:
        logger.error(e)


def delete_file(headers, file_id, file_type):
    try:
        logger = logging.getLogger('main_logger')
        if file_type == "application/vnd.aa.directory":
            endpoint_delete = f"https://sbdinc--sbx.cloud.automationanywhere.digital/v2/repository/folders/{file_id}"
        else:
            endpoint_delete = f"https://sbdinc--sbx.cloud.automationanywhere.digital/v2/repository/files/{file_id}"
        logger.info(endpoint_delete)
        res = requests.delete(endpoint_delete, headers=headers)
        status_code = res.status_code
        res_content = res.content
        logger.info(f"Deletion status: {status_code}, Message: {res_content}")
        if status_code == "200":
            return True
        else:
            return False
    except Exception as e:
        logger.error(e)


wipe_repo()
