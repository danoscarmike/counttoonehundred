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
    def list_services(self):
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
    def get_config(self, service_name):
        print(f"Fetching config for service: {service_name}", end="")
        try:
            service_config = self.client.getConfig(serviceName=service_name).execute()
            return service_config
        except HttpError as he:
            if he.resp.status == 403:
                return None
            else:
                raise HttpError(he.resp, he.content)

    def get_packages_from_config(self, service_config):
        packages = []
        if service_config and service_config.get("apis"):
            for api in service_config.get("apis"):
                api_version = api.get("version")
                api_name = api.get("name")
                if api_name.find(api_version) == -1:
                    continue
                else:
                    package_name = api_name[
                        0 : api_name.find(api_version) + len(api_version)
                    ]
                if package_name not in packages:
                    packages.append(package_name)
        return packages

    def get_all_packages(self):
        packages = {}
        services = self.list_services()
        for service in services:
            config = self.get_config(service)
            packages[service] = self.get_packages_from_config(config)
        return packages


if __name__ == "__main__":
    import pprint

    sm = ServiceManagerClient()
    # iam = sm.get_config("dns.googleapis.com")
    # iam_apis = sm.get_packages_from_config(iam)

    packages = sm.get_all_packages()
    
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(packages)
