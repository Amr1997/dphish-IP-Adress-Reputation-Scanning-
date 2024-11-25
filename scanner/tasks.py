import requests
from celery import shared_task
from .models import IPScanTask
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

# Set up logging for better debugging
logger = logging.getLogger(__name__)

@shared_task
def process_ip(task_id):
    try:
        task = IPScanTask.objects.get(id=task_id)

        # Start task by marking it as in-progress
        task.status = IPScanTask.StatusChoices.IN_PROGRESS
        task.save()

        # Fetch IP info from ipinfo.io
        response = requests.get(f'https://ipinfo.io/{task.ip_address}/json')

        # If the response is successful, set the result, otherwise handle error
        if response.status_code == 200:
            task.set_result(response.json())  # Store the result in the serialized format
            task.status = IPScanTask.StatusChoices.COMPLETED  # Mark as completed
        else:
            task.set_result({'error': f"Failed to fetch data: {response.status_code}"})
            task.status = IPScanTask.StatusChoices.FAILED  # Mark as failed if the request fails

        task.save()

        # Send WebSocket notification
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'notifications',  # Group name to notify
            {
                'type': 'send_notification',
                'message': f'Task {task_id} completed with status: {task.status}'
            }
        )
    except IPScanTask.DoesNotExist:
        logger.error(f"Task with ID {task_id} does not exist.")
    except Exception as e:
        logger.error(f"An error occurred while processing task {task_id}: {str(e)}")
