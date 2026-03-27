from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Sub-Categories
    path('subcategories/', views.subcategory_list, name='subcategory_list'),
    path('subcategories/create/', views.subcategory_create, name='subcategory_create'),
    path('subcategories/<int:pk>/edit/', views.subcategory_edit, name='subcategory_edit'),
    path('subcategories/<int:pk>/delete/', views.subcategory_delete, name='subcategory_delete'),

    # AJAX
    path('api/subcategories/', views.ajax_subcategories, name='ajax_subcategories'),

    # Books
    path('books/', views.book_list, name='book_list'),
    path('books/create/', views.book_create, name='book_create'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/<int:pk>/edit/', views.book_edit, name='book_edit'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),

    # Issue / Return
    path('books/<int:book_pk>/issue/', views.issue_book, name='issue_book'),
    path('issues/', views.issue_list, name='issue_list'),
    path('issues/<int:issue_pk>/return/', views.return_book, name='return_book'),

    # Fines
    path('fines/', views.fine_list, name='fine_list'),
    path('fines/<int:pk>/pay/', views.fine_pay, name='fine_pay'),
]
