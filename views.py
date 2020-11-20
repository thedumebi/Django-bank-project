import csv
from io import StringIO
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models import Q
from django.db import connection

from .models import Category, Item, Comment, Remove
from .owner import OwnerCreateView, OwnerUpdateView, OwnerDeleteView, OwnerListView, OwnerDetailView
from .utils import dump_queries
from .forms import PictureForm, CommentForm, RemoveForm, QuantityForm, FileForm

# Create your views here.
class HomeView(View):
    template_name = 'bank/home_view.html'
    def get(self, request):
        return render(request, self.template_name)

class CategoryListView(ListView):
    template_name = 'bank/category_list.html'
    model = Category
    fields = ['name']

class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Item
    template_name = 'bank/category_detail.html'
    def get(self, request, pk):
        category = Category.objects.get(id=pk)
        item_list = Item.objects.all()
        ctx = {'category': category, 'item_list':item_list}
        return render(request, self.template_name, ctx)

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    fields = ['name']
    success_url = reverse_lazy('bank:category_list')

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    fields = ['name']
    success_url = reverse_lazy('bank:category_list')

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    fields = ['name']
    success_url = reverse_lazy('bank:category_list')

class ItemListView(LoginRequiredMixin, ListView):
    template_name = 'bank/item_list.html'
    def get(self, request):
        strval =  request.GET.get("search", False)
        if strval :
            query = Q(name__contains=strval)
            #query.add(Q(text__contains=strval), Q.OR)
            item_list = Item.objects.filter(query).select_related().order_by('-updated_at')[:10]
            item_dict = dict()
            for item in item_list:
                kv = {item.category.name: item.category.id}
                item_dict.update(kv)
        else:
            item_list = Item.objects.all().order_by('-updated_at')
            item_dict = dict()
            for item in item_list:
                print(item.category.name)
                kv = {item.category.name: item.category.id}
                item_dict.update(kv)
        for item in item_list:
            item.natural_updated = naturaltime(item.updated_at)
        ctx = {'item_list':item_list , 'item_dict':item_dict}
        dump_queries()
        return render(request, self.template_name, ctx)

class ItemAddView(LoginRequiredMixin, UpdateView):
    template_name = 'bank/item_remove.html'
    success_url = reverse_lazy('bank:item_list')
    def get(self, request, pk):
        item = get_object_or_404(Item, id = pk)
        form = RemoveForm(instance=item)
        q_form = QuantityForm()
        ctx = {'form': form, 'q_form':q_form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk):
        item = get_object_or_404(Item, id = pk)
        form = RemoveForm(instance=item)
        q_form = QuantityForm()
        x = int(request.POST['quantity'])
        y = request.POST['item']
        if int(pk) != int(y):
            error_message = 'you selected the wrong item!'
            ctx = {'form': form, 'q_form': q_form, 'error_message': error_message}
            return render(request, self.template_name, ctx)
        item = get_object_or_404(Item, pk = pk)
        item_qty = item.quantity
        if q_form.is_valid():
            ctx = {'form': form, 'q_form': q_form}
            return render(request, self.template_name, ctx)
        item.quantity = item_qty + x
        item.total_price = int(item.price) * int(item.quantity)
        item.save()

        return redirect(self.success_url)

class ItemRemoveView(LoginRequiredMixin, UpdateView):
    template_name = 'bank/item_remove.html'
    success_url = reverse_lazy('bank:item_list')
    def get(self, request, pk):
        item = get_object_or_404(Item, id = pk)
        form = RemoveForm(instance=item)
        q_form = QuantityForm()
        ctx = {'form': form, 'q_form':q_form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk):
        item = get_object_or_404(Item, id = pk)
        form = RemoveForm(instance=item)
        q_form = QuantityForm()
        x = int(request.POST['quantity'])
        y = request.POST['item']
        if int(pk) != int(y):
            error_message = 'you selected the wrong item!'
            ctx = {'form': form, 'q_form': q_form, 'error_message': error_message}
            return render(request, self.template_name, ctx)
        item = get_object_or_404(Item, pk = pk)
        item_qty = item.quantity
        if x > item_qty:
            error_message = 'cannot take more than what is in stock, you have '+str(item_qty)+' left'
            ctx = {'form': form, 'q_form': q_form, 'error_message': error_message}
            return render(request, self.template_name, ctx)
        item.quantity = item_qty - x
        item.total_price = int(item.price) * int(item.quantity)
        item.save()

        return redirect(self.success_url)


def load_items(request):
     category_id = request.GET.get('category')
     items = Item.objects.filter(category_id=category_id).order_by('name')
     ctx = {'items': items}
     return render(request, 'bank/item_dropdown_list_options.html', ctx)

class ItemDetailView(LoginRequiredMixin, DetailView):
    model = Item
    template_name = 'bank/item_detail.html'
    def get(self, request, pk):
        item = Item.objects.get(id=pk)
        comments = Comment.objects.filter(item = item).order_by('-updated_at')
        comment_item = CommentForm()
        ctx = {'item': item, 'comments': comments, 'comment_item': comment_item}
        return render(request, self.template_name, ctx)

class ItemCreateView(LoginRequiredMixin, CreateView):
    template_name = 'bank/item_form.html'
    success_url = reverse_lazy('bank:item_list')
    def get(self, request):
        form = PictureForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request):
        form = PictureForm(request.POST, request.FILES or None)
        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)
        item = form.save(commit=False)
        item.total_price = int(item.price) * int(item.quantity)
        x= request.POST['category']
        item.save()
        category = Category.objects.get(id = x)
        r = Remove(category=category, item = item)
        r.save()
        return redirect(self.success_url)

class ItemFileCreateView(LoginRequiredMixin, CreateView):
    template_name = 'bank/item_create_file.html'
    success_url = reverse_lazy('bank:item_list')
    failure_url = 'bank/item_create_file_fail.html'
    def get(self, request):
        form = FileForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request):
        item_list = Item.objects.all()
        fhand = request.FILES['file']
        try:
            file_data = fhand.read().decode('UTF-8')
            reader = csv.reader(StringIO(file_data))
            next(reader)
        except:
            form = FileForm()
            ctx = {'form': form}
            return HttpResponse(render(request, self.failure_url, ctx))

        if item_list:
            for row in reader:
                if Item.objects.filter(name=row[1]).exists() == False:
                    name=row[1]
                    item_name = name
                    quantity=row[2]
                    price=row[3]
                    total_price=int(price) * int(quantity)

                    try:
                        quantity = int(row[2])
                    except:
                        quantity = None

                    try:
                        price = int(row[3])
                    except:
                        price = None

                    try:
                        total_price = int(price) * int(quantity)
                    except:
                        total_price = None
                    category, created = Category.objects.get_or_create(name=row[5])

                    item = Item(name = item_name, price = price, quantity = quantity, total_price = total_price, category = category)
                    item.save()
                for item in item_list:
                    if row[1] == item.name:
                        item_a = Item.objects.get(name=row[1])
                        item_a.quantity = item.quantity + int(row[2])
                        item_a.price = int(row[3])
                        item_a.total_price = item_a.price * item_a.quantity
                        item_a.save()
                    else:
                        continue
        else :
            for row in reader:
                name=row[1]
                item_name = name
                quantity=row[2]
                price=row[3]
                total_price=int(price) * int(quantity)

                try:
                    quantity = int(row[2])
                except:
                    quantity = None

                try:
                    price = int(row[3])
                except:
                    price = None

                try:
                    total_price = total_price = int(price) * int(quantity)
                except:
                    total_price = None
                category, created = Category.objects.get_or_create(name=row[5])

                item = Item(name = item_name, price = price, quantity = quantity, total_price = total_price, category = category)
                item.save()
        return redirect(self.success_url)


class ItemUpdateView(OwnerUpdateView):
    template_name = 'bank/item_form.html'
    success_url = reverse_lazy('bank:item_list')
    def get(self, request, pk):
        item = get_object_or_404(Item, id = pk)
        form = PictureForm(instance=item)
        form.fields['quantity'].widget.attrs['readonly'] = True
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk):
        item = get_object_or_404(Item, id=pk)
        form = PictureForm(request.POST, request.FILES or None, instance = item)
        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)
        x = form.save(commit=False)
        x.total_price = int(x.price)*int(x.quantity)
        x.save()
        return redirect(self.success_url)

class ItemDeleteView(LoginRequiredMixin, DeleteView):
    model = Item
    template_name = 'bank/item_delete.html'
    success_url = reverse_lazy('bank:item_list')

class CommentCreate(LoginRequiredMixin, View):
    template_name = 'bank/item_detail.html'
    def post(self, request, pk):
        item = get_object_or_404(Item, id = pk)
        comments = Comment.objects.filter(item=item).order_by('-updated_at')
        comment_item = CommentForm(request.POST)
        if not comment_item.is_valid():
            ctx = {'item': item, 'comments': comments, 'comment_item': comment_item}
            return render(request, self.template_name, ctx)
        comment = comment_item.save(commit = False)
        comment.user = self.request.user
        comment.item = item
        comment.save()
        return redirect(reverse_lazy('bank:item_detail', args = [pk]))

class CommentEdit(LoginRequiredMixin, View):
    template_name = 'bank/comment_edit.html'
    success_url = reverse_lazy('bank:item_detail')
    def get(self, request, pk):
        comm = get_object_or_404(Comment, id=pk, user = self.request.user)
        comment_item = CommentForm(instance=comm)
        item_id = comm.item.id
        item = get_object_or_404(Item, id = item_id)
        comments = Comment.objects.filter(item=item).order_by('-updated_at')
        ctx = {'comment_item': comment_item, 'comment':comm, 'item_id':item_id, 'item':item, 'comments':comments}
        return render(request, self.template_name, ctx)


    def post(self, request, pk):
        comm = get_object_or_404(Comment, id = pk)
        item_id = comm.item.id
        item = get_object_or_404(Item, id=item_id)
        comments = Comment.objects.filter(item=item).order_by('-updated_at')
        comment_item = CommentForm(request.POST)
        if not comment_item.is_valid():
            ctx = {'comment_item': comment_item, 'comment':comm, 'item_id':item_id, 'item':item, 'comments':comments}
            return render(request, self.template_name, ctx)
        comm.text = request.POST['text']
        comm.save()
        return redirect(reverse_lazy('bank:item_detail', args = [item_id]))



class CommentDelete(OwnerDeleteView):
    model = Comment
    template_name = "bank/comment_delete.html"

    def get_success_url(self):
        item= self.object.item
        return reverse_lazy('bank:item_detail', args=[item.id])

def picture_file(request, pk):
    item = get_object_or_404(Item, id = pk)
    response = HttpResponse()
    response['Content-Type'] = item.content_type
    response['Content-Length'] = len(item.picture)
    response.write(item.picture)
    return response
