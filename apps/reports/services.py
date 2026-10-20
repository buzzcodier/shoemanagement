from datetime import datetime, time, timedelta
from decimal import Decimal

from django.conf import settings
from django.db.models import (
    Count, DecimalField, F, IntegerField, Q, Sum, Value,
)
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.sales.models import Sale, SaleItem
from apps.shoes.models import Shoe, ShoeVariant


PROFIT_EXPR = F("unit_price") - F("buying_price")


def _date_range(start=None, end=None):
    """
    Given two date objects (or None), return aware datetime bounds.
    Defaults: end = today, start = end - 29 days (30-day inclusive range).
    """
    today = timezone.localdate()

    end_date = end or today
    start_date = start or (end_date - timedelta(days=29))

    tz = timezone.get_current_timezone()
    start_dt = timezone.make_aware(datetime.combine(start_date, time.min), tz)
    end_dt = timezone.make_aware(
        datetime.combine(end_date, time.max), tz
    )
    return start_dt, end_dt


def dashboard_metrics():
    today = timezone.localdate()
    today_start, today_end = _date_range(today, today)

    today_sales = Sale.objects.filter(created_at__range=(today_start, today_end))
    today_total = today_sales.aggregate(
        total=Coalesce(Sum("total_amount"), Value(0, output_field=DecimalField()))
    )["total"]

    today_items = SaleItem.objects.filter(sale__in=today_sales)
    today_profit = today_items.aggregate(
        profit=Coalesce(
            Sum(PROFIT_EXPR * F("quantity"), output_field=DecimalField()),
            Value(0, output_field=DecimalField()),
        )
    )["profit"]

    today_count = today_sales.count()

    stock_value = ShoeVariant.objects.aggregate(
        value=Coalesce(
            Sum(F("quantity") * F("shoe__buying_price"), output_field=DecimalField()),
            Value(0, output_field=DecimalField()),
        )
    )["value"]

    threshold = settings.LOW_STOCK_THRESHOLD
    low_stock = (
        ShoeVariant.objects
        .select_related("shoe", "shoe__company")
        .filter(quantity__lt=threshold)
        .order_by("quantity")[:10]
    )

    low_stock_list = [
        {
            "variant_id": v.id,
            "shoe_id": v.shoe.id,
            "shoe_name": v.shoe.name,
            "company_name": v.shoe.company.name,
            "size": v.size,
            "quantity": v.quantity,
        }
        for v in low_stock
    ]

    recent_sales = (
        Sale.objects
        .select_related("cashier")
        .order_by("-created_at")[:10]
    )
    recent_list = [
        {
            "id": s.id,
            "cashier": s.cashier.username,
            "total_amount": str(s.total_amount),
            "payment_method": s.payment_method,
            "created_at": s.created_at,
            "item_count": s.items.count(),
        }
        for s in recent_sales
    ]

    # Top sellers last 7 days
    week_ago = timezone.localdate() - timedelta(days=6)
    week_start, week_end = _date_range(week_ago, timezone.localdate())
    top_week = (
        SaleItem.objects
        .filter(sale__created_at__range=(week_start, week_end))
        .values(
            shoe_id=F("shoe_variant__shoe__id"),
            shoe_name=F("shoe_variant__shoe__name"),
            company_name=F("shoe_variant__shoe__company__name"),
        )
        .annotate(
            qty=Sum("quantity"),
            revenue=Sum(F("unit_price") * F("quantity")),
        )
        .order_by("-qty")[:5]
    )
    top_week_list = [
        {
            "shoe_id": row["shoe_id"],
            "shoe_name": row["shoe_name"],
            "company_name": row["company_name"],
            "quantity": row["qty"],
            "revenue": str(row["revenue"]),
        }
        for row in top_week
    ]

    return {
        "today_sales_total": str(today_total),
        "today_profit": str(today_profit),
        "today_transaction_count": today_count,
        "stock_value": str(stock_value),
        "low_stock": low_stock_list,
        "recent_sales": recent_list,
        "top_sellers_week": top_week_list,
    }


def sales_summary(start=None, end=None):
    start_dt, end_dt = _date_range(start, end)
    sales = Sale.objects.filter(created_at__range=(start_dt, end_dt))

    total = sales.aggregate(
        t=Coalesce(Sum("total_amount"), Value(0, output_field=DecimalField()))
    )["t"]
    count = sales.count()

    items = SaleItem.objects.filter(sale__in=sales)
    units = items.aggregate(
        u=Coalesce(Sum("quantity"), Value(0, output_field=IntegerField()))
    )["u"]
    cost = items.aggregate(
        c=Coalesce(
            Sum(F("buying_price") * F("quantity"), output_field=DecimalField()),
            Value(0, output_field=DecimalField()),
        )
    )["c"]
    profit = items.aggregate(
        p=Coalesce(
            Sum(PROFIT_EXPR * F("quantity"), output_field=DecimalField()),
            Value(0, output_field=DecimalField()),
        )
    )["p"]

    return {
        "start": start_dt.date().isoformat(),
        "end": end_dt.date().isoformat(),
        "total_revenue": str(total),
        "total_cost": str(cost),
        "total_profit": str(profit),
        "transaction_count": count,
        "units_sold": units,
    }


def best_sellers(start=None, end=None, limit=10):
    start_dt, end_dt = _date_range(start, end)
    rows = (
        SaleItem.objects
        .filter(sale__created_at__range=(start_dt, end_dt))
        .values(
            shoe_id=F("shoe_variant__shoe__id"),
            shoe_name=F("shoe_variant__shoe__name"),
            company_name=F("shoe_variant__shoe__company__name"),
        )
        .annotate(
            qty=Sum("quantity"),
            revenue=Sum(F("unit_price") * F("quantity")),
        )
        .order_by("-qty")[:limit]
    )
    return [
        {
            "shoe_id": r["shoe_id"],
            "shoe_name": r["shoe_name"],
            "company_name": r["company_name"],
            "quantity": r["qty"],
            "revenue": str(r["revenue"]),
        }
        for r in rows
    ]


def best_sizes(start=None, end=None, limit=10):
    start_dt, end_dt = _date_range(start, end)
    rows = (
        SaleItem.objects
        .filter(sale__created_at__range=(start_dt, end_dt))
        .values(size=F("shoe_variant__size"))
        .annotate(qty=Sum("quantity"))
        .order_by("-qty")[:limit]
    )
    return [{"size": r["size"], "quantity": r["qty"]} for r in rows]


def by_cashier(start=None, end=None):
    start_dt, end_dt = _date_range(start, end)
    rows = (
        Sale.objects
        .filter(created_at__range=(start_dt, end_dt))
        .values(cashier=F("cashier__username"))
        .annotate(
            count=Count("id"),
            total=Coalesce(Sum("total_amount"), Value(0, output_field=DecimalField())),
        )
        .order_by("-total")
    )
    return [
        {"cashier": r["cashier"], "count": r["count"], "total": str(r["total"])}
        for r in rows
    ]


def by_payment(start=None, end=None):
    start_dt, end_dt = _date_range(start, end)
    rows = (
        Sale.objects
        .filter(created_at__range=(start_dt, end_dt))
        .values("payment_method")
        .annotate(
            count=Count("id"),
            total=Coalesce(Sum("total_amount"), Value(0, output_field=DecimalField())),
        )
        .order_by("-total")
    )
    return [
        {
            "payment_method": r["payment_method"],
            "count": r["count"],
            "total": str(r["total"]),
        }
        for r in rows
    ]


def stock_value():
    rows = (
        ShoeVariant.objects
        .select_related("shoe", "shoe__company", "shoe__category")
        .filter(quantity__gt=0)
    )
    total_pairs = 0
    total_cost = Decimal("0")
    total_retail = Decimal("0")

    for v in rows:
        total_pairs += v.quantity
        total_cost += v.quantity * v.shoe.buying_price
        price = v.selling_price if v.selling_price is not None else v.shoe.selling_price
        total_retail += v.quantity * price

    return {
        "total_pairs": total_pairs,
        "total_cost_value": str(total_cost),
        "total_retail_value": str(total_retail),
    }


def low_stock(limit=50):
    threshold = settings.LOW_STOCK_THRESHOLD
    rows = (
        ShoeVariant.objects
        .select_related("shoe", "shoe__company")
        .filter(quantity__lt=threshold)
        .order_by("quantity", "shoe__name", "size")[:limit]
    )
    return [
        {
            "variant_id": v.id,
            "shoe_id": v.shoe.id,
            "shoe_name": v.shoe.name,
            "company_name": v.shoe.company.name,
            "size": v.size,
            "quantity": v.quantity,
        }
        for v in rows
    ]