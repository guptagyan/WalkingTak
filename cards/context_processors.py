from .models import CartItem

def cart_count(request):
    count = 0
    if request.user.is_authenticated:
        count = CartItem.objects.filter(cart__user=request.user).count()
    return {
        'global_cart_count': count
    }
