from django.db import models
import json

class IPScanTask(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'

    ip_address = models.GenericIPAddressField()
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,  # Add choices here
        default=StatusChoices.PENDING,  # Set default status
    )
    result = models.TextField(null=True, blank=True)  # Use TextField for JSON compatibility
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_result(self, result_dict):
        self.result = json.dumps(result_dict)  # Serialize JSON to string

    def get_result(self):
        return json.loads(self.result) if self.result else None  # Deserialize string to JSON
