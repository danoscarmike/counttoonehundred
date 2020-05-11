import csv
import requests


def get_discovery():
    r = requests.get("https://www.googleapis.com/discovery/v1/apis")
    counter = 0
    groupedApis = {}
    for service in r.json()["items"]:
        if service["name"] in groupedApis:
            groupedApis[service["name"]]["versions"].append(service["version"])
        else:
            groupedApis[service["name"]] = {}
            groupedApis[service["name"]]["versions"] = [service["version"]]
            groupedApis[service["name"]]["title"] = service["title"]
            if "documentationLink" in service:
                groupedApis[service["name"]]["doclink"] = service["documentationLink"]
            else:
                groupedApis[service["name"]]["doclink"] = ""

    for key, value in groupedApis.items():
        versions_string = ",".join(str(v) for v in value["versions"])
        line_writer.writerow([value["title"], key, versions_string, value["doclink"]])
        counter += 1

    print(f"Wrote {counter} lines to file.")


if __name__ == "__main__":
    with open("../cloud_service_versions.csv", mode="w") as csv_file:
        line_writer = csv.writer(csv_file, delimiter=",")
        line_writer.writerow(["Title", "Service", "Version(s)", "Docs"])
        get_discovery()
