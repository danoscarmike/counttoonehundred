import json


class Processor():
    json_manager = None
    client = None

    def __init__(self, json_manager, client):
        self.json_manager = json_manager
        self.client = client

    def is_cloud_service(self, service_config):
        config_string = json.dumps(service_config)
        if 'Firebase' in service_config.get('title') or 'auth/firebase' in config_string:
            return False
        if 'auth/cloud-platform' in config_string:
            return True
        if 'tos/cloud' in config_string:
            return True
        return False

    def update(self):
        # read in the current canonical list of services
        cloud_apis = self.json_manager.load_json()
        if cloud_apis is None:
            print("File not found. Generating new list.")
            cloud_apis = {}
        # get the latest set of services from Service Manager
        live_services = self.client.list()


        for service in live_services:
            if service not in cloud_apis.keys():
                cloud_apis[service] = {}
                service_config = self.client.get(service)
                if service_config is not None:
                    if service_config.get("title"):
                        cloud_apis[service]["title"] = service_config["title"]
                    cloud_apis[service]["is_cloud"] = self.is_cloud_service(service_config)

        self.json_manager.write_json(cloud_apis)
