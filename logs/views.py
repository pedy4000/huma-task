import json
from datetime import timedelta
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import LogEntry

RATE_LIMIT = 5
WINDOW = timedelta(minutes=1)

@csrf_exempt
@require_http_methods(["POST"])
def create_log(request):
    try:
        data = json.loads(request.body)
        client_id = data["client_id"]
        message = data["message"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return JsonResponse(
            {"error": "JSON body with 'client_id' and 'message' required"},
            status=400,
        )

    cutoff = timezone.now() - WINDOW
    recent = LogEntry.objects.filter(
        client_id=client_id, timestamp__gte=cutoff
    ).count()

    if recent >= RATE_LIMIT:
        return JsonResponse({"error": "rate limit exceded"}, status=429)

    log = LogEntry.objects.create(client_id=client_id, message=message)
    return JsonResponse(
        {
            "id": log.id,
            "client_id": log.client_id,
            "message": log.message,
            "timestamp": log.timestamp
        },
        status=201
    )

@require_http_methods(["GET"])
def get_logs(requet, client_id):
    logs = LogEntry.objects.filter(client_id=client_id)[:20]
    return JsonResponse(
        {
            "client_id": client_id,
            "count": len(logs),
            "logs": [
                {"id": l.id, "message": l.message, "timestamp": l.timestamp.isoformat()}
                for l in logs
            ],
        },
        status=200,
    )