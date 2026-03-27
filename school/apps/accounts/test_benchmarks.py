import pytest
from apps.accounts.models import CustomUser, Role, Section, SectionPermission

@pytest.mark.django_db
def test_rbac_check_performance(benchmark):
    user = CustomUser.objects.create_user(username='bench_user')
    role = Role.objects.create(name='Bench Role')
    user.roles.add(role)

    section = Section.objects.create(name='Bench Section', codename='bench')
    SectionPermission.objects.create(role=role, section=section, access_level='view')

    # Benchmark the section access check
    result = benchmark(user.has_section_access, 'bench', 'view')
    assert result is True

@pytest.mark.django_db
def test_rbac_check_no_access_performance(benchmark):
    user = CustomUser.objects.create_user(username='bench_user_2')
    # No roles, no permissions
    result = benchmark(user.has_section_access, 'bench', 'view')
    assert result is False
