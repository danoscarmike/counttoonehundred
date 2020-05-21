import csv
import json


def _write_csv(csv_file, data):
    with open(csv_file, "w") as csv_file:
        line_writer = csv.writer(csv_file, delimiter=",")
        line_writer.writerow(["title", "service_name", "is_cloud"])
        for service, details in data.items():
            service_name = service
            title = details.get("title")
            is_cloud = details.get("is_cloud")
            line_writer.writerow([title, service_name, is_cloud])


class FileManager:
    file_name = None

    def __init__(self, file_name):
        if file_name is not None:
            self.file_name = file_name

    def load_json(self):
        try:
            with open(self.file_name, "r") as json_file:
                self.services_json = json.load(json_file)
                return self.services_json
        except (FileNotFoundError):
            return None

    def _write_json(self, data):
        with open(self.file_name, "w") as json_file:
            json.dump(data, json_file, sort_keys=True, indent=4)

    def write_file(self, data):
        csv_file = self.file_name.replace(".json", ".csv")
        self._write_json(data)
        _write_csv(csv_file, data)
