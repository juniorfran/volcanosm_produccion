from django.shortcuts import redirect
from django.urls import reverse

class MikrotikSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'mikrotik_api' not in request.session:
            return redirect(reverse('internet:mikrotik_login'))  # Redirige al login si no hay sesión
        return self.get_response(request)
