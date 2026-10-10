from rest_framework.routers import DefaultRouter
from  .views import ShoeCompanyViewset,ShoeViewset,ShoeVariantViewset

router = DefaultRouter()
router.register(r'companies', ShoeCompanyViewset, )
router.register(r'shoes', ShoeViewset,)
router.register(r'variants', ShoeVariantViewset, )


urlpatterns = router.urls

