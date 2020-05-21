from data_management.bigquery import BigQuery
from data_management.file_manager import FileManager
from processor.processor import Processor
from data_management.service_manager import ServiceManagerClient


if __name__ == "__main__":
    bq = BigQuery("yoshi-status.yoshi_coverage", "cloud_canonical")
    file_manager = FileManager("cloud_apis1.json")
    client = ServiceManagerClient()
    processor = Processor(bq, client, file_manager)
    processor.update_database()
