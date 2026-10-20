from rest_framework.routers import DefaultRouter

from .views import PackTemplateViewSet, PurchaseViewSet, SupplierViewSet

router = DefaultRouter()
router.register("suppliers", SupplierViewSet)
router.register("pack-templates", PackTemplateViewSet)
router.register("", PurchaseViewSet, basename="purchase")

urlpatterns = router.urls