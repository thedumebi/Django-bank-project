from django import forms
from django.forms import ModelForm, FileField
from .models import Item, Comment, Category, Remove
from .humanize import naturalsize
from django.core.files.uploadedfile import InMemoryUploadedFile


class FileForm(forms.Form):
    file = forms.FileField(required=True, label='Upload Database File')

    """def save(self, commit=True):
        instance = super(FileForm, self).save(commit=False)
        file = instance.file
        if isinstance(file, InMemoryUploadedFile):
            bytearr = file.read()
            instance.content_type = file.content_type
            instance.file = bytearr
        if commit:
            instance.save()
        return instance"""


class PictureForm(ModelForm):
    max_upload_limit = 2*1024*1024
    max_upload_limit_text = naturalsize(max_upload_limit)
    picture = FileField(required=False, label='Upload Item Picture '+max_upload_limit_text)
    upload_file_name = 'picture'

    class Meta:
        model = Item
        fields = ['name', 'price', 'quantity', 'picture', 'category']
        labels = {'name': 'Item name', 'price':'Item price(NGN)', 'category':'Item category'}

    def clean(self):
        cleaned_data = super().clean()
        pic = cleaned_data.get('picture')
        if pic is None:
            return
        if len(pic) > self.max_upload_limit:
            self.add_error('picture', 'picture must be <'+self.max_upload_limit_text+'bytes')

    def save(self, commit=True):
        instance = super(PictureForm, self).save(commit=False)
        pic = instance.picture
        if isinstance(pic, InMemoryUploadedFile):
            bytearr = pic.read()
            instance.content_type = pic.content_type
            instance.picture = bytearr
        if commit:
            instance.save()
        return instance

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': 'comment'}

class RemoveForm(ModelForm):
    class Meta:
        model = Remove
        fields = ['category', 'item']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item'].queryset = Item.objects.none()
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['item'].queryset = Item.objects.filter(category_id = category_id).order_by('name')
            except (ValueError, TypeError):
                pass
        #elif self.instance.pk:
            #self.fields['item'].queryset = self.instance.category.item_set.order_by('name')
class QuantityForm(ModelForm):
    class Meta:
        model = Item
        fields = ['quantity']
