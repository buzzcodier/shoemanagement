from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    shoe_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "description", "shoe_count"]

    def get_shoe_count(self, obj):
        return obj.shoes.count()