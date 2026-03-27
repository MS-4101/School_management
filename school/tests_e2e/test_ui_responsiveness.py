import pytest
import os
from playwright.sync_api import Page, expect

# Set environment variable to allow async unsafe operations for Playwright + Django tests
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

VIEWPORTS = [
    {"name": "Desktop", "width": 1280, "height": 800},
    {"name": "Tablet", "width": 768, "height": 1024},
    {"name": "Mobile", "width": 375, "height": 667},
]

@pytest.mark.django_db
@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_responsiveness_dashboard(page: Page, live_server, viewport):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user, created = User.objects.get_or_create(username=f'ui_admin_{viewport["name"]}', is_superuser=True)
    if created:
        user.set_password('pass123')
        user.save()

    page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})

    # Login
    page.goto(f"{live_server.url}/accounts/login/")
    page.fill('input[name="username"]', f'ui_admin_{viewport["name"]}')
    page.fill('input[name="password"]', 'pass123')
    page.click('button[type="submit"]')

    # Check Dashboard
    page.goto(f"{live_server.url}/dashboard/")
    page.wait_for_load_state("networkidle")

    expect(page).to_have_url(f"{live_server.url}/dashboard/")

    # Capture screenshots for all viewports
    os.makedirs('screenshots/responsiveness', exist_ok=True)
    page.screenshot(path=f'screenshots/responsiveness/dashboard_{viewport["name"]}.png')

@pytest.mark.django_db
@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_responsiveness_login(page: Page, live_server, viewport):
    page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
    page.goto(f"{live_server.url}/accounts/login/")

    login_card = page.locator(".card, .login-container, form")
    expect(login_card.first).to_be_visible()

    os.makedirs('screenshots/responsiveness', exist_ok=True)
    page.screenshot(path=f'screenshots/responsiveness/login_{viewport["name"]}.png')
