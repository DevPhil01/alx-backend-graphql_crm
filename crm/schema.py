import re
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db import transaction
from django.utils import timezone
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter


# ----------------------------
# GraphQL Types
# ----------------------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock", "created_at")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "product", "total_amount", "order_date", "created_at")


# ----------------------------
# Mutations
# ----------------------------
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists")

        if phone and not re.match(r"^(\+?\d{1,3}[- ]?)?\d{3,15}$", phone):
            raise Exception("Invalid phone number format")

        customer = Customer.objects.create(name=name, email=email, phone=phone)
        return CreateCustomer(customer=customer, message="Customer created successfully.")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(graphene.JSONString, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        customers = []
        errors = []
        for data in input:
            name = data.get("name")
            email = data.get("email")
            phone = data.get("phone")

            if not name or not email:
                errors.append(f"Missing required fields for {data}")
                continue
            if Customer.objects.filter(email=email).exists():
                errors.append(f"Email already exists: {email}")
                continue
            if phone and not re.match(r"^(\+?\d{1,3}[- ]?)?\d{3,15}$", phone):
                errors.append(f"Invalid phone format for {email}")
                continue

            customer = Customer.objects.create(name=name, email=email, phone=phone)
            customers.append(customer)

        return BulkCreateCustomers(customers=customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False, default_value=0)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock):
        if price <= 0:
            raise Exception("Price must be positive")
        if stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime(required=False)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        products = Product.objects.filter(pk__in=product_ids)
        if not products.exists():
            raise Exception("Invalid product IDs")

        total_amount = sum(p.price for p in products)
        order_date = order_date or timezone.now()

        order = Order.objects.create(customer=customer, total_amount=total_amount, order_date=order_date)
        order.product.set(products)

        return CreateOrder(order=order)


# ----------------------------
# Query (with Filters)
# ----------------------------
class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

    def resolve_all_customers(self, info, **kwargs):
        return Customer.objects.all()

    def resolve_all_products(self, info, **kwargs):
        return Product.objects.all()

    def resolve_all_orders(self, info, **kwargs):
        return Order.objects.all()


# ----------------------------
# Mutation Root
# ----------------------------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
