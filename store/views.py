from django.shortcuts import render, get_object_or_404, redirect,HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate,  login as auth_login, logout, get_user_model
from .models import Product, User, Review, Orders
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Avg
import json
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
import logging


logger = logging.getLogger(__name__)

Customer = get_user_model()



def get_cart_items(request):
    cart = request.session.get('cart', {})  
    cart_items = []

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(sno=product_id)
            cart_items.append({
                'productId': product.sno,
                'productName': product.name,
                'price': product.price,
                'imageUrl': product.product_image.url,
                'quantity': quantity,
                'total': product.price * quantity,
            })
        except Product.DoesNotExist:
            continue

    return JsonResponse({'cartItems': cart_items})



def home_view(request):
    products = Product.objects.all()[:8]
    return render(request,'store/index.html', {'products': products})

def shop(request):
    products = Product.objects.all()
    category = request.GET.get('category', 'All')
    if category == 'All':
        products = Product.objects.all()
    else:
        products = Product.objects.filter(category__iexact=category)
    paginator = Paginator(products, 8)  # Show 8 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'store/shop.html', {'products': products, 'selected_category': category, 'page_obj': page_obj})
    
def contact(request):
    return render(request,'store/contact.html')
    
def cart(request):
    return render(request,'store/cart.html')


# def cart(request):
#     cart = request.session.get('cart', {})
#     sno = map(int, cart.keys())  # Convert string keys to integers
#     products = Product.objects.filter(id__in=sno)
#     cart_items = [
#         {
#             'product': product,
#             'quantity': cart[str(product.sno)],
#             'subtotal': product.price * cart[str(product.sno)],
#         }
#         for product in products
#     ]
#     total = sum(item['subtotal'] for item in cart_items)
#     return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})


# def add_to_cart(request, sno):
#     cart = request.session.get('cart', {})
#     if str(sno) in cart:
#         cart[str(sno)]['quantity'] += 1
#     else:
#         product = get_object_or_404(Product, sno=sno)
#         cart[str(sno)] = {'name': product.name, 'price': float(product.price), 'quantity': 1}
#     request.session['cart'] = cart
#     request.session.modified = True
#     return JsonResponse({'status': 'success', 'cart': cart})
  

# def update_cart(request, sno):
#     if request.method == "POST":
#         quantity = int(request.POST.get('quantity', 1))
#         cart = request.session.get('cart', {})
#         if quantity > 0:
#             cart[str(sno)] = quantity
#         else:
#             cart.pop(str(sno), None)  # Remove product if quantity is 0
#         request.session['cart'] = cart
#         messages.success(request, "Cart updated!")
#     return redirect('cart')

# def remove_from_cart(request, sno):
#     cart = request.session.get('cart', {})
#     if str(sno) in cart:
#         cart.pop(str(sno))
#         request.session['cart'] = cart
#         messages.success(request, "Item removed from cart.")
#     return redirect('cart')


@login_required
def submit_review(request, sno):
    if request.method == "POST":
        product = get_object_or_404(Product, sno=sno)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        # # Validate rating range
        # if int(rating) < 1 or int(rating) > 5:
        #     messages.error(request, "Rating must be between 1 and 5.")
        #     return redirect('prod_view', sno=product.sno)

        # Save review
        Review.objects.create(
            product=product,
            customer=request.user,
            rating=rating,
            comment=comment
        )
        messages.success(request, "Review added successfully!")
        avg_rating = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
        rounded_avg_rating = round(avg_rating, 2) if avg_rating else 0
        return redirect('prod_view', sno=product.sno)
    

@login_required
def checkout(request):
    if request.method == "POST":
        try:
            # Get the cart data and validate it
            cart_data = request.POST.get('cart_data')
            cart_items = json.loads(cart_data) if cart_data else []

            if not cart_items:
                return JsonResponse({'error': 'Cart is empty!'}, status=400)

            # Retrieve customer details
            customer = Customer.objects.get(email=request.user.email)

            # Prepare the products list for the order
            products_list = []
            total_price = 0

            # Validate and process stock for all products
            for item in cart_items:
                product_id = item.get('id')
                quantity = item.get('quantity')

                product = Product.objects.get(sno=product_id)
                if product.quantity < quantity:
                    messages.error(request, f"Error adding product: {e}")
                    return redirect('checkout')
                    # return JsonResponse({'error': f'Not enough stock for {product.name}'}, status=400)

                # Update product stock
                product.quantity -= quantity
                product.save()

                # Add product details to the products list
                products_list.append({
                    "product_name": product.name,
                    "quantity": quantity,
                    "price": product.price
                })

                # Calculate total price
                subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
                delivery = 5.00  # Example fixed delivery fee
                discount = subtotal * 0.1 if subtotal > 50 else 0
                total_price = subtotal + delivery - discount

            # Create a single order with products as JSON
            Orders.objects.create(
                customer=customer,
                email=customer.email,
                address=request.POST.get('streetaddress'),
                mobile=request.POST.get('phone'),
                zipcode=request.POST.get('postcodezip'),
                status='Pending',
                products=products_list,
                total_price=total_price,
            )

            messages.success(request, {'success': 'Order placed successfully!', 'total_price': total_price})
            return redirect('/')
        except Product.DoesNotExist:
            return messages.error(request, {'error': 'Invalid product in cart!'}, status=400)
        except json.JSONDecodeError:
            return messages.error(request, {'error': 'Invalid cart data!'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

    # For GET request, load the checkout page
    customer = Customer.objects.get(email=request.user.email)
    return render(request, 'store/checkout.html', {
        'customer': customer,
    })




# if request.method == 'POST':
#         # Fetch the current user
#         user = request.user

#         # Retrieve billing information
#         street_address = request.POST.get('streetaddress')
#         town_city = request.POST.get('towncity')
#         postcode_zip = request.POST.get('postcodezip')
#         phone = request.POST.get('phone') or user.mobile  # Default to user's phone
#         full_address = f"{street_address}, {town_city}, {postcode_zip}"

#         # Retrieve cart data from hidden input
#         cart_data = request.POST.get('cart_data', '[]')
#         try:
#             cart_items = json.loads(cart_data)
#             if not all('id' in item and 'quantity' in item for item in cart_items):
#                 messages.error(request, 'Cart data is incomplete or corrupted.')
#                 return redirect('cart')
#         except json.JSONDecodeError:
#             messages.error(request, 'Invalid cart data.')
#             return redirect('cart')

#         product_ids = [int(item['id']) for item in cart_items if 'id' in item]
#         products = {product.sno: product for product in Product.objects.filter(sno__in=product_ids)}


#         order_created = False

#         for item in cart_items:
#             product_sno = int(item['id'])
#             quantity = int(item.get('quantity', 1))
#             product = products.get(product_sno)
#             if not product_sno:
#                 messages.error(request, 'Product ID missing in cart item.')
#                 continue

#             try:
#                 product = get_object_or_404(Product, sno=int(product_sno))
#                 quantity = int(item.get('quantity', 1))  # Default to 1 if missing

#                 # Create the order
#                 order = Orders(product=product, customer=user, email=user.email, address=full_address,  mobile=phone, quantity=int(item['quantity']), status='Pending',)
#                 try:
#                     order.save()
#                 except Exception as e:
#                     print(f"Order save failed: {e}")
#                 messages.success(request, 'Your order has been placed successfully!')
#             except Exception as e:
#                 messages.error(request, f"An error occurred while processing your order: {str(e)}")
#             return redirect('cart')
        
#         return redirect('/')

#     context = {
#         'customer': request.user,
#     }



#  Process the cart items (implementation depends on your `OrderItem` model)
        # for item in cart_items:
        #     # Create OrderItem here (example assumes `Product` model exists)
        #     try:
        #         product = Product.objects.get(sno=item['id'])
        #         OrderItem.objects.create(
        #             order=order,
        #             product=product,
        #             price=product.price,
        #             quantity=item['quantity'],
        #         )
        #     except Product.DoesNotExist:
        #         messages.warning(request, f"Product with ID {item['id']} does not exist.")
        #         continue

        # Success message and redirect

@login_required
def order_history(request):
    return render(request,'store/order_history.html')


def prod_view(request, sno):
    product = get_object_or_404(Product, sno=sno)
    reviews = Review.objects.filter(product=product)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    review_count = reviews.count()  
    related_products = Product.objects.filter(category=product.category).exclude(sno=product.sno)[:4]
    # context = {'product': product, 'related_products': related_products}

    return render(request, 'store/product-single.html', {'product': product, 'reviews': reviews, 'average_rating': round(avg_rating, 2) if avg_rating else 0,
        'review_count': review_count, 'related_products': related_products})




@login_required
def user_account(request):
    try:
        # Get the currently logged-in user
        user = request.user

        # Retrieve all orders for the logged-in user
        orders = Orders.objects.filter(customer=user).all() 
        # for order in orders:
        #     total_price = 0
        #     for product in order.products:
        #         subtotal = product['price'] * product['quantity']
        #         delivery = 5.00  # Example fixed delivery fee
        #         discount = subtotal * 0.1 if subtotal > 50 else 0
        #         total_price = subtotal + delivery - discount
        #     order.total_price = total_price  # Adding calculated total price to each order

        return render(request, 'store/user_account.html', {
            'user': user,
            'orders': orders,
        })
    except Orders.DoesNotExist:
        # Handle case if no orders are found or any issues with the Orders model
        return render(request, 'store/user_account.html', {
            'user': request.user,
            'orders': [],  # Empty orders list if no orders exist
        })




def user_login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        # Authenticate the user
        user = authenticate(request, email=email, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Successfully logged in!")

            # Redirect to 'next' or fallback to 'home'
            next_url = request.POST.get('next')
            if not next_url or next_url == '':
                next_url = '/'
            return redirect(next_url)

        else:
            messages.error(request, "Invalid email or password. Please try again.")
            return redirect("login")  

    next_url = request.GET.get('next', '')
    return render(request, "store/login.html", {'next': next_url})



def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect('signup')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        # Check if email is already in use
        if Customer.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('signup')

        # Check if username is already in use
        if Customer.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect('signup')

        # Create the user
        try:
            user = Customer.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('login')
        except Exception as e:
            messages.error(request, "Something went wrong. Please try again.")
            return redirect('signup')

    return render(request, 'store/signup.html')

def logout_view(request):
    """
    Logs the user out and redirects to the home page or login page.
    """
    logout(request)
    return redirect('/')


def order_list(request):
    orders = Orders.objects.all()
    formatted_orders = []
    for order in orders:
        logger.debug(f"Order Products: {order.products}")  # Debug log
        formatted_orders.append({
            'id' : order.id,
            'customer': order.customer,
            'total_price': order.total_price,
            'status': order.status,
            'address': order.address,
            'products': order.products,
            'zipcode' : order.zipcode
        })
    return render(request, 'store/orderList.html', {'orders': formatted_orders})


def update_order_status(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Orders, id=order_id)
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
            messages.success(request, f"Order status updated to {new_status}.")
        else:
            messages.error(request, "Invalid status.")
    return redirect('order_list')

def addproducts(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        sno = request.POST.get('sno')
        category = request.POST.get('category')
        description = request.POST.get('description')
        
        # Handle file upload
        product_image = request.FILES.get('product_image')

        # Validation checks (optional but recommended)
        if not name or not price or not quantity or not sno or not category or not description:
            messages.error(request, "All fields are required.")
            return redirect('addproduct')

        # Save product to database
        try:
            product = Product(
                name=name,
                price=price,
                quantity=quantity,
                sno=sno,
                category=category,
                description=description,
                product_image=product_image
            )
            product.save()
            messages.success(request, f"Product '{name}' added successfully!")
            return redirect('addproduct')
        except Exception as e:
            messages.error(request, f"Error adding product: {e}")
            return redirect('addproduct')
    
    # Render the form
    return render(request, 'store/addproducts.html')

    