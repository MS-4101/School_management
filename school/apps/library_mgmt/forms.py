from django import forms
from .models import Book, Category, SubCategory, BookIssue, BookCopy
from apps.accounts.models import CustomUser
from django.utils import timezone
from datetime import timedelta


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['name', 'category', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['rows'] = 3


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'category', 'sub_category',
                  'publisher', 'published_date',
                  'description', 'cover_image', 'location']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'cover_image':
                field.widget.attrs['class'] = 'form-control'
        self.fields['published_date'].widget = forms.DateInput(attrs={
            'type': 'date', 'class': 'form-control'
        })
        self.fields['description'].widget.attrs['rows'] = 3
        self.fields['sub_category'].queryset = SubCategory.objects.none()
        if self.instance.pk and self.instance.category:
            self.fields['sub_category'].queryset = SubCategory.objects.filter(category=self.instance.category)
        elif 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['sub_category'].queryset = SubCategory.objects.filter(category_id=category_id)
            except (ValueError, TypeError):
                pass


class BookIssueForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    due_date = forms.DateTimeField(
        initial=lambda: timezone.now() + timedelta(days=14),
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )

    class Meta:
        model = BookIssue
        fields = ['user', 'book_copy', 'due_date', 'remarks']

    def __init__(self, *args, **kwargs):
        book = kwargs.pop('book', None)
        super().__init__(*args, **kwargs)
        if book:
            self.fields['book_copy'].queryset = book.copies.filter(status='available', availability=True)
        else:
            self.fields['book_copy'].queryset = BookCopy.objects.filter(status='available', availability=True)
        self.fields['book_copy'].widget.attrs.update({'class': 'form-control'})
        self.fields['remarks'].widget.attrs.update({'class': 'form-control', 'rows': 2})
