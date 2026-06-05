import json
from datetime import timedelta
from django.test import TestCase, Client
from django.utils import timezone

from .models import LogEntry

class LogAPITests(TestCase):
    def setUp(self):
        self.client = Client()
    
    def _post(self, client_id="test_client", message="test_message"):
        return self.client.post(
            "/log",
            data=json.dumps({"client_id": client_id, "message": message}),
            content_type="application/json",
        )
    
    def test_create_log_succeeds(self):
        resp = self._post()
        self.assertEqual(resp.status_code, 201)
        body = resp.json()
        self.assertEqual(body["client_id"], "test_client")
        self.assertEqual(body["message"], "test_message")
        self.assertIn("timestamp", body)
        self.assertEqual(LogEntry.objects.count(), 1)
    
    def test_rate_limit_blocks_on_sixth(self):
        for _ in range(5):
            self.assertEqual(self._post().status_code, 201)
        resp = self._post()
        self.assertEqual(resp.status_code, 429)
        self.assertEqual(LogEntry.objects.count(), 5)

    def test_rate_limit_is_per_client(self):
        for _ in range(5):
            self.assertEqual(self._post(client_id="test_client").status_code, 201)
        self.assertEqual(self._post(client_id="test_client2").status_code, 201)
    
    def test_old_logs_do_not_count_toward_limit(self):
        old = timezone.now() - timedelta(minutes=2)
        for _ in range(5):
            entry = LogEntry.objects.create(client_id="test_client", message="old")
            LogEntry.objects.filter(pk=entry.pk).update(timestamp=old)
        self.assertEqual(self._post().status_code, 201)
    
    def test_bad_body_returns_400(self):
        resp = self.client.post("/log", data="raw", content_type="application/json")
        self.assertEqual(resp.status_code, 400)