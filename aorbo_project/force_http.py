from django.http import HttpResponsePermanentRedirect

class ForceHttpMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is secure (HTTPS)
        if request.is_secure():
            # Redirect to HTTP version
            http_url = request.build_absolute_uri('http:' + request.get_full_path()[5:])
            return HttpResponsePermanentRedirect(http_url)
        
        response = self.get_response(request)
        return response
