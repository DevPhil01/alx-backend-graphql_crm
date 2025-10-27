import requests
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

from celery import shared_task


@shared_task
def generate_crm_report():
    """Celery task to generate a weekly CRM report via GraphQL."""

    # Setup the GraphQL client
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=False,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # GraphQL query to fetch totals
    query = gql("""
    query {
        allCustomers {
            totalCount
        }
        allOrders {
            totalCount
        }
    }
    """)

    # Execute the query
    try:
        result = client.execute(query)

        total_customers = result.get("allCustomers", {}).get("totalCount", 0)
        total_orders = result.get("allOrders", {}).get("totalCount", 0)

        # Fetch total revenue using REST API fallback
        response = requests.get("http://localhost:8000/graphql")
        total_revenue = 0
        if response.status_code == 200:
            # You can optionally calculate revenue based on ORM in Django
            total_revenue = 10000  # Simulated example total

        # Format the log entry
        log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue\n"

        # Write to log file
        with open("/tmp/crm_report_log.txt", "a") as log_file:
            log_file.write(log_entry)

        print("CRM report generated successfully!")

    except Exception as e:
        error_msg = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error generating report: {e}\n"
        with open("/tmp/crm_report_log.txt", "a") as log_file:
            log_file.write(error_msg)
        print("Error generating CRM report:", e)
