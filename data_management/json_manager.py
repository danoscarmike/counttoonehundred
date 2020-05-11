import csv
import json


class JsonManager:
    csv_file = None
    json_file = None

    def __init__(self, file_name):
        self.json_file = file_name + ".json"
        self.csv_file = file_name + ".csv"

    def load_json(self):
        if self.json_file is None:
            return None
        try:
            with open(self.json_file, 'r') as json_file:
                self.services_json = json.load(json_file)
                return self.services_json
        except (FileNotFoundError):
            return None

    def write_json(self, data):
        with open(self.json_file, 'w') as json_file:
            json.dump(data, json_file)

    def write_csv(self):
        with open(self.csv_file, 'w') as csv_file:
            line_writer = csv.writer(csv_file, delimiter=',')
            line_writer.writerow(['title', 'service_name', 'is_cloud'])
            for service in self.services_json.keys():
                line_writer.writerow([service.get("title"), service, service.get("is_cloud")])


if __name__ == "__main__":
    json = JsonManager("cloud_apis.json")
    json.load_cloud_services()