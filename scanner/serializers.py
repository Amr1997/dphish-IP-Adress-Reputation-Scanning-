from rest_framework import serializers
from .models import IPScanTask

class IPScanTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPScanTask
        fields = '__all__'
