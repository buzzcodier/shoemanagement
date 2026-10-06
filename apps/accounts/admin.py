from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import User

admin.register(User)

class CustomUserAdmin(UserAdmin):
    list_display =('username','email','is_active','is_staff','role')
    list_filter = ('role','is_active','is_staff')
    fieldsets = UserAdmin.fieldsets + (("Shop", {'fields' : ("role","phone")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Shop", {'fields' : ("role","phone")}),)
    
