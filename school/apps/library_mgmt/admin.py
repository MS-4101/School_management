from django.contrib import admin
from .models import Category, SubCategory, Book, BookCopy, BookIssue, Fine, DamageLog


class BookCopyInline(admin.TabularInline):
    model = BookCopy
    extra = 1
    fields = ('accession_number', 'status', 'condition_status', 'availability')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'category', 'sub_category', 'total_copies', 'available_copies')
    list_filter = ('category', 'sub_category')
    search_fields = ('title', 'author', 'isbn')
    inlines = [BookCopyInline]


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ('accession_number', 'book', 'status', 'condition_status', 'availability', 'po_item')
    list_filter = ('status', 'condition_status', 'availability')
    search_fields = ('accession_number', 'book__title', 'bar_code')


@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = ('book', 'book_copy', 'user', 'issue_date', 'due_date', 'status')
    list_filter = ('status',)
    search_fields = ('book__title', 'book_copy__accession_number', 'user__username')


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ('issue', 'amount', 'paid', 'paid_date')
    list_filter = ('paid',)


@admin.register(DamageLog)
class DamageLogAdmin(admin.ModelAdmin):
    list_display = ('book_copy', 'reported_by', 'damage_date', 'status')
    list_filter = ('status',)
    search_fields = ('book_copy__accession_number', 'description')
