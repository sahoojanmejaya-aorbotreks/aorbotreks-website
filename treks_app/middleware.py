import logging
from urllib import request
from .models import Visitor

logger = logging.getLogger(__name__)

class VisitorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            # Ensure a session exists
            if not request.session.session_key:
                request.session.create()

            path = request.path or ""
            if path.startswith("/admin/") or path.startswith("/static/") or path.startswith("/media/"):
                return response

            # IP handling behind proxies
            ip_raw = request.META.get("HTTP_X_FORWARDED_FOR")
            ip_address = (ip_raw.split(",")[0].strip() if ip_raw else request.META.get("REMOTE_ADDR"))
            user_agent = request.META.get("HTTP_USER_AGENT", "unknown")


            # Log unique visitor per session
            Visitor.objects.get_or_create(
                session_id=request.session.session_key,
                defaults={"ip_address": ip_address, "user_agent": user_agent},
            )
        except Exception as e:
            logger.error(f"VisitorMiddleware error: {e}")
        return response
