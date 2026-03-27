from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Sub-Categories'
        ordering = ['category', 'name']
        unique_together = ['name', 'category']

    def __str__(self):
        return f"{self.category.name} → {self.name}"


class Book(models.Model):
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True, verbose_name='ISBN')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    inventory_item = models.ForeignKey(
        'inventory.Commodity', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='library_books', help_text='Linked inventory commodity for stock tracking'
    )
    publisher = models.CharField(max_length=200, blank=True)
    published_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, help_text='Shelf / Rack location')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} by {self.author}"

    @property
    def total_copies(self):
        return self.copies.count()

    @property
    def available_copies(self):
        return self.copies.filter(availability=True, status='available').count()

    @property
    def is_available(self):
        return self.available_copies > 0


class BookCopy(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('issued', 'Issued'),
        ('lost', 'Lost'),
        ('maintenance', 'Maintenance'),
    ]
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies')
    po_item = models.ForeignKey(
        'inventory.PurchaseOrderItem', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='book_copies'
    )
    accession_number = models.CharField(max_length=100, unique=True, verbose_name='Accession Number')
    bar_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    condition_status = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    availability = models.BooleanField(default=True, help_text='Whether the book can be issued')
    added_date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Book Copies'
        ordering = ['accession_number']

    def __str__(self):
        return f"{self.book.title} ({self.accession_number})"


class BookIssue(models.Model):
    STATUS_CHOICES = [
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='all_issues')
    book_copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE, related_name='issues', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='book_issues')
    issue_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='issued')
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.book.title} ({self.book_copy.accession_number if self.book_copy else 'N/A'}) → {self.user}"

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = timezone.now() + timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.status == 'returned':
            return False
        return timezone.now() > self.due_date

    @property
    def fine_amount(self):
        if not self.is_overdue and self.status == 'returned':
            if self.return_date and self.return_date > self.due_date:
                days = (self.return_date - self.due_date).days
                return max(days, 0) * 2
            return 0
        if self.is_overdue:
            days = (timezone.now() - self.due_date).days
            return max(days, 0) * 2
        return 0


class Fine(models.Model):
    issue = models.OneToOneField(BookIssue, on_delete=models.CASCADE, related_name='fine')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    paid_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = 'Paid' if self.paid else 'Unpaid'
        return f"Fine ₹{self.amount} ({status}) - {self.issue.book.title}"


class DamageLog(models.Model):
    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('repairing', 'Repairing'),
        ('written_off', 'Written Off'),
    ]
    book_copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE, related_name='damage_logs')
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='reported_book_damages'
    )
    damage_date = models.DateTimeField(default=timezone.now)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')

    class Meta:
        ordering = ['-damage_date']

    def __str__(self):
        return f"Damage: {self.book_copy.accession_number} ({self.status})"
