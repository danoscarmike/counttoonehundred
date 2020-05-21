import json

from data_management.published_protos import get_published_services
from utils.print_strategy import PrintStrategy as ps


class Processor:
    plural_format = "services"
    print_strategy = None

    def __init__(self, bq, client, file_manager):
        self.bq = bq
        self.client = client
        self.file_manager = file_manager
        self.print_strategy = ps()

    def is_cloud_service(self, service_config):
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

    def print_update_message(self, target, counter):
        if counter == 1:
            self.plural_format = "service"

        print(f"Updated {target} with {counter} new {self.plural_format}.")

    def update_file(self):
        # read in the current canonical list of services
        cloud_apis = self.file_manager.load_json()
        googleapis_protos = get_published_services()
        if cloud_apis is None:
            print("File not found. Generating new list.")
            cloud_apis = {}
        # get the latest set of services from Service Manager
        live_services = self.client.list()

        print("Checking for new services...", end=" // ")
        counter = 0
        for service in live_services:
            if service not in cloud_apis.keys():
                counter += 1
                cloud_apis[service] = {}
                service_config = self.client.get(service)
                if service_config is not None:
                    if service_config.get("title"):
                        cloud_apis[service]["title"] = service_config["title"]
                    cloud_apis[service]["is_cloud"] = self.is_cloud_service(
                        service_config
                    )
                    if service in googleapis_protos:
                        cloud_apis[service]["in_googleapis"] = True
                    else:
                        cloud_apis[service]["in_googleapis"] = False

        self.print_strategy.print_find_success(counter=counter, source="file")

        self.file_manager.write_json(cloud_apis)
        self.file_manager.write_csv(cloud_apis)

        self.print_strategy.print_update_success(counter=counter, target="file")

    def update_database(self):
        current_rows = self.bq.get_rows()
        cloud_apis = list(current_rows)
        self.print_strategy.print_find_success(
            counter=len(cloud_apis), source=self.bq.table_id
        )

        db_services = []
        new_db_services = []
        for row in cloud_apis:
            db_services.append(row.service_name)

        live_services = self.client.list()

        counter = 0
        for service in live_services:
            if service not in db_services:
                counter += 1
                service_config = self.client.get(service)
                if service_config is not None:
                    if service_config.get("title"):
                        title = service_config["title"]
                        is_cloud = self.is_cloud_service(service_config)
                        new_db_services.append((title, service, is_cloud))

        self.print_strategy.print_find_success(counter=counter)

        if len(new_db_services) > 0:
            if self.bq.stream_update(new_db_services) == []:
                self.print_strategy.print_update_success(
                    counter=counter, target=self.bq.table_id
                )
