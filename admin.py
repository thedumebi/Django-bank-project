from django.contrib import admin
from .models import Category, Comment, Item

# Register your models here.
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Item)