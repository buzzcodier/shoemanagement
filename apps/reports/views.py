from django.shortcuts import render

# Create your views here.
from datetime import datetime

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.accounts.permissions import IsManagerOrOwner
from . import services


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _parse_limit(request, default=10, max_limit=100):
    try:
        return max(1, min(int(request.query_params.get("limit", default)), max_limit))
    except (ValueError, TypeError):
        return default


@api_view(["GET"])
@permission_classes([IsManagerOrOwner])
def dashboard(request):
    return Response(services.dashboard_metrics())


@api_view(["GET"])
@permission_classes([IsManagerOrOwner])
def sales_summary(request):
    start = _parse_date(request.query_params.get("start"))
    end = _parse_date(request.query_params.get("end"))
    return Response(services.sales_summary(start, end))


@api_view(["GET"])
@permission_classes([IsManagerOrOwner])
def best_sellers_view(request):
    start = _parse_date(request.query_params.get("start"))
    end = _parse_date(request.query_params.get("end"))
    limit = _parse_limit(request)
    return Response(services.best_sellers(start, end, limit))


@api_view(["GET"])
@permission_classes([IsManagerOrOwner])
def best_sizes_view(request):
    start = _parse_date(request.query_params.get("start"))
    end = _parse_date(request.query_params.get("end"))
    limit = _parse_limit(request)
    return Response(services.best_sizes(start, end, limit))


@api_view(["GET"])
@permission_classes([IsManagerOrOwner])
def by_cashier_view(request):
    start = _parse_date(request.query_params.get("start"))
    end = _parse_date(request.query_params.get("end"))
    return Response(services.by_cashier(start, end))


@api_view(["GET"])
@permission_classes([IsManagerOrOwner])
def by_payment_view(request):
    start = _parse_date(request.query_params.get("start"))
    end = _parse_date(request.query_params.get("end"))
    return Response(services.by_payment(start, end))


@api_view(["GET"])
@permission_classes([IsManagerOrOwner])
def stock_value_view(request):
    return Response(services.stock_value())


@api_view(["GET"])
@permission_classes([IsManagerOrOwner])
def low_stock_view(request):
    limit = _parse_limit(request, default=50, max_limit=200)
    return Response(services.low_stock(limit))