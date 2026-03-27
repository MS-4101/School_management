from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('items/', views.CommodityListView.as_view(), name='commodity_list'),
    path('items/create/', views.CommodityCreateView.as_view(), name='commodity_create'),
    path('items/<int:pk>/', views.CommodityDetailView.as_view(), name='commodity_detail'),
    path('items/<int:pk>/update/', views.CommodityUpdateView.as_view(), name='commodity_update'),
    path('items/<int:pk>/delete/', views.CommodityDeleteView.as_view(), name='commodity_delete'),
    path('categories/', views.CategoryListView.as_view(), name='inv_category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='inv_category_create'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='inv_category_update'),
    path('transactions/add/', views.StockTransactionCreateView.as_view(), name='transaction_create'),
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/create/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/update/', views.SupplierUpdateView.as_view(), name='supplier_update'),
    path('po/', views.PurchaseOrderListView.as_view(), name='po_list'),
    path('po/<int:pk>/', views.PurchaseOrderDetailView.as_view(), name='po_detail'),
    path('po/<int:pk>/receive/', views.PurchaseOrderReceiveView.as_view(), name='po_receive'),
]
