import pytest
from apps.accounts.models import School, CustomUser
from apps.buses.models import Bus, Student

@pytest.fixture
def bus_setup(db):
    admin = CustomUser.objects.create_user(username='admin')
    school = School.objects.create(name='Greenwood', admin_user=admin)
    bus = Bus.objects.create(school=school, bus_name='Bus 1', bus_number='B1', login_id='bus1')
    bus.set_password('pass123')
    return school, bus

@pytest.mark.django_db
class TestBusModels:
    def test_bus_creation(self, bus_setup):
        school, bus = bus_setup
        assert bus.bus_name == 'Bus 1'
        assert bus.school == school
        from django.contrib.auth.hashers import check_password
        assert check_password('pass123', bus.login_password)

    def test_student_multi_tenancy(self, bus_setup):
        school1, bus1 = bus_setup
        admin2 = CustomUser.objects.create_user(username='admin2')
        school2 = School.objects.create(name='Blueberry', admin_user=admin2)

        s1 = Student.objects.create(school=school1, name='Alice', class_name='1A')
        s2 = Student.objects.create(school=school2, name='Bob', class_name='1B')

        assert Student.objects.filter(school=school1).count() == 1
        assert Student.objects.filter(school=school2).count() == 1
