import requests
import datetime
from celery import shared_task

@shared_task
def generate_crm_report():
    """
    Generates a weekly CRM report and logs it to /tmp/crm_report_log.txt.
    The report includes:
    - Total number of customers
    - Total number of orders
    - Total revenue (sum of total_amount)
    """
    try:
        # GraphQL endpoint
        url = "http://localhost:8000/graphql"

        # GraphQL query
        query = """
        query {
            allCustomers {
                totalCount
            }
            allOrders {
                totalCount
                edges {
                    node {
                        totalAmount
                    }
                }
            }
        }
        """

        response = requests.post(url, json={"query": query})
        data = response.json().get("data", {})

        total_customers = data.get("allCustomers", {}).get("totalCount", 0)
        all_orders = data.get("allOrders", {})
        total_orders = all_orders.get("totalCount", 0)

        # Calculate total revenue
        total_revenue = 0
        if "edges" in all_orders:
            for edge in all_orders["edges"]:
                node = edge.get("node", {})
                total_revenue += node.get("totalAmount", 0)

        # Log report to file
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{now} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue\n"

        with open("/tmp/crm_report_log.txt", "a") as logfile:
            logfile.write(log_message)

        print("CRM weekly report generated successfully!")

    except Exception as e:
        with open("/tmp/crm_report_log.txt", "a") as logfile:
            logfile.write(f"Error generating report: {str(e)}\n")
        print(f"Error: {e}")
