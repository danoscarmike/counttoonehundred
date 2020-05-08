import csv

from utilities import *

# 1. get list of services from service manager API
# 2. iterate over list:
    # get service config
    # create array of arrays: [name, title, documentation, is_cloud_api]
    # write array to csv

def run(writer):
    services = list_from_service_manager()
    for service in services:
        title = 'UNKNOWN'
        is_cloud = 'UNKNOWN'
        service_config = get_service_json(service)
        if service_config is not None:
            service_json = json.loads(service_config)
            if service_json.get("title"):
                title = service_json["title"]
            if service_json is not None:
                is_cloud = is_cloud_service(service_json)
        writer.writerow([title, service, is_cloud])


if __name__ == "__main__":
    with open('cloud_apis.csv', mode='w') as csv_file:
        line_writer = csv.writer(csv_file, delimiter=',')
        line_writer.writerow(['title', 'service_name', 'is_cloud'])
        run(line_writer)