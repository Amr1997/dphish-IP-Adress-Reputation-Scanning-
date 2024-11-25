from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from .models import IPScanTask
from .tasks import process_ip
from ipaddress import ip_address, AddressValueError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ipaddress import ip_address, AddressValueError
from .models import IPScanTask
from .tasks import process_ip

class IPScanView(APIView):
    def post(self, request):
        ips = request.data.get('ips', [])
        invalid_ips = []  # List to collect invalid IPs
        ip_task_map = {}  # Dictionary to map IPs to task IDs

        # Validate each IP address
        for ip in ips:
            try:
                # Try to validate the IP address
                ip_address(ip)  # This will raise a ValueError if the IP is invalid
                # If valid, create a task
                task = IPScanTask.objects.create(ip_address=ip)
                process_ip.delay(task.id)
                ip_task_map[ip] = task.id  # Map IP to task ID
            except ValueError:  # Catch invalid IP address and add to invalid_ips
                invalid_ips.append(ip)
            except AddressValueError:  # In case of specific AddressValueError
                invalid_ips.append(ip)

        # Prepare the response
        response_data = {"message": "Tasks initiated"}

        # If there are invalid IPs, add them to the response
        if invalid_ips:
            response_data["invalid_ips"] = invalid_ips

        # If there are valid IPs, add them to the response
        if ip_task_map:
            response_data["tasks"] = ip_task_map

        # If there were invalid IPs, return 400 status, else return 202
        if invalid_ips:
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(response_data, status=status.HTTP_202_ACCEPTED)



class WebhookView(APIView):
    def post(self, request):
        task_id = request.data.get("task_id")
        webhook_url = request.data.get("webhook_url")
        
        if not task_id or not webhook_url:
            return Response(
                {"error": "task_id and webhook_url are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            task = IPScanTask.objects.get(id=task_id)
            task_status = {
                "task_id": task.id,
                "ip_address": task.ip_address,
                "status": task.status,
                "result": task.result,
               
            }

            response = requests.post(webhook_url, json=task_status)
            
            if response.status_code in [200, 201]:
                return Response(
                    {"message": "Webhook notification sent successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "error": "Failed to notify frontend",
                        "details": response.text,
                    },
                    status=response.status_code,
                )
        except IPScanTask.DoesNotExist:
            return Response(
                {"error": f"Task with ID {task_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
