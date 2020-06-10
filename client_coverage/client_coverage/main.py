import sqlalchemy

from database import init_connection_engine
from googleapis import get_published_protos
from service_manager import ServiceManagerClient
from utils import is_cloud_service


def update_status_db(event, context):

    print(
        f"Successfully triggered by {context.event_id} published at {context.timestamp}."
    )

    # get all services (Cloud + non-Cloud) from Service Manager
    service_manager = ServiceManagerClient()
    services = service_manager.list()

    # get all services with protos in github/googleapis/googleapis
    protos = get_published_protos()

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
            :is_public)"
    )

    stmt_select_star = sqlalchemy.text("SELECT * FROM services")

    # initiate database connection
    db = init_connection_engine()

    with db.connect() as conn:
        # iterate over public services list
        for service in services:

            # check if protos published to googleapis
            if service in protos:
                in_googleapis = 1

            # check if already in db
            db_result = conn.execute(stmt_select_service, service=service).fetchone()
            if db_result:

                # if service in db and is_public is False, update
                if db_result[5] == 0:
                    conn.execute(
                        stmt_update_public,
                        in_googleapis=in_googleapis,
                        is_public=1,
                        service=service,
                    )
                    print(f"Toggled {service}: is_public -> 1.")

            # if service not in db, insert it
            else:
                service_config = service_manager.get(service)
                is_cloud = is_cloud_service(service_config)
                conn.execute(
                    stmt_insert_service,
                    service=service,
                    title=service_config.get("title"),
                    is_cloud=is_cloud,
                    in_googleapis=in_googleapis,
                    is_public=1,
                )
                print(
                    f"Inserted {service}: is_cloud:{is_cloud}, \
                    in_googleapis:{in_googleapis}, is_public:1)."
                )

        # iterate over all services in the database to check for deprecated services
        db_services = conn.execute(stmt_select_star).fetchall()
        for entry in db_services:
            service_name = entry[1]
            is_public = entry[5]

            # if service is not in public list and is_public is True, update
            if (service_name not in services) and (is_public == 1):
                if service_name in protos:
                    in_googleapis = 1
                else:
                    in_googleapis = 0
                conn.execute(
                    stmt_update_public,
                    in_googleapis=in_googleapis,
                    is_public=0,
                    service=service_name,
                )
                print(f"Toggled {service_name}: is_public -> 0.")

    print("Database update complete.")


# for local execution
if __name__ == "__main__":
    # mock google.cloud.functions.Context
    class Context:
        event_id = None
        timestamp = None

    context = Context()

    # mock event dict
    event = {}

    update_status_db(event, context)
