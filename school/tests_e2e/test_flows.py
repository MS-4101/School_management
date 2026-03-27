import pytest
import os
from playwright.sync_api import Page, expect

# Set environment variable to allow async unsafe operations for Playwright + Django tests
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

@pytest.mark.django_db
def test_login_flow(page: Page, live_server):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    User.objects.create_superuser(username='admin', password='adminpassword123')

    # Go to login page
    page.goto(f"{live_server.url}/accounts/login/")

    # Fill login form
    page.fill('input[name="username"]', 'admin')
    page.fill('input[name="password"]', 'adminpassword123')
    page.click('button[type="submit"]')

    # Check if redirected to dashboard or home
    # Based on the fail log, it redirects to /dashboard/
    expect(page).to_have_url(f"{live_server.url}/dashboard/")
    expect(page.get_by_text("Welcome back, admin!")).to_be_visible()

    # Navigate to Library
    from apps.accounts.models import Section
    Section.objects.get_or_create(name='Library', codename='library', order=1)

    page.goto(f"{live_server.url}/library/")
    # Wait for content to load
    page.wait_for_load_state("networkidle")

    # Take screenshot
    os.makedirs('screenshots', exist_ok=True)
    page.screenshot(path='screenshots/login_and_navigation.png')

@pytest.mark.django_db
def test_book_search(page: Page, live_server):
    from django.contrib.auth import get_user_model
    from apps.library_mgmt.models import Book, Category
    User = get_user_model()
    User.objects.create_superuser(username='admin_search', password='adminpassword123')

    cat, _ = Category.objects.get_or_create(name='Science')
    Book.objects.get_or_create(title='Quantum Physics', author='Planck', isbn='111', category=cat)
    Book.objects.get_or_create(title='Biology', author='Mendel', isbn='222', category=cat)

    page.goto(f"{live_server.url}/accounts/login/")
    page.fill('input[name="username"]', 'admin_search')
    page.fill('input[name="password"]', 'adminpassword123')
    page.click('button[type="submit"]')

    # Go to book list
    page.goto(f"{live_server.url}/library/books/")

    # Search for 'Quantum'
    page.fill('input[name="search"]', 'Quantum')
    # The button might be inside a form, let's use the form submit
    page.keyboard.press("Enter")

    # Wait for result
    page.wait_for_load_state("networkidle")

    expect(page.get_by_text("Quantum Physics")).to_be_visible()
    # If search works correctly, Biology should not be visible.
    # If it was visible in previous run, search might be failing or it's an issue with the template showing all books anyway.
    expect(page.get_by_text("Biology")).not_to_be_visible()

    page.screenshot(path='screenshots/book_search.png')
