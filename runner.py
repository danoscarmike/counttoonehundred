from data_management.bigquery import BigQuery
from data_management.file_manager import FileManager
from processor.processor import Processor
from data_management.service_manager import ServiceManagerClient


def run():
    bq = BigQuery("yoshi-status.yoshi_coverage", "cloud_canonical")
    client = ServiceManagerClient()
    processor = Processor(bq, client)
    processor.update_database()


if __name__ == "__main__":
    run()
