from django.db import models

class LogEntry(models.Model):
    client_id = models.CharField(max_length=255, db_index=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-timestamp"]