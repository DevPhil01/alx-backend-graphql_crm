#!/bin/bash
# Script: clean_inactive_customers.sh
# Description: Deletes customers with no orders for over a year and logs the result.

PROJECT_DIR="$(dirname "$(realpath "$0")")/../.."

cd "$PROJECT_DIR" || exit

DELETED_COUNT=$(python3 manage.py shell <<EOF
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer

cutoff_date = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(order__isnull=True) | Customer.objects.exclude(order__date__gte=cutoff_date)
deleted_count, _ = inactive_customers.distinct().delete()
print(deleted_count)
EOF
)

echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt

