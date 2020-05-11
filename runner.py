from data_management.json_manager import JsonManager
from processor.processor import Processor
from data_management.service_manager import ServiceManagerClient


if __name__ == "__main__":
    json_manager = JsonManager("cloud_apis.json")
    client = ServiceManagerClient()
    processor = Processor(json_manager, client)
    processor.update()
