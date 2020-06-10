import backoff

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def backoff_hdlr(details):
    print(
        " // Backing off {wait:0.1f} seconds afters {tries} tries.\r".format(**details)
    )


def success_hdlr(details):
    print(" // Success\r", end="")


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
