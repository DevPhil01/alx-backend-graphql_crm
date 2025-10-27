import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """
    Logs a timestamped heartbeat message every 5 minutes and verifies
    the CRM GraphQL endpoint is responsive.
    """
    log_file = "/tmp/crm_heartbeat_log.txt"
    now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{now} CRM is alive"

    try:
        # Configure GraphQL transport
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=False,
            retries=3,
        )

        # Create the GraphQL client
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # Define the GraphQL query
        query = gql("{ hello }")

        # Execute the query
        result = client.execute(query)
        hello_response = result.get("hello", "")

        message += f" | GraphQL says: {hello_response}"

    except Exception as e:
        message += f" | GraphQL query failed: {e}"

    # Append the log message to /tmp/crm_heartbeat_log.txt
    with open(log_file, "a") as f:
        f.write(message + "\n")

    print(message)
