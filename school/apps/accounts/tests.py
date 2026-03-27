import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.accounts.models import Role, Permission, Section, SectionPermission

User = get_user_model()

@pytest.fixture
def admin_user(db):
    user = User.objects.create_superuser(username='admin', password='password123')
    return user

@pytest.mark.django_db
class TestAccountsModels:
    def test_create_user(self):
        user = User.objects.create_user(username='testuser', password='password123', email='test@example.com')
        assert user.username == 'testuser'
        assert user.is_active
        assert str(user) == 'testuser'

    def test_role_permissions(self):
        perm = Permission.objects.create(name='Can Edit', codename='can_edit')
        role = Role.objects.create(name='Editor')
        role.permissions.add(perm)
        user = User.objects.create_user(username='editor_user')
        user.roles.add(role)

        assert user.has_role('Editor')
        assert user.has_perm_code('can_edit')
        assert not user.has_perm_code('can_delete')

    def test_section_access(self):
        section = Section.objects.create(name='Library', codename='library')
        role = Role.objects.create(name='Librarian')
        SectionPermission.objects.create(role=role, section=section, access_level='view')

        user = User.objects.create_user(username='librarian_user')
        user.roles.add(role)

        assert user.has_section_access('library', 'view')
        assert not user.has_section_access('library', 'full')

@pytest.mark.django_db
class TestAccountsViews:
    def test_login_view_get(self, client):
        url = reverse('accounts:login')
        response = client.get(url)
        assert response.status_code == 200

    def test_login_view_post_success(self, client):
        User.objects.create_user(username='testuser', password='password123')
        url = reverse('accounts:login')
        response = client.post(url, {'username': 'testuser', 'password': 'password123'})
        assert response.status_code == 302

    def test_user_list_view(self, client, admin_user):
        client.force_login(admin_user)
        url = reverse('accounts:user_list')
        response = client.get(url)
        assert response.status_code == 200

    def test_role_list_view(self, client, admin_user):
        client.force_login(admin_user)
        url = reverse('accounts:role_list')
        response = client.get(url)
        assert response.status_code == 200

    def test_permission_list_view(self, client, admin_user):
        client.force_login(admin_user)
        url = reverse('accounts:permission_list')
        response = client.get(url)
        assert response.status_code == 200

    def test_profile_view(self, client, admin_user):
        client.force_login(admin_user)
        url = reverse('accounts:profile')
        response = client.get(url)
        assert response.status_code == 200

    def test_access_control_view(self, client, admin_user):
        client.force_login(admin_user)
        url = reverse('accounts:access_control')
        response = client.get(url)
        assert response.status_code == 200
