import json

from google.cloud import bigquery

# from published_protos import get_published_services


class BigQuery:
    def __init__(self, dataset, table_name):
        self.client = bigquery.Client()
        self.dataset = dataset
        self.table_name = table_name
        self.table_id = dataset + "." + table_name
        self.table = None

    def upload_to_table(self, filename, dataset, table):
        table_ref = dataset.table(table)
        job_config = bigquery.LoadJobConfig()
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
        job_config.source_format = bigquery.SourceFormat.CSV
        job_config.skip_leading_rows = 1
        job_config.autodetect = True

        with open(filename, "rb") as source_file:
            job = self.client.load_table_from_file(
                source_file, table_ref, location="US", job_config=job_config,
            )

            print(f"Starting BigQuery table update. Job ID: {job.job_id}")
            job.result()  # Waits for table load to complete.
            print(f"Table `{dataset}.{table}` update complete.")

    def stream_update(self, data):
        if not self.table:
            self.table = self.client.get_table(self.table_id)
        self.client.get_table(self.table)

        return self.client.insert_rows(self.table, data)  # Make an API request.

    def get_rows(self):
        if not self.table:
            self.table = self.client.get_table(self.table_id)
        return self.client.list_rows(self.table)


# if __name__ == "__main__":
#     dataset = "yoshi-status.yoshi_coverage"
#     table = "cloud_canonical"
#     # upload_to_table("cloud_apis.csv", dataset, table="cloud_canonical")
#     bq = BigQuery(dataset, table)
#     googleapis = get_published_services()
#     with open("/Users/danom/code/pycode/cloud_apis/cloud_apis1.json") as data_file:
#         data = json.load(data_file)
#         services = []
#         for service in data:
#             if service in googleapis:
#                 in_googleapis = True
#             else:
#                 in_googleapis = False
#             payload = data.get(service)
#             services.append((service, payload.get("title"), payload.get("is_cloud"), in_googleapis))
#
#         bq.stream_update(services)
