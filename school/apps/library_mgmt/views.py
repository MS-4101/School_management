from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from .models import Book, Category, SubCategory, BookIssue, Fine
from .forms import BookForm, CategoryForm, SubCategoryForm, BookIssueForm
from apps.accounts.decorators import section_required


# ─── Categories ──────────────────────────────────────────────

@login_required
@section_required('library', 'view')
def category_list(request):
    categories = Category.objects.prefetch_related('subcategories').all()
    return render(request, 'library_mgmt/category_list.html', {'categories': categories})


@login_required
@section_required('library.categories', 'full')
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('library:category_list')
    else:
        form = CategoryForm()
    return render(request, 'library_mgmt/category_form.html', {'form': form, 'title': 'Add Category'})


@login_required
@section_required('library.categories', 'full')
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated.')
            return redirect('library:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'library_mgmt/category_form.html', {'form': form, 'title': f'Edit: {category.name}'})


@login_required
@section_required('library.categories', 'full')
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted.')
        return redirect('library:category_list')
    return render(request, 'library_mgmt/category_confirm_delete.html', {'category': category})


# ─── Sub-Categories ──────────────────────────────────────────

@login_required
@section_required('library', 'view')
def subcategory_list(request):
    subcategories = SubCategory.objects.select_related('category').all()
    return render(request, 'library_mgmt/subcategory_list.html', {'subcategories': subcategories})


@login_required
@section_required('library.subcategories', 'full')
def subcategory_create(request):
    if request.method == 'POST':
        form = SubCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sub-Category created successfully.')
            return redirect('library:subcategory_list')
    else:
        form = SubCategoryForm()
    return render(request, 'library_mgmt/subcategory_form.html', {'form': form, 'title': 'Add Sub-Category'})


@login_required
@section_required('library.subcategories', 'full')
def subcategory_edit(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, instance=subcategory)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sub-Category updated.')
            return redirect('library:subcategory_list')
    else:
        form = SubCategoryForm(instance=subcategory)
    return render(request, 'library_mgmt/subcategory_form.html', {'form': form, 'title': f'Edit: {subcategory.name}'})


@login_required
@section_required('library.subcategories', 'full')
def subcategory_delete(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    if request.method == 'POST':
        subcategory.delete()
        messages.success(request, 'Sub-Category deleted.')
        return redirect('library:subcategory_list')
    return render(request, 'library_mgmt/subcategory_confirm_delete.html', {'subcategory': subcategory})


@login_required
def ajax_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(subcategories), safe=False)


# ─── Books ───────────────────────────────────────────────────

@login_required
@section_required('library', 'view')
def book_list(request):
    books = Book.objects.select_related('category', 'sub_category').all()
    search = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    subcategory_id = request.GET.get('subcategory', '')
    if search:
        books = books.filter(
            Q(title__icontains=search) | Q(author__icontains=search) | Q(isbn__icontains=search)
        )
    if category_id:
        books = books.filter(category_id=category_id)
    if subcategory_id:
        books = books.filter(sub_category_id=subcategory_id)
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    if category_id:
        subcategories = subcategories.filter(category_id=category_id)
    return render(request, 'library_mgmt/book_list.html', {
        'books': books, 'categories': categories, 'subcategories': subcategories,
        'search': search, 'selected_category': category_id, 'selected_subcategory': subcategory_id
    })


@login_required
@section_required('library.books', 'full')
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book added successfully.')
            return redirect('library:book_list')
    else:
        form = BookForm()
    return render(request, 'library_mgmt/book_form.html', {'form': form, 'title': 'Add Book'})


@login_required
@section_required('library.books', 'full')
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated.')
            return redirect('library:book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'library_mgmt/book_form.html', {'form': form, 'title': f'Edit: {book.title}'})


@login_required
@section_required('library.books', 'full')
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted.')
        return redirect('library:book_list')
    return render(request, 'library_mgmt/book_confirm_delete.html', {'book': book})


@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    copies = book.copies.all().order_by('accession_number')
    issues = book.all_issues.select_related('user').order_by('-issue_date')[:10]
    return render(request, 'library_mgmt/book_detail.html', {
        'book': book, 'copies': copies, 'issues': issues
    })


# ─── Issue / Return ──────────────────────────────────────────

@login_required
@section_required('library.issues', 'full')
def issue_book(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk)
    if not book.is_available:
        messages.error(request, 'No copies available.')
        return redirect('library:book_detail', pk=book_pk)
    if request.method == 'POST':
        form = BookIssueForm(request.POST, book=book)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.book = book
            issue.save()
            copy = issue.book_copy
            copy.status = 'issued'
            copy.availability = False
            copy.save()
            messages.success(request, f'Book issued to {issue.user}.')
            return redirect('library:book_detail', pk=book_pk)
    else:
        form = BookIssueForm(book=book)
    return render(request, 'library_mgmt/issue_form.html', {'form': form, 'book': book})


@login_required
@section_required('library.issues', 'full')
def return_book(request, issue_pk):
    issue = get_object_or_404(BookIssue, pk=issue_pk)
    if issue.status == 'returned':
        messages.info(request, 'Book already returned.')
        return redirect('library:issue_list')
    if request.method == 'POST':
        issue.return_date = timezone.now()
        issue.status = 'returned'
        issue.save()
        if issue.book_copy:
            copy = issue.book_copy
            copy.status = 'available'
            copy.availability = True
            copy.save()
        if issue.return_date > issue.due_date:
            days = (issue.return_date - issue.due_date).days
            fine_amount = max(days, 1) * 2
            Fine.objects.create(issue=issue, amount=fine_amount)
            messages.warning(request, f'Book returned with fine of ₹{fine_amount}.')
        else:
            messages.success(request, 'Book returned successfully.')
        return redirect('library:issue_list')
    return render(request, 'library_mgmt/return_confirm.html', {'issue': issue})


@login_required
@section_required('library.issues', 'view')
def issue_list(request):
    issues = BookIssue.objects.select_related('book', 'user').all()
    status_filter = request.GET.get('status', '')
    if status_filter:
        issues = issues.filter(status=status_filter)
    for issue in issues:
        if issue.status == 'issued' and issue.is_overdue:
            issue.status = 'overdue'
            issue.save()
    return render(request, 'library_mgmt/issue_list.html', {
        'issues': issues, 'status_filter': status_filter
    })


# ─── Fines ───────────────────────────────────────────────────

@login_required
@section_required('library.fines', 'view')
def fine_list(request):
    fines = Fine.objects.select_related('issue__book', 'issue__user').all()
    paid_filter = request.GET.get('paid', '')
    if paid_filter == 'yes':
        fines = fines.filter(paid=True)
    elif paid_filter == 'no':
        fines = fines.filter(paid=False)
    return render(request, 'library_mgmt/fine_list.html', {'fines': fines, 'paid_filter': paid_filter})


@login_required
@section_required('library.fines', 'full')
def fine_pay(request, pk):
    fine = get_object_or_404(Fine, pk=pk)
    if request.method == 'POST':
        fine.paid = True
        fine.paid_date = timezone.now()
        fine.save()
        messages.success(request, 'Fine marked as paid.')
    return redirect('library:fine_list')
