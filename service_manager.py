import json
import os

import backoff

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def backoff_hdlr(details):
    print(
        " // Backing off {wait:0.1f} seconds afters {tries} tries.\r".format(**details)
    )


def success_hdlr(details):
    print(" // Success")


class ServiceManagerClient:
    client = None

    def __init__(self):
        self.client = build("servicemanagement", "v1").services()

    @backoff.on_exception(backoff.expo, HttpError, on_backoff=backoff_hdlr)
    def list(self):
        services = []
        request = self.client.list()
        print("Service Manager: fetching services ... ")
        while request is not None:
            response = request.execute()
            for item in response["services"]:
                services.append(item["serviceName"])
            request = self.client.list_next(request, response)
        print(f"Service Manager: found {len(services)} services.")
        return services

    @backoff.on_exception(
        backoff.expo, HttpError, on_backoff=backoff_hdlr, on_success=success_hdlr
    )
    def get(self, service_name):
        print(f"Fetching config for service: {service_name}", end="")
        service_config = self.client.getConfig(serviceName=service_name).execute()
        return service_config

    def parse_service_apis(self, service_config):
        service_name = service_config.get("name")
        service_shortname = service_name[0 : service_name.find(".")]
        apis = []
        if service_config.get("apis"):
            for api in service_config.get("apis"):
                api_name = api.get("name")

                # only keep service-specific apis
                if api_name.find(service_shortname) == -1:
                    continue
                if api_name not in apis:
                    apis.append(api_name)
        return apis

    def download_service_config_json(self, service_config):
        cdir = os.getcwd() + "/service_configs/"
        service_name = service_config.get("name")
        short_name = service_name[0 : service_name.find(".googleapis.com")]
        with open(cdir + short_name + ".json", "w") as fp:
            fp.write(json.dumps(service_config, sort_keys=True, indent=4))

    def create_apis_json(self, service_list):
        all_apis = {}
        cdir = os.getcwd() + "/service_configs/"
        for service in service_list:
            service_name = service[0 : service.find(".googleapis.com")]
            try:
                with open(cdir + service_name + ".json", "r") as fp:
                    fp.close()
            except (FileNotFoundError):
                try:
                    new_service_config = sm.get(service)
                    self.download_service_config_json(new_service_config)
                except (Exception):
                    continue
            try:
                with open(cdir + service_name + ".json", "r") as fp:
                    service_config = json.loads(fp.read())
                    service_apis = self.parse_service_apis(service_config)
                    for api in service_apis:
                        all_apis[api] = service
            except (FileNotFoundError):
                continue
        return json.dumps(all_apis, indent=4, sort_keys=True)


if __name__ == "__main__":
    # import pprint

    sm = ServiceManagerClient()
    service_list = sm.list()
    all_apis = sm.create_apis_json(service_list)
    print(all_apis)
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(sm.create_apis_json(service_list))

    # apis = sm.parse_service_apis(config)
