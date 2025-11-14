from django.shortcuts import render
from .models import Category,Product,City, Order, OrderItem,ProductVariant

from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from .models import ProductVariant
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from decimal import Decimal
from django.http import JsonResponse
from twilio.rest import Client



def home(request):
    from .models import Product, Category

    # Get all products (if needed elsewhere)
    products = Product.objects.all()

    # Get "Accessories" category
    accessories_category = Category.objects.filter(name__iexact='Accessories').first()
    accessories_products = Product.objects.filter(category=accessories_category)[:4] if accessories_category else []

    # Get "Cuban" category
    cuban_category = Category.objects.filter(name__iexact='Cuban').first()
    cuban_products = Product.objects.filter(category=cuban_category)[:4] if cuban_category else []

    context = {
        'products': products,
        'accessories_products': accessories_products,
        'cuban_products': cuban_products,
    }

    return render(request, 'Warzone/home.html', context)


def product(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    return render(request, 'Warzone/product.html', {'categories': categories,'products': products},)



    
    


def product_list(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    products = category.product.all()  # Uses the related_name 'projects'
    return render(request, 'Warzone/product.html', {'category': category, 'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    images = product.images.all()  # related_name='images'
    variants = product.variants.all()  # related_name='variants'
    return render(request, 'Warzone/productdetail.html', {
        'product': product,
        'images': images,
        'variants': variants,
    })


# def contactc(request):
#     if request.method == 'POST':
#         form = ContactForm(request.POST)
#         if form.is_valid():
#             # Save the form data to the database
#             form.save()

#             # Get the form data to send in the email
#             name = form.cleaned_data['name']
#             email = form.cleaned_data['email']
#             mobile = form.cleaned_data['mobile']
#             description = form.cleaned_data['description']
            
#             # Compose the email content
#             subject = f'New Contact Message from {name}'
#             message = f"Name: {name}\nEmail: {email}\nPhone: {mobile}\nMessage: {description}"
#             recipient_email = 'najus777@gmail.com'  # Replace with the recipient's email address
            
#             try:
#                 # Send the email using Django's send_mail function
#                 send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient_email])

#                 # Redirect to success page or any other appropriate page
#                 return redirect('Warzone:success')  # You can change 'Warzone:success' to your actual success URL
#             except Exception as e:
#                 # Handle any errors that occur while sending the email
#                 print(f"Error sending email: {e}")
#                 return render(request, 'Warzone/contact.html', {'form': form, 'error': 'There was an error sending the email. Please try again.'})

#     else:
#         form = ContactForm()

#     return render(request, 'Warzone/contact.html', {'form': form})
def success(request):
    return render(request, 'Warzone/success.html')

def get_cart(request):
    return request.session.get("cart", {})

def save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True

def cart_items_json(request):
    cart = get_cart(request)
    items = []
    total = 0

    for variant_id, item in cart.items():
        variant = get_object_or_404(ProductVariant, id=variant_id)
        quantity = item["quantity"]
        subtotal = float(variant.price) * quantity
        total += subtotal
        feature_image = variant.product.images.filter(is_feature=True).first()
        items.append({
            "id": variant.id,
            "product": variant.product.title,
            "variant": variant.name,
            "price": float(variant.price),
            "quantity": quantity,
            "subtotal": subtotal,
            "feature_image": feature_image.image.url if feature_image else ''
        })

    return JsonResponse({"items": items, "total": total})


def add_to_cart(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    
    # Get cart from session
    cart = request.session.get("cart", {})

    if str(variant_id) in cart:
        cart[str(variant_id)]["quantity"] += 1
    else:
        cart[str(variant_id)] = {
            "quantity": 1
        }

    # Save back to session
    request.session["cart"] = cart

    # Return JSON response for drawer update
    return JsonResponse({
        "success": True,
        "variant_id": variant_id,
        "quantity": cart[str(variant_id)]["quantity"]
    })

def update_cart_ajax(request, variant_id):
    if request.method == "POST":
        cart = request.session.get("cart", {})
        quantity = int(request.POST.get("quantity", 1))
        if quantity > 0:
            cart[str(variant_id)]["quantity"] = quantity
        else:
            cart.pop(str(variant_id), None)
        request.session["cart"] = cart
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def remove_from_cart_ajax(request, variant_id):
    cart = request.session.get("cart", {})
    cart.pop(str(variant_id), None)
    request.session["cart"] = cart
    return JsonResponse({"success": True})

def send_whatsapp_message_twilio(to_number, message_body):
    """
    Send a WhatsApp message using Twilio API.
    """
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        message = client.messages.create(
        body=message_body,
        from_=settings.TWILIO_WHATSAPP_NUMBER,
        to=to_number
    )
    

        return message.sid
    except Exception as e:
        print("Error sending WhatsApp message:", e)
        return None

def get_delivery_charge(request):
    city_id = request.GET.get("city_id")
    if city_id:
        try:
            city = City.objects.get(id=city_id)
            return JsonResponse({"delivery_charge": city.delivery_charge})
        except City.DoesNotExist:
            pass
    return JsonResponse({"delivery_charge": 0})

def checkout(request):
    cities = City.objects.all()
    cart = request.session.get("cart", {})  # cart stores variant IDs

    cart_items = []
    total_price = 0

    # Prepare cart items
    for variant_id, item in cart.items():
        variant = get_object_or_404(ProductVariant, id=variant_id)
        quantity = item.get("quantity", 1)
        price = float(variant.price)
        subtotal = price * quantity
        total_price += subtotal

        feature_image = variant.product.images.filter(is_feature=True).first()
        img_url = feature_image.image.url if feature_image else ""

        cart_items.append({
            "product": variant.product,
            "variant": variant,  # store full variant
            "quantity": quantity,
            "price": price,
            "subtotal": subtotal,
            "feature_image": img_url,
        })

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        city_id = request.POST.get("city")
        landmark = request.POST.get("landmark", "")

        # If cart is empty, don’t allow checkout
        if not cart:
            messages.error(request, "Your cart is empty!")
            return redirect("store:product_list")

        # Delivery charge
        city = City.objects.get(id=city_id) if city_id else None
        delivery_charge = city.delivery_charge if city else 0
        total_with_delivery = Decimal(total_price) + Decimal(delivery_charge)

        # Save order
        order = Order.objects.create(
            name=name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            landmark=landmark,
            total_price=total_with_delivery,
        )

        # Save order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                title=f"{item['product'].title} - {item['variant'].name}",  # product + variant
                price=item["price"],
                quantity=item["quantity"],
                image_url=item["feature_image"],
            )

        # Clear cart session
        request.session["cart"] = {}

        # Confirmation message
        messages.success(request, f"Order placed successfully! Your order ID is {order.id}")

        # WhatsApp order message
        message_text = (
            f"✅ Order Confirmation\n\n"
            f"Order ID: {order.id}\n"
            f"Name: {order.name}\n"
            f"Phone: {order.phone}\n"
            f"Email: {order.email}\n"
            f"Address: {order.address}, {order.city.name if order.city else ''}\n"
        )
        if order.landmark:
            message_text += f"Landmark: {order.landmark}\n"

        message_text += "\n🛒 Items:\n"
        for item in cart_items:
            message_text += f"- {item['product'].title} ({item['variant'].name}) x {item['quantity']} = NPR {item['subtotal']}\n"

        message_text += f"\nTotal (with delivery): NPR {order.total_price}"

        # Send via WhatsApp (Twilio)
        send_whatsapp_message_twilio(settings.MY_WHATSAPP_NUMBER, message_text)

        return redirect("store:success")

    # Render checkout page
    context = {
        "cities": cities,
        "cart_items": cart_items,
        "total_price": total_price,
    }
    return render(request, "Warzone/checkout.html", context)


