from TPV_.Ventas.models import Cart


class CreateCartMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.session.exists('cart'):
            request.session['cart'] = Cart.objects.create_cart(request.user).to_dict()

        response = self.get_response(request)

        return response