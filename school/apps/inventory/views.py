from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q, Sum
from .models import Commodity, Category, StockTransaction, Supplier, PurchaseOrder, PurchaseOrderItem
from django.urls import reverse_lazy
from django.contrib import messages
from apps.accounts.decorators import SectionRequiredMixin

from apps.library_mgmt.models import Book, BookIssue, BookCopy
from apps.lab_mgmt.models import Equipment, LabBooking, LabUnit


class DashboardView(SectionRequiredMixin, TemplateView):
    section_codename = 'inventory'
    template_name = 'inventory/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        low_stock_items = Commodity.objects.filter(current_stock__lte=F('low_stock_threshold'))
        context['low_stock_items'] = low_stock_items
        context['total_items'] = Commodity.objects.count()
        context['recent_transactions'] = StockTransaction.objects.all().select_related('commodity')[:10]

        total_books = Book.objects.count()
        books_issued = BookIssue.objects.filter(status='issued').count()
        context['total_books'] = total_books
        context['books_issued'] = books_issued
        context['total_equipment'] = Equipment.objects.count()
        context['equipment_available'] = Equipment.objects.filter(status='available').count()
        context['pending_bookings'] = LabBooking.objects.filter(status='pending').count()
        context['issue_percentage'] = (books_issued * 100 / total_books) if total_books > 0 else 0

        for item in low_stock_items:
            if item.low_stock_threshold > 0:
                item.stock_progress = min(100, (item.current_stock * 100 / item.low_stock_threshold))
            else:
                item.stock_progress = 0

        context['pending_pos'] = PurchaseOrder.objects.filter(status__in=['draft', 'ordered', 'partial']).count()
        context['received_pos'] = PurchaseOrder.objects.filter(status='received').count()
        context['total_po_value'] = PurchaseOrder.objects.exclude(status='cancelled').aggregate(
            total=Sum('grand_total'))['total'] or 0
        context['recent_pos'] = PurchaseOrder.objects.all().select_related('supplier').order_by('-order_date')[:5]
        context['total_suppliers'] = Supplier.objects.count()
        context['total_book_copies'] = BookCopy.objects.count()
        context['total_lab_units'] = LabUnit.objects.count()
        maintenance_books = BookCopy.objects.filter(status='maintenance').count()
        maintenance_lab = LabUnit.objects.filter(status='maintenance').count()
        context['total_maintenance'] = maintenance_books + maintenance_lab
        return context


class CommodityListView(SectionRequiredMixin, ListView):
    section_codename = 'inventory.items'
    model = Commodity
    template_name = 'inventory/commodity_list.html'
    context_object_name = 'commodities'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        category_id = self.request.GET.get('category')
        source = self.request.GET.get('source')
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if source:
            queryset = queryset.filter(source_type=source)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class CommodityDetailView(SectionRequiredMixin, DetailView):
    section_codename = 'inventory.items'
    model = Commodity
    template_name = 'inventory/commodity_detail.html'
    context_object_name = 'commodity'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transactions'] = self.object.transactions.all().select_related('user')
        return context


class CommodityCreateView(SectionRequiredMixin, CreateView):
    section_codename = 'inventory.items'
    required_level = 'full'
    model = Commodity
    fields = ['name', 'category', 'description', 'unit', 'low_stock_threshold', 'image', 'source_type']
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('inventory:commodity_list')

    def form_valid(self, form):
        messages.success(self.request, "Commodity created successfully.")
        return super().form_valid(form)


class CommodityUpdateView(SectionRequiredMixin, UpdateView):
    section_codename = 'inventory.items'
    required_level = 'full'
    model = Commodity
    fields = ['name', 'category', 'description', 'unit', 'low_stock_threshold', 'image', 'source_type']
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('inventory:commodity_list')

    def form_valid(self, form):
        messages.success(self.request, "Commodity updated successfully.")
        return super().form_valid(form)


class CommodityDeleteView(SectionRequiredMixin, DeleteView):
    section_codename = 'inventory.items'
    required_level = 'full'
    model = Commodity
    template_name = 'inventory/item_confirm_delete.html'
    success_url = reverse_lazy('inventory:commodity_list')


class CategoryListView(SectionRequiredMixin, ListView):
    section_codename = 'inventory.categories'
    model = Category
    template_name = 'inventory/category_list.html'
    context_object_name = 'categories'


class CategoryCreateView(SectionRequiredMixin, CreateView):
    section_codename = 'inventory.categories'
    required_level = 'full'
    model = Category
    fields = ['name', 'description']
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('inventory:inv_category_list')


class CategoryUpdateView(SectionRequiredMixin, UpdateView):
    section_codename = 'inventory.categories'
    required_level = 'full'
    model = Category
    fields = ['name', 'description']
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('inventory:inv_category_list')


class StockTransactionCreateView(SectionRequiredMixin, CreateView):
    section_codename = 'inventory.items'
    required_level = 'full'
    model = StockTransaction
    fields = ['commodity', 'transaction_type', 'quantity', 'notes']
    template_name = 'inventory/commodity_form.html'
    success_url = reverse_lazy('inventory:dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        commodity = form.instance.commodity
        commodity.current_stock += form.instance.quantity
        commodity.save()
        messages.success(self.request, f"Stock updated for {commodity.name}.")
        return response


class SupplierListView(SectionRequiredMixin, ListView):
    section_codename = 'inventory.suppliers'
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(vendor_code__icontains=query) | Q(contact_person__icontains=query))
        return queryset


class SupplierCreateView(SectionRequiredMixin, CreateView):
    section_codename = 'inventory.suppliers'
    required_level = 'full'
    model = Supplier
    fields = ['name', 'vendor_code', 'contact_person', 'email', 'phone', 'address', 'tax_id', 'status']
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Add New Supplier"
        return context


class SupplierUpdateView(SectionRequiredMixin, UpdateView):
    section_codename = 'inventory.suppliers'
    required_level = 'full'
    model = Supplier
    fields = ['name', 'vendor_code', 'contact_person', 'email', 'phone', 'address', 'tax_id', 'status']
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Edit Supplier: {self.object.name}"
        return context


class PurchaseOrderListView(SectionRequiredMixin, ListView):
    section_codename = 'inventory.purchase_orders'
    model = PurchaseOrder
    template_name = 'inventory/po_list.html'
    context_object_name = 'pos'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        status = self.request.GET.get('status')
        if query:
            queryset = queryset.filter(Q(po_number__icontains=query) | Q(supplier__name__icontains=query))
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class PurchaseOrderDetailView(SectionRequiredMixin, DetailView):
    section_codename = 'inventory.purchase_orders'
    model = PurchaseOrder
    template_name = 'inventory/po_detail.html'
    context_object_name = 'po'


class PurchaseOrderReceiveView(SectionRequiredMixin, View):
    section_codename = 'inventory.purchase_orders'
    required_level = 'full'
    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        if po.status != 'received':
            po.status = 'received'
            po.save()
            messages.success(request, f"Purchase Order {po.po_number} marked as Received. Units have been generated.")
        else:
            messages.info(request, f"Purchase Order {po.po_number} is already received.")
        return redirect('inventory:po_detail', pk=pk)
