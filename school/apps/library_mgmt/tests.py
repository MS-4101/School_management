import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from apps.library_mgmt.models import Book, BookCopy, BookIssue, Fine, Category, SubCategory

User = get_user_model()

@pytest.fixture
def library_setup(db):
    user = User.objects.create_user(username='student', password='password123')
    category = Category.objects.create(name='Science')
    book = Book.objects.create(title='Physics', author='Newton', isbn='1234567890', category=category)
    copy = BookCopy.objects.create(book=book, accession_number='ACC001')
    return user, book, copy

@pytest.mark.django_db
class TestLibraryModels:
    def test_book_availability(self, library_setup):
        user, book, copy = library_setup
        assert book.is_available
        assert book.total_copies == 1
        assert book.available_copies == 1

    def test_book_issue_return(self, library_setup):
        user, book, copy = library_setup
        issue = BookIssue.objects.create(user=user, book=book, book_copy=copy)
        copy.status = 'issued'
        copy.availability = False
        copy.save()

        assert not book.is_available
        assert issue.status == 'issued'
        assert not issue.is_overdue

        # Return book
        issue.status = 'returned'
        issue.return_date = timezone.now()
        issue.save()
        copy.status = 'available'
        copy.availability = True
        copy.save()

        assert book.is_available

    def test_fine_calculation_regression(self, library_setup):
        user, book, copy = library_setup
        # Create an overdue issue
        past_date = timezone.now() - timedelta(days=20)
        due_date = timezone.now() - timedelta(days=5)
        issue = BookIssue.objects.create(user=user, book=book, book_copy=copy, issue_date=past_date, due_date=due_date)

        assert issue.is_overdue
        # Fine is 2 per day
        # (now - (now - 5 days)) = 5 days. 5 * 2 = 10
        assert issue.fine_amount >= 10

    def test_fine_creation_on_return(self, client, library_setup):
        user, book, copy = library_setup
        due_date = timezone.now() - timedelta(days=5)
        issue = BookIssue.objects.create(user=user, book=book, book_copy=copy, due_date=due_date)

        # We'll use the view or the model logic directly
        # The view `return_book` in library_mgmt/views.py handles fine creation
        from django.urls import reverse
        client.force_login(user) # User needs permission but for now we test logic
        # Mocking superuser to bypass section_required for simplicity in this unit test
        user.is_superuser = True
        user.save()

        url = reverse('library:return_book', args=[issue.pk])
        response = client.post(url)
        assert response.status_code == 302

        issue.refresh_from_db()
        assert issue.status == 'returned'
        assert Fine.objects.filter(issue=issue).exists()
        fine = Fine.objects.get(issue=issue)
        assert fine.amount > 0

@pytest.mark.django_db
class TestLibraryViews:
    def test_book_list_view(self, client, library_setup):
        user, book, copy = library_setup
        user.is_superuser = True
        user.save()
        client.force_login(user)

        url = reverse('library:book_list')
        response = client.get(url)
        assert response.status_code == 200
        assert 'Physics' in response.content.decode()
