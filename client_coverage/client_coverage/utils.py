import json
import os

from google.cloud import secretmanager


def _get_project():
    try:
        service_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", None)
        with open(service_creds, "r") as creds_json:
            creds = json.load(creds_json)
        project = creds["project_id"]
        if project:
            return project
        else:
            project = os.environ.get("PROJECT_ID", None)
            if project:
                return project
            else:
                raise ValueError
    except ValueError:
        print("Could not determine project id.")


_PROJECT = _get_project()
_SECRET_CLIENT = secretmanager.SecretManagerServiceClient()


def _get_secret(secret, version):
    name = _SECRET_CLIENT.secret_version_path(_PROJECT, secret, version)
    response = _SECRET_CLIENT.access_secret_version(name)
    return response.payload.data.decode("UTF-8")


def is_cloud_service(service_config):
    config_string = json.dumps(service_config)
    if "Firebase" in service_config.get("title"):
        return False
    if "auth/firebase" in config_string:
        return False
    if "auth/cloud-platform" in config_string:
        return True
    if "tos/cloud" in config_string:
        return True
    return False
