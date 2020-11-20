from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
class Category(models.Model):
    name = models.CharField(
        max_length=200,
        validators= [MinLengthValidator(3, 'Category name must be greater than two characters')]
        )

    def __str__(self):
        return self.name

class Remove(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, related_name='remove_category')
    item = models.ForeignKey('Item', on_delete=models.CASCADE, null=True, related_name='remove_item')
    

class Item(models.Model):
    name = models.CharField(
        max_length=200, 
        unique = True, 
        validators=[MinLengthValidator(2,'Item name must be greater than one character')])
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    quantity = models.PositiveIntegerField(null=True)
    total_price = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    picture = models.BinaryField(null=True, blank=True, editable=True)
    content_type = models.CharField(max_length=256, null=True, blank=True,
    help_text='The MIMEType of the file')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, related_name='item_category')

    def __str__(self):
        return self.name

class Comment(models.Model):
    text = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(3, "Comment must be greater than two characters")],
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comment_owner')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text[:11] + '...'