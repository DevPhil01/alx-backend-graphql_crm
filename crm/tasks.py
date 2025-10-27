from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime
import os

@shared_task
def generate_crm_report():
    """
    Generates a weekly CRM report using GraphQL and logs it to /tmp/crm_report_log.txt.
    """
    try:
        # Define GraphQL transport
        transport = RequestsHTTPTransport(
            url='http://localhost:8000/graphql/',
            use_json=True,
        )

        # Create client
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # GraphQL query to fetch customers, orders, and revenue
        query = gql("""
        {
            allCustomers {
                id
            }
            allOrders {
                id
                totalAmount
            }
        }
        """)

        # Execute query
        result = client.execute(query)

        total_customers = len(result.get("allCustomers", []))
        orders = result.get("allOrders", [])
        total_orders = len(orders)
        total_revenue = sum(order.get("totalAmount", 0) for order in orders)

        # Prepare log message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = (
            f"{timestamp} - Report: {total_customers} customers, "
            f"{total_orders} orders, {total_revenue} total revenue\n"
        )

        # Ensure /tmp directory exists and log to file
        log_path = "/tmp/crm_report_log.txt"
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        with open(log_path, "a") as log_file:
            log_file.write(log_message)

        print("CRM weekly report generated successfully.")

    except Exception as e:
        error_message = f"Error generating CRM report: {str(e)}\n"
        with open("/tmp/crm_report_log.txt", "a") as log_file:
            log_file.write(error_message)
        print(error_message)
