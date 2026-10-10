from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.filters import SearchFilter,OrderingFilter
from .models import Category
from .serializers import CategorySerializer
from apps.accounts.permissions import IsManagerOrOwner
# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class=CategorySerializer
    permission_classes = [IsManagerOrOwner]
    filter_backends = [SearchFilter,OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name',]

    
