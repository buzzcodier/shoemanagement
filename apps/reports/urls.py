from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="reports-dashboard"),
    path("sales-summary/", views.sales_summary, name="reports-sales-summary"),
    path("best-sellers/", views.best_sellers_view, name="reports-best-sellers"),
    path("best-sizes/", views.best_sizes_view, name="reports-best-sizes"),
    path("by-cashier/", views.by_cashier_view, name="reports-by-cashier"),
    path("by-payment/", views.by_payment_view, name="reports-by-payment"),
    path("stock-value/", views.stock_value_view, name="reports-stock-value"),
    path("low-stock/", views.low_stock_view, name="reports-low-stock"),
]