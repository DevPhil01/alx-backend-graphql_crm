from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime

# ----------------------------
# Cron Job: update_low_stock
# ----------------------------
def update_low_stock():
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=False,
        retries=3,
    )

    client = Client(transport=transport, fetch_schema_from_transport=False)

    mutation = gql("""
        mutation {
            updateLowStockProducts {
                message
                updatedProducts {
                    id
                    name
                    stock
                }
            }
        }
    """)

    try:
        result = client.execute(mutation)
        updates = result.get("updateLowStockProducts", {})
        updated_products = updates.get("updatedProducts", [])
        message = updates.get("message", "No message returned")

        with open("/tmp/low_stock_updates_log.txt", "a") as log:
            log.write(f"\n[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] {message}\n")
            for p in updated_products:
                log.write(f" - {p['name']} → Stock: {p['stock']}\n")

    except Exception as e:
        with open("/tmp/low_stock_updates_log.txt", "a") as log:
            log.write(f"\n[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] ERROR: {str(e)}\n")
