import pytest
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from apps.lab_mgmt.models import Lab, Equipment, EquipmentCategory, LabUnit, LabBooking

User = get_user_model()

@pytest.fixture
def lab_setup(db):
    user = User.objects.create_user(username='lab_user', password='password123')
    lab = Lab.objects.create(name='Physics Lab', location='Room 101')
    category = EquipmentCategory.objects.create(name='Electronics')
    equipment = Equipment.objects.create(name='Oscilloscope', lab=lab, category=category, quantity=2)
    unit1 = LabUnit.objects.create(equipment=equipment, internal_uid='OSC001')
    unit2 = LabUnit.objects.create(equipment=equipment, internal_uid='OSC002')
    return user, lab, equipment, unit1, unit2

@pytest.mark.django_db
class TestLabModels:
    def test_equipment_availability(self, lab_setup):
        user, lab, equipment, unit1, unit2 = lab_setup
        assert equipment.available_quantity == 2

        unit1.status = 'in_use'
        unit1.save()
        assert equipment.available_quantity == 1

    def test_lab_booking_flow(self, lab_setup):
        user, lab, equipment, unit1, unit2 = lab_setup
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=2)

        booking = LabBooking.objects.create(
            user=user, equipment=equipment, lab_unit=unit1,
            purpose='Testing circuits', quantity_booked=1,
            start_date=start, end_date=end
        )

        assert booking.status == 'pending'

        # Approve booking
        admin = User.objects.create_user(username='admin_user', is_superuser=True)
        booking.status = 'approved'
        booking.approved_by = admin
        unit1.status = 'in_use'
        unit1.save()
        booking.save()

        assert equipment.available_quantity == 1
        assert unit1.status == 'in_use'

@pytest.mark.django_db
class TestLabViews:
    def test_lab_list_view(self, client, lab_setup):
        user, lab, equipment, unit1, unit2 = lab_setup
        user.is_superuser = True
        user.save()
        client.force_login(user)

        from django.urls import reverse
        url = reverse('lab:lab_list')
        response = client.get(url)
        assert response.status_code == 200
        assert 'Physics Lab' in response.content.decode()
