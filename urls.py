from django.urls import path
from . import views

app_name = 'bank'
urlpatterns = [
    path('', views.HomeView.as_view(), name = 'all'),
    path('category', views.CategoryListView.as_view(), name = 'category_list'),
    path('category/<int:pk>/detail', views.CategoryDetailView.as_view(), name = 'category_detail'),
    path('category/create', views.CategoryCreateView.as_view(), name = 'category_create'),
    path('category/<int:pk>/update', views.CategoryUpdateView.as_view(), name = 'category_update'),
    path('category/<int:pk>/delete', views.CategoryDeleteView.as_view(), name = 'category_delete'),
    path('item', views.ItemListView.as_view(), name = 'item_list'),
    path('item/create', views.ItemCreateView.as_view(), name = 'item_create'),
    path('item/create/file', views.ItemFileCreateView.as_view(), name = 'item_create_file'),
    path('item/<int:pk>/remove', views.ItemRemoveView.as_view(), name = 'item_remove'),
    path('item/<int:pk>/add', views.ItemAddView.as_view(), name = 'item_add'),
    path('item/<int:pk>/detail', views.ItemDetailView.as_view(), name = 'item_detail'),
    path('item/<int:pk>/update', views.ItemUpdateView.as_view(), name = 'item_update'),
    path('item/<int:pk>/delete', views.ItemDeleteView.as_view(), name = 'item_delete'),
    path('item/<int:pk>/comment', views.CommentCreate.as_view(), name = 'item_comment'),
    path('item/<int:pk>/comment/edit', views.CommentEdit.as_view(), name = 'item_comment_edit'),
    path('item/<int:pk>/comment/delete', views.CommentDelete.as_view(), name = 'item_comment_delete'),
    path('item/<int:pk>/picture', views.picture_file, name = 'item_picture'),
    path('ajax/load-item/', views.load_items, name = 'ajax_load_items',),
]
