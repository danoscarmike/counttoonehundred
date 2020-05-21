import backoff

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class ServiceManagerClient:
    client = None

    def __init__(self):
        self.client = build("servicemanagement", "v1").services()

    def backoff_hdlr(details):
        print(
            " // Backing off {wait:0.1f} seconds afters {tries} tries "
            "calling function {target}\r".format(**details)
        )

    def success_hdlr(details):
        print(" // Success\r", end="")

    @backoff.on_exception(backoff.expo, HttpError, on_backoff=backoff_hdlr)
    def list(self):
        services = []
        request = self.client.list()
        counter = 0
        print("Fetching services from Service Manager...", end=" // ")
        while request is not None:
            response = request.execute()
            for item in response["services"]:
                services.append(item["serviceName"])
                counter += 1
            request = self.client.list_next(request, response)
        print(f"Found {counter} services.")
        return services

    @backoff.on_exception(
        backoff.expo, HttpError, on_backoff=backoff_hdlr, on_success=success_hdlr
    )
    def get(self, service_name):
        print(f"Fetching config for service: {service_name}", end="")
        service_config = self.client.getConfig(serviceName=service_name).execute()
        return service_config


if __name__ == "__main__":
    import json

    client = ServiceManagerClient()
    print(json.dumps(client.get("datastudio.googleapis.com"), indent=4, sort_keys=True))
