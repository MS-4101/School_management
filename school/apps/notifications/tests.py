import pytest
from unittest.mock import patch, MagicMock
from apps.notifications.services import send_whatsapp_message
from apps.notifications.models import NotificationLog

@pytest.mark.django_db
class TestNotificationServices:
    @patch('twilio.rest.Client')
    def test_send_whatsapp_success(self, mock_twilio_client):
        # Setup mock
        mock_msg = MagicMock()
        mock_msg.sid = 'SM123'
        mock_twilio_client.return_value.messages.create.return_value = mock_msg

        log = NotificationLog.objects.create(
            notification_type='test', recipient_phone='+1234567890', message='Hello'
        )

        result = send_whatsapp_message('+1234567890', 'Hello', log)

        assert result is True
        log.refresh_from_db()
        assert log.status == 'sent'
        assert log.twilio_sid == 'SM123'

    @patch('twilio.rest.Client')
    def test_send_whatsapp_failure(self, mock_twilio_client):
        mock_twilio_client.return_value.messages.create.side_effect = Exception("Twilio error")

        log = NotificationLog.objects.create(
            notification_type='test', recipient_phone='+1234567890', message='Hello'
        )

        result = send_whatsapp_message('+1234567890', 'Hello', log)

        assert result is False
        log.refresh_from_db()
        assert log.status == 'failed'
