from data_management.file_manager import FileManager
from processor.processor import Processor
from data_management.service_manager import ServiceManagerClient


if __name__ == "__main__":
    file_manager = FileManager("cloud_apis")
    client = ServiceManagerClient()
    processor = Processor(file_manager, client)
    processor.update()
    print("cloud_apis.json updated.")
