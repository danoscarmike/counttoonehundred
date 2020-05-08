import backoff
import json

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SERVICE_CLIENT = build('servicemanagement', 'v1').services()


def backoff_hdlr(details):
    print (f'Backing off due to {details}')


@backoff.on_exception(backoff.expo, HttpError, max_time=120, on_backoff=backoff_hdlr(str(HttpError)))
def list_from_service_manager():
    services = []
    request = SERVICE_CLIENT.list()
    counter = 0
    while request is not None:
        response = request.execute()
        for item in response["services"]:
            services.append(item["serviceName"])
            counter+=1
        request = SERVICE_CLIENT.list_next(request, response)
    print(f'Found {counter} services.')
    return services


@backoff.on_exception(backoff.expo, HttpError, max_time=120, on_backoff=backoff_hdlr(str(HttpError)))
def get_service_json(service_name):
    print(f'Fetching config for service: {service_name}', end=' // ')
    service = SERVICE_CLIENT.getConfig(serviceName=service_name).execute()
    print('Success')
    return json.dumps(service, sort_keys=True, indent=4)


def is_cloud_service(service_json):
    config_string = json.dumps(service_json)
    if 'auth/cloud-platform' in config_string:
        return True
    if 'tos/cloud' in config_string:
        return True
    return False


if __name__ == "__main__":
    service_config = get_service_json("vision.googleapis.com")
    if service_config is not None:
        print(is_cloud_service(service_config))