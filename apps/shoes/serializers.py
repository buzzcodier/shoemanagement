from rest_framework import serializers
from .models import Shoe,ShoeCompany,ShoeVariant


class ShoeCompanySerializer(serializers.ModelSerializer):
    shoe_count = serializers.IntegerField(source="shoes.count", read_only=True)

    class Meta:
        model  = ShoeCompany
        fields = ['id','name','contact_person','phone','email','address','created_at','shoe_count']
        read_only_fields = ['created_at']



class ShoeVariantSerializer(serializers.ModelSerializer):
    effective_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    
    class Meta:
        model  = ShoeVariant
        fields = ['id','shoe','size','quantity','selling_price','effective_price','created_at']




class ShoeSerializer(serializers.ModelSerializer):
    variants = ShoeVariantSerializer(many=True, read_only=True)
    category_name =serializers.CharField(source='category.name', read_only=True)
    company_name =serializers.CharField(source='company.name', read_only=True)
    total_stock = serializers.IntegerField( read_only=True)


    class Meta:
        model =Shoe

        fields = ['id','name','model_number','category','category_name','company','company_name','material','gender','description','buying_price','selling_price','image','active','created_at','updated_at','variants','total_stock']
        read_only_fields = ['created_at','updated_at']

