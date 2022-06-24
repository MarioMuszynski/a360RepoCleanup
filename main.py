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
    endpoint = "https://sbdinc--sbx.cloud.automationanywhere.digital/v2/repository/folders/12713/list"
    content_type = "application/json"
    token = "eyJhbGciOiJSUzUxMiJ9.eyJzdWIiOiIxNjYiLCJjbGllbnRUeXBlIjoiV0VCIiwibGljZW5zZXMiOltdLCJhbmFseXRpY3NMaWNlbnNlc1B1cmNoYXNlZCI6eyJBbmFseXRpY3NDbGllbnQiOnRydWV9LCJ0ZW5hbnRVdWlkIjoiMGE2NjVkMGEtN2QzZC0xNTZiLTgxN2UtYTE4ZmE3NDEwNDljIiwiaHlicmlkVGVuYW50IjoiIiwibXVsdGlwbGVMb2dpbiI6ZmFsc2UsImlhdCI6MTY1NjA0Mzc3OCwiZXhwIjoxNjU2MDQ3Mzc4LCJpc3MiOiJBdXRvbWF0aW9uQW55d2hlcmUiLCJuYW5vVGltZSI6OTU2MjM0Mjg5MDg1MTY1fQ.Kup8Jpj6VZ8ETATd7Dx8SSt0k3hVs7fdTKojA1S9rGvNq3gyfkoMqanl6A0nw2DTDfK8CtQRmOij4SygX-gGyZzPDjpzg4EhNULALCVNSO8YiuOn4MTHV7fxz6CvWJzueEhrp07BCY46e-fDm9uedzWQMuXgU_VpUlfTEKDOFhEK2Cm8cKmbeRsxFF9dlVUJ-B-ziHqTNFGBDSi43W9LzTpqQy_BFs5vCmYukbhOu41HB2ByU2rjVcqIa4x6g7wEM0P3HuJ0pN7eq4Wjua_UoJh48CICF70O4sPh5GwaqYKe0_2UpUA3gqGahca4TSe0lWPG-K3NMFdLyKkcG7IcBg"
    headers = {"X-Authorization": token, "Content-Type": content_type}
    body_string = "{ \"page\": { \"offset\": 0, \"length\": 1000 }}"
    body_json = json.loads(body_string)
    files_left = 1
    while files_left > 0:
        res = requests.post(endpoint, headers=headers, json=body_json)
        res.raise_for_status()
        status_code = res.status_code
        logger.info(f"Get first layer status: {status_code}")
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
            if file_type == "application/vnd.aa.taskbot" or file_type == "application/vnd.aa.atmx":
                delete_file(headers, file_id)
            elif file_type == "application/vnd.aa.directory":
                logger.info("Attempting to delete folder")
                file_deleted = delete_file(headers, file_id)
                logger.info(f"Folder deleted: {file_deleted}")
                if not file_deleted:
                    logger.info("Folder not deleted - entering folder")
                    delete_files_in_sub(headers, file_id)


def delete_files_in_sub(headers, folder_id):
    try:
        logger = logging.getLogger('main_logger')
        endpoint_get_files = f"https://sbdinc--sbx.cloud.automationanywhere.digital/v2/repository/folders/{folder_id}/list"
        body_string = "{ \"page\": { \"offset\": 0, \"length\": 1000 }}"
        body_json = json.loads(body_string)
        res = requests.post(endpoint_get_files, headers=headers, json=body_json)
        res.raise_for_status()
        status_code = res.status_code
        logger.info(f"Get second layer status: {status_code}")
        content = res.content
        second_array = json.loads(content)
        logger.info(second_array)
        for index, k in enumerate(second_array['list']):
            file_id = second_array['list'][index]['id']
            file_name = second_array['list'][index]['name']
            file_type = second_array['list'][index]['type']
            logger.info(f"File type: {file_type}, Name: {file_name}, ID: {file_id}")
            if file_type == "application/vnd.aa.taskbot" or file_type == "application/vnd.aa.atmx":
                delete_file(headers, file_id)
            elif file_type == "application/vnd.aa.directory":
                logger.info("Attempting to delete folder")
                file_deleted = delete_file(headers, file_id)
                logger.info(f"Folder deleted: {file_deleted}")
                if not file_deleted:
                    logger.info("Folder not deleted - entering folder")
                    delete_files_in_sub(headers, file_id)
    except Exception as e:
        logger.error(e)


def delete_file(headers, file_id):
    try:
        logger = logging.getLogger('main_logger')
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