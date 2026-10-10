from django.shortcuts import render
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import SearchFilter, OrderingFilter
from .models import ShoeCompany,ShoeVariant,Shoe
from .serializers import  ShoeCompanySerializer,ShoeSerializer,ShoeVariantSerializer

from .filters import ShoeFilter,ShoeVariantFilter
from  apps.accounts.permissions import IsManagerOrOwner





# Create your views here.

class ShoeCompanyViewset(viewsets.ModelViewSet):
    queryset = ShoeCompany.objects.all()
    serializer_class = ShoeCompanySerializer
    permission_classes = [IsManagerOrOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'contact_person', 'phone', 'email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ShoeViewset(viewsets.ModelViewSet):
    queryset = (
        Shoe.objects.select_related('category', 'company').prefetch_related('variants')
    )
    serializer_class = ShoeSerializer
    permission_classes = [IsManagerOrOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ShoeFilter
    search_fields = ['name', 'model_number' , 'description']
    ordering_fields = ['name', 'selling_price','buying_price', 'created_at']



class ShoeVariantViewset(viewsets.ModelViewSet):
    queryset = ShoeVariant.objects.select_related('shoe')
    serializer_class = ShoeVariantSerializer
    permission_classes = [IsManagerOrOwner]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ShoeVariantFilter
    ordering_fields = ['size', 'quantity',]


    

