
from django_filters import rest_framework as filters
import django_filters


from .models import Shoe, ShoeVariant


class ShoeFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="selling_price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="selling_price", lookup_expr='lte')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')

    class Meta:
        model =Shoe
        fields = ['category','company','gender','active']

        def filter_in_stock(self, queryset, name, value):
            if value:
                return queryset.filter(variants__quantity__gt=0).distinct()
            return queryset



class ShoeVariantFilter(django_filters.FilterSet):
    class Meta:
        model =ShoeVariant
        fields = ['shoe','size']




    

    