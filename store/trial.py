from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . import forms, models


# Utility functions
def get_cart_count(request):
    """Get the count of unique products in the cart (using session)."""
    cart = request.session.get('cart', [])
    return len(set(cart))


def get_wishlist_count(user):
    """Get the count of items in the user's wishlist."""
    return models.Wishlist.objects.filter(user=user).count()


# Views
def home_view(request):
    """Render the homepage with available products."""
    products = models.Product.objects.all()
    product_count_in_cart = get_cart_count(request)

    if request.user.is_authenticated:
        wishlist_count = get_wishlist_count(request.user)
    else:
        wishlist_count = 0

    return render(request, 'store/index.html', {
        'products': products,
        'product_count_in_cart': product_count_in_cart,
        'wishlist_count': wishlist_count
    })


def customer_signup_view(request):
    """Handle customer registration."""
    user_form = forms.CustomerUserForm()
    customer_form = forms.CustomerForm()

    if request.method == 'POST':
        user_form = forms.CustomerUserForm(request.POST)
        customer_form = forms.CustomerForm(request.POST, request.FILES)

        if user_form.is_valid() and customer_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()

            customer = customer_form.save(commit=False)
            customer.user = user
            customer.save()

            messages.success(request, "Account created successfully!")
            return redirect('customerlogin')

    return render(request, 'store/customersignup.html', {
        'userForm': user_form,
        'customerForm': customer_form
    })


@login_required(login_url='customerlogin')
def wishlist_view(request):
    """View and manage the user's wishlist."""
    wishlist_items = models.Wishlist.objects.filter(user=request.user)

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')

        if action == 'add':
            product = get_object_or_404(models.Product, id=product_id)
            models.Wishlist.objects.get_or_create(user=request.user, product=product)
            messages.success(request, "Product added to your wishlist!")
        elif action == 'remove':
            models.Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
            messages.success(request, "Product removed from your wishlist!")

        return redirect('wishlist')

    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})


@login_required(login_url='customerlogin')
def order_history_view(request):
    """Display the order history for the logged-in user."""
    orders = models.Orders.objects.filter(customer=request.user.customer)
    return render(request, 'store/order_history.html', {'orders': orders})


@login_required(login_url='customerlogin')
def place_order_view(request):
    """Handle placing an order for the items in the cart."""
    cart = request.session.get('cart', [])
    if not cart:
        messages.error(request, "Your cart is empty!")
        return redirect('home')

    products = models.Product.objects.filter(id__in=cart)

    if request.method == 'POST':
        for product in products:
            models.Orders.objects.create(
                product=product,
                customer=request.user.customer,
                status='Pending'
            )
        # Clear cart after placing the order
        request.session['cart'] = []
        messages.success(request, "Your order has been placed successfully!")
        return redirect('order-history')

    return render(request, 'store/checkout.html', {'products': products})


# Cart-related Views
def add_to_cart_view(request, pk):
    """Add a product to the cart (using session)."""
    cart = request.session.get('cart', [])
    if pk not in cart:
        cart.append(pk)
        request.session['cart'] = cart
        messages.success(request, "Product added to the cart!")
    else:
        messages.info(request, "Product is already in the cart!")
    
    return redirect('home')


def cart_view(request):
    """View the cart (using session)."""
    cart = request.session.get('cart', [])
    products = models.Product.objects.filter(id__in=cart)

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        cart = [pid for pid in cart if str(pid) != product_id]
        request.session['cart'] = cart
        messages.success(request, "Product removed from the cart!")

    return render(request, 'store/cart.html', {'products': products})
