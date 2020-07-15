import sqlalchemy

from database import init_connection_engine
from googleapis import get_published_protos
from service_manager import ServiceManagerClient
from utils import is_cloud_service


def update_status_db(event, context):

    print(
        f"Successfully triggered by {context.event_id} published at \
            {context.timestamp}."
    )

    # get all services from Service Manager
    service_manager_client = ServiceManagerClient()
    service_manager = service_manager_client.list()
    service_manager_set = {x for x in service_manager}

    # get all services with protos published to github/googleapis/googleapis
    googleapis = get_published_protos()
    googleapis_services = googleapis.keys()
    googleapis_set = {x for x in googleapis_services}

    # create a superset
    all_services_set = service_manager_set | googleapis_set

    # prepare SQL statement templates
    stmt_select_service = sqlalchemy.text(
        "SELECT * FROM services WHERE service_name=:service"
    )

    stmt_update_public = sqlalchemy.text(
        "UPDATE services SET is_public=:in_service_manager, \
            in_googleapis=:in_googleapis WHERE service_name=:service"
    )

    stmt_insert_service = sqlalchemy.text(
        "INSERT INTO services (service_name, title, is_cloud, in_googleapis, \
            is_public) VALUES (:service, :title, :is_cloud, :in_googleapis, \
            :in_service_manager)"
    )

    stmt_select_star = sqlalchemy.text("SELECT * FROM services")

    # initiate database connection
    db = init_connection_engine()

    with db.connect() as conn:
        # iterate over superset of services
        for service in all_services_set:
            if service in googleapis:
                in_googleapis = 1
            else:
                in_googleapis = 0

            if service in service_manager:
                in_service_manager = 1
            else:
                in_service_manager = 0

            db_result = conn.execute(stmt_select_service, service=service).fetchone()

            # if already in the db: refresh in_googleapis and is_public values
            if db_result:
                current_in_googleapis = db_result[4]
                current_is_public = db_result[5]
                if (in_googleapis != current_in_googleapis) or (
                    in_service_manager != current_is_public
                ):
                    conn.execute(
                        stmt_update_public,
                        in_googleapis=in_googleapis,
                        in_service_manager=in_service_manager,
                        service=service,
                    )

            # if service is in service manager, but not the db: add it
            elif service in service_manager:
                service_config = service_manager_client.get(service)
                is_cloud = is_cloud_service(service_config)
                conn.execute(
                    stmt_insert_service,
                    service=service,
                    title=service_config.get("title"),
                    is_cloud=is_cloud,
                    in_googleapis=in_googleapis,
                    in_service_manager=in_service_manager,
                )
                print(
                    f"Inserted {service}: is_cloud:{is_cloud}, \
                        in_googleapis:{in_googleapis}, is_public:{in_service_manager})."
                )

            # service only exists in googleapis => assume private/allow-listed
            # set is_cloud to 0 (conservative)
            else:
                is_cloud = 0
                title = googleapis[service]["title"]
                conn.execute(
                    stmt_insert_service,
                    service=service,
                    title=title,
                    is_cloud=is_cloud,
                    in_googleapis=in_googleapis,
                    in_service_manager=in_service_manager,
                )
                print(
                    f"Inserted {service}: is_cloud:unknown(0), in_googleapis:{in_googleapis}, \
                        is_public:{in_service_manager})."
                )

        # iterate over all services in the database to check for deprecated services
        db_all = conn.execute(stmt_select_star).fetchall()
        for entry in db_all:
            service_name = entry[1]
            in_googleapis = entry[4]
            in_service_manager = entry[5]
            # service is in db but not in service manager, or googleapis
            if service_name not in all_services_set:
                if in_googleapis == 1 or in_service_manager == 1:
                    in_googleapis = 0
                    in_service_manager = 0
                    conn.execute(
                        stmt_update_public,
                        in_googleapis=in_googleapis,
                        in_service_manager=in_service_manager,
                        service=service_name,
                    )
                    print(
                        f"Toggled {service_name}: is_public -> 0; in_googleapis -> 0."
                    )

    print("Database update complete.")


def db_refresh_cloud_status():
    # get all services (Cloud + non-Cloud) from Service Manager
    service_manager = ServiceManagerClient()
    services_list = service_manager.list()

    # prepare SQL statement templates
    stmt_select_service = sqlalchemy.text(
        "SELECT * FROM services WHERE service_name=:service"
    )

    stmt_update_cloud = sqlalchemy.text(
        "UPDATE services SET is_cloud=:is_cloud WHERE service_name=:service"
    )

    db = init_connection_engine()
    with db.connect() as conn:
        for service in services_list:
            service_config = service_manager.get(service)
            is_cloud = is_cloud_service(service_config)
            db_result = conn.execute(stmt_select_service, service=service).fetchone()
            if db_result:
                current_cloud = db_result[3]
                if current_cloud != is_cloud:
                    conn.execute(stmt_update_cloud, is_cloud=is_cloud, service=service)
                    print(
                        f"Toggled {service} (is_cloud): {current_cloud} -> {is_cloud}."
                    )


# for local execution
if __name__ == "__main__":
    # mock event dict
    event = {}

    # mock google.cloud.functions.Context
    class Context:
        event_id = None
        timestamp = None

    context = Context()

    update_status_db(event, context)
