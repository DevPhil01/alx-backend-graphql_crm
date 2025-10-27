#!/usr/bin/env python3
"""
Script: send_order_reminders.py
Description: Queries recent pending orders via GraphQL and logs reminders.
"""

from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import sys

def main():
    try:
        # Define the GraphQL endpoint
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=False,
            retries=3,
        )

        client = Client(transport=transport, fetch_schema_from_transport=False)

        # Calculate the date 7 days ago
        week_ago = (datetime.now() - timedelta(days=7)).date().isoformat()

        # GraphQL query
        query = gql(f"""
        query {{
          orders(orderDate_Gte: "{week_ago}") {{
            id
            customer {{
              email
            }}
          }}
        }}
        """)

        # Execute query
        result = client.execute(query)
        orders = result.get("orders", [])

        # Log file path
        log_path = "/tmp/order_reminders_log.txt"

        # Write logs
        with open(log_path, "a") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for order in orders:
                order_id = order.get("id")
                customer_email = order.get("customer", {}).get("email", "N/A")
                log_file.write(f"{timestamp} - Order ID: {order_id}, Customer Email: {customer_email}\n")

        print("Order reminders processed!")

    except Exception as e:
        print(f"Error processing order reminders: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
