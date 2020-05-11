import csv
import json


class FileManager:
    csv_file = None
    json_file = None

    def __init__(self, file_name):
        if file_name is not None:
            self.json_file = file_name + ".json"
            self.csv_file = file_name + ".csv"

    def load_json(self):
        if self.json_file is None:
            return None
        try:
            with open(self.json_file, "r") as json_file:
                self.services_json = json.load(json_file)
                return self.services_json
        except (FileNotFoundError):
            return None

    def write_json(self, data):
        with open(self.json_file, "w") as json_file:
            json.dump(data, json_file, sort_keys=True, indent=4)

    def write_csv(self, data):
        with open(self.csv_file, "w") as csv_file:
            line_writer = csv.writer(csv_file, delimiter=",")
            line_writer.writerow(["title", "service_name", "is_cloud"])
            for service in data.keys():
                service = data.get(service)
                title = service.get("title")
                is_cloud = service.get("is_cloud")
                line_writer.writerow([title, service, is_cloud])
