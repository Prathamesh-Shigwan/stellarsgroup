from django.db.models import Sum, Count, Q
from django.views.decorators.http import require_POST
from products.models import MainCategory, SubCategory, Product, CartItem, Order, OrderItem, \
    ExtraImages,ProductVariant, VariantExtraImage, Inventory, VariantInventory, Cart, CartItem, \
    Wishlist, ShippingAddress, BillingAddress,BannerImage, About
from accounts.models import User
from blog.models import Blog
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime, timedelta, date
from django.http import JsonResponse
from django.utils.timezone import make_aware, localtime
from django.contrib.admin.models import LogEntry
from django.db.models.functions import TruncDay, TruncMonth
from django.utils.timezone import now
from django.db import models  # Import the models module
from custom_admin.utils import get_recent_actions_ut  # Ensure you have this function to fetch recent actions
from custom_admin.forms import DateRangeForm, MainCategoryForm, SubCategoryForm, \
    ProductForm, ExtraImagesFormSet, ProductVariantForm, VariantExtraImageForm, \
    InventoryForm, VariantInventoryForm, OrderForm, CartForm, WishlistForm, \
    BlogForm, BannerImageForm, CustomerForm, ProfileForm, AboutForm
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.forms import modelformset_factory
from django.db import transaction
from django.forms import inlineformset_factory


def is_admin(user):
    return user.is_superuser


@staff_member_required
def dashboard(request):
    # Default date range (current month)
    today = now()
    default_start_date = today.replace(day=1).date()  # Convert to date
    default_end_date = today.date()  # Convert to date

    # Process the date filter form
    form = DateRangeForm(request.GET or None)
    start_date = default_start_date
    end_date = default_end_date

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date') or default_start_date
        end_date = form.cleaned_data.get('end_date') or default_end_date

    # Convert dates to aware datetime objects
    start_date = make_aware(datetime.combine(start_date, datetime.min.time()))
    end_date = make_aware(datetime.combine(end_date, datetime.max.time()))

    # Total sales (sum of all orders' totals) within the date range
    total_sales = Order.objects.filter(status='completed', created_at__range=(start_date, end_date)) \
        .aggregate(Sum('total'))['total__sum'] or 0.00

    # Total orders count within the date range
    total_orders = Order.objects.filter(created_at__range=(start_date, end_date)).count()

    # Payment methods breakdown
    payment_methods = Order.objects.filter(created_at__range=(start_date, end_date)) \
        .values('payment_method').annotate(count=Count('payment_method'))

    # Total products count
    total_products = Product.objects.count()

    # Products in cart
    products_in_cart = CartItem.objects.aggregate(total=Sum('quantity'))['total'] or 0

    # Canceled orders count within the date range
    canceled_orders = Order.objects.filter(status='cancelled', created_at__range=(start_date, end_date)).count()

    # Returned orders count within the date range
    returned_orders = Order.objects.filter(status='returned', created_at__range=(start_date, end_date)).count()

    # Replaced orders count within the date range
    replaced_orders = Order.objects.filter(status='replaced', created_at__range=(start_date, end_date)).count()

    # Total customers
    total_customers = User.objects.filter(is_staff=False).count()

    # Total blogs
    total_blogs = Blog.objects.count()

    # Recent orders
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]

    # Recent actions (custom utility function to fetch admin actions)
    recent_actions = get_recent_actions(request)

    context = {
        'form': form,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'payment_methods': payment_methods,  # List of payment methods with counts
        'total_products': total_products,
        'products_in_cart': products_in_cart,
        'canceled_orders': canceled_orders,
        'returned_orders': returned_orders,
        'replaced_orders': replaced_orders,
        'total_customers': total_customers,
        'total_blogs': total_blogs,
        'recent_orders': recent_orders,
        'recent_actions': recent_actions,
    }

    return render(request, 'custom_admin/dashboard.html', context)


def weekly_order_data(request):
    # Get the current date and the start of the week (Monday)
    today = now()
    start_of_week = today - timedelta(days=today.weekday())  # Monday

    # Prepare labels for each day of the week
    labels = [(start_of_week + timedelta(days=i)).strftime("%A") for i in range(7)]

    # Initialize data with 0 for each day
    data = {day: 0 for day in labels}

    # Query orders created in the last week and group by day
    orders = (
        Order.objects.filter(created_at__gte=start_of_week, created_at__lt=start_of_week + timedelta(days=7))
        .annotate(day=models.functions.TruncDay('created_at'))
        .values('day')
        .annotate(total=Count('id'))
    )

    # Populate the data dictionary
    for order in orders:
        day_label = order['day'].strftime("%A")
        data[day_label] = order['total']

    return JsonResponse({'labels': labels, 'data': list(data.values())})


def daily_sales_data(request):
    # Get sales data for the last 7 days
    today = datetime.today()
    last_7_days = [today - timedelta(days=i) for i in range(7)][::-1]

    labels = [day.strftime("%A") for day in last_7_days]  # Day names
    data = []

    for day in last_7_days:
        start_of_day = make_aware(datetime.combine(day, datetime.min.time()))
        end_of_day = make_aware(datetime.combine(day, datetime.max.time()))

        # Sum sales for the day
        daily_sales = Order.objects.filter(
            status='completed',
            created_at__range=(start_of_day, end_of_day)
        ).aggregate(Sum('total'))['total__sum'] or 0
        data.append(daily_sales)

    return JsonResponse({'labels': labels, 'data': data})


def monthly_sales_data(request):
    # Get the current year
    current_year = now().year

    # Prepare labels for each month
    labels = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    # Initialize data with 0 for each month
    data = {month: 0 for month in labels}

    # Query orders from the current year and group by month
    orders = (
        Order.objects.filter(created_at__year=current_year)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('total'))
    )

    # Populate the data dictionary
    for order in orders:
        month_label = order['month'].strftime("%B")
        data[month_label] = float(order['total'])  # Convert to float for JavaScript compatibility

    return JsonResponse({'labels': labels, 'data': list(data.values())})


def get_recent_actions(request):
    # Fetch the 10 most recent log entries
    recent_actions = LogEntry.objects.select_related('content_type', 'user').order_by('-action_time')[:10]

    # Prepare the data for rendering
    actions = []
    for entry in recent_actions:
        actions.append({
            'object_repr': entry.object_repr,  # Object name
            'action_flag': entry.get_action_flag_display(),  # Action type (Add, Change, Delete)
            'content_type': entry.content_type.name,  # Content type (e.g., Order, Product)
            'user': entry.user.username,  # User who performed the action
            'action_time': localtime(entry.action_time),  # Localized action time
        })

    return actions


@staff_member_required
def main_categories_view(request):
    main_categories = MainCategory.objects.all()
    return render(request, 'custom_admin/products/main_categories.html', {'main_categories': main_categories})


def add_main_category_view(request):
    if request.method == 'POST':
        form = MainCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:main_categories')
    else:
        form = MainCategoryForm()
    return render(request, 'custom_admin/products/add_main_category.html', {'form': form})


def edit_main_category_view(request, pk):
    category = get_object_or_404(MainCategory, pk=pk)
    if request.method == 'POST':
        form = MainCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:main_categories')
    else:
        form = MainCategoryForm(instance=category)
    return render(request, 'custom_admin/products/edit_main_category.html', {'form': form, 'category': category})


def delete_main_category_view(request, pk):
    category = get_object_or_404(MainCategory, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('custom_admin:main_categories')
    return render(request, 'custom_admin/products/delete_main_category.html', {'category': category})


def subcategories_view(request):
    subcategories = SubCategory.objects.all()
    return render(request, 'custom_admin/products/subcategories.html', {'subcategories': subcategories})


def add_subcategory_view(request):
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:subcategories')
    else:
        form = SubCategoryForm()
    return render(request, 'custom_admin/products/add_subcategory.html', {'form': form})


def edit_subcategory_view(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, request.FILES, instance=subcategory)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:subcategories')
    else:
        form = SubCategoryForm(instance=subcategory)
    return render(request, 'custom_admin/products/edit_subcategory.html', {'form': form, 'subcategory': subcategory})


def delete_subcategory_view(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    if request.method == 'POST':
        subcategory.delete()
        return redirect('custom_admin:subcategories')
    return render(request, 'custom_admin/products/delete_subcategory.html', {'subcategory': subcategory})


def product_list_view(request):
    products = Product.objects.all()
    return render(request, 'custom_admin/products/product_list.html', {'products': products})


def add_product_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        formset = ExtraImagesFormSet(request.POST, request.FILES, instance=form.instance)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():  # Ensure atomicity
                product = form.save()
                formset.instance = product
                formset.save()
            return redirect('custom_admin:product_list')
        else:
            print(form.errors, formset.errors)  # Debug errors
    else:
        form = ProductForm()
        formset = ExtraImagesFormSet()

    return render(
        request,
        'custom_admin/products/add_product.html',
        {'form': form, 'formset': formset}
    )


def edit_product_view(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        formset = ExtraImagesFormSet(request.POST, request.FILES, instance=product)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                product = form.save()  # Save the product
                formset.instance = product  # Associate extra images with this product
                formset.save()  # Save all extra images
            return redirect('custom_admin:product_list')
        else:
            print("Form errors:", form.errors)
            print("Formset errors:", formset.errors)
    else:
        form = ProductForm(instance=product)
        formset = ExtraImagesFormSet(instance=product)

    return render(
        request,
        'custom_admin/products/edit_product.html',
        {'form': form, 'formset': formset, 'product': product}
    )


def delete_product_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('custom_admin:product_list')
    return render(request, 'custom_admin/products/delete_product.html', {'product': product})


def variant_list_view(request):
    variants = ProductVariant.objects.all()
    return render(request, 'custom_admin/products/variant_list.html', {'variants': variants})



# Create the formset for extra images
VariantExtraImageFormSet = inlineformset_factory(
    ProductVariant,
    VariantExtraImage,
    form=VariantExtraImageForm,
    extra=1,  # Allows adding one extra image
    can_delete=True  # Allows deletion of extra images
)


@staff_member_required
def add_variant_view(request):
    if request.method == 'POST':
        form = ProductVariantForm(request.POST, request.FILES)
        formset = VariantExtraImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                variant = form.save()
                formset.instance = variant  # Bind the variant to the formset
                formset.save()
            return redirect('custom_admin:variant_list')  # Replace with the correct URL for the variant list
        else:
            print(form.errors, formset.errors)  # Debugging errors
    else:
        form = ProductVariantForm()
        formset = VariantExtraImageFormSet()

    return render(request, 'custom_admin/products/add_variant.html', {'form': form, 'formset': formset})


@staff_member_required
def edit_variant_view(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)

    if request.method == 'POST':
        form = ProductVariantForm(request.POST, request.FILES, instance=variant)
        formset = VariantExtraImageFormSet(request.POST, request.FILES, instance=variant)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            return redirect('custom_admin:variant_list')
        else:
            print(f"Form errors: {form.errors}")
            print(f"Formset errors: {formset.errors}")
    else:
        form = ProductVariantForm(instance=variant)
        formset = VariantExtraImageFormSet(instance=variant)

    return render(
        request,
        'custom_admin/products/edit_variant.html',
        {'form': form, 'formset': formset, 'variant': variant}
    )


def delete_variant_view(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)
    if request.method == 'POST':
        variant.delete()
        return redirect('custom_admin:variant_list')
    return render(request, 'custom_admin/products/delete_variant.html', {'variant': variant})


def inventory_list_view(request):
    inventories = Inventory.objects.all()
    return render(request, 'custom_admin//products/inventory_list.html', {'inventories': inventories})


def add_inventory_view(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:inventory_list')
    else:
        form = InventoryForm()
    return render(request, 'custom_admin//products/add_inventory.html', {'form': form})


def edit_inventory_view(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=inventory)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:inventory_list')
    else:
        form = InventoryForm(instance=inventory)
    return render(request, 'custom_admin//products/edit_inventory.html', {'form': form, 'inventory': inventory})


def delete_inventory_view(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        inventory.delete()
        return redirect('custom_admin:inventory_list')
    return render(request, 'custom_admin//products/delete_inventory.html', {'inventory': inventory})


# Variant Inventory Views
def variant_inventory_list_view(request):
    variant_inventories = VariantInventory.objects.all()
    return render(request, 'custom_admin//products/variant_inventory_list.html', {'variant_inventories': variant_inventories})


def add_variant_inventory_view(request):
    if request.method == 'POST':
        form = VariantInventoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:variant_inventory_list')
    else:
        form = VariantInventoryForm()
    return render(request, 'custom_admin//products/add_variant_inventory.html', {'form': form})


def edit_variant_inventory_view(request, pk):
    variant_inventory = get_object_or_404(VariantInventory, pk=pk)
    if request.method == 'POST':
        form = VariantInventoryForm(request.POST, instance=variant_inventory)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:variant_inventory_list')
    else:
        form = VariantInventoryForm(instance=variant_inventory)
    return render(request, 'custom_admin//products/edit_variant_inventory.html', {'form': form, 'variant_inventory': variant_inventory})


def delete_variant_inventory_view(request, pk):
    variant_inventory = get_object_or_404(VariantInventory, pk=pk)
    if request.method == 'POST':
        variant_inventory.delete()
        return redirect('custom_admin:variant_inventory_list')
    return render(request, 'custom_admin/products/delete_variant_inventory.html', {'variant_inventory': variant_inventory})


# Order List View
def order_list_view(request):
    orders = Order.objects.all()
    return render(request, 'custom_admin/order/order_list.html', {'orders': orders})


# Add Order View
def add_order_view(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:order_list')
    else:
        form = OrderForm()
    return render(request, 'custom_admin/order/add_order.html', {'form': form})


# Edit Order View
def edit_order_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:order_list')
    else:
        form = OrderForm(instance=order)
    return render(request, 'custom_admin/order/edit_order.html', {'form': form, 'order': order})


# Delete Order View
def delete_order_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('custom_admin:order_list')
    return render(request, 'custom_admin/order/delete_order.html', {'order': order})


def cart_list_view(request):
    carts = Cart.objects.all()
    return render(request, 'custom_admin/order/cart_list.html', {'carts': carts})


def add_cart_view(request):
    if request.method == 'POST':
        form = CartForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:cart_list')
    else:
        form = CartForm()
    return render(request, 'custom_admin/order/add_cart.html', {'form': form})


def edit_cart_view(request, pk):
    cart = get_object_or_404(Cart, pk=pk)
    if request.method == 'POST':
        form = CartForm(request.POST, instance=cart)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:cart_list')
    else:
        form = CartForm(instance=cart)
    return render(request, 'custom_admin/order/edit_cart.html', {'form': form, 'cart': cart})


def delete_cart_view(request, pk):
    cart = get_object_or_404(Cart, pk=pk)
    if request.method == 'POST':
        cart.delete()
        return redirect('custom_admin:cart_list')
    return render(request, 'custom_admin/order/delete_cart.html', {'cart': cart})


def wishlist_list_view(request):
    wishlists = Wishlist.objects.all()
    return render(request, 'custom_admin/order/wishlist_list.html', {'wishlists': wishlists})

# Add View
def add_wishlist_view(request):
    if request.method == 'POST':
        form = WishlistForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:wishlist_list')
    else:
        form = WishlistForm()
    return render(request, 'custom_admin/order/add_wishlist.html', {'form': form})

# Edit View
def edit_wishlist_view(request, pk):
    wishlist = get_object_or_404(Wishlist, pk=pk)
    if request.method == 'POST':
        form = WishlistForm(request.POST, instance=wishlist)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:wishlist_list')
    else:
        form = WishlistForm(instance=wishlist)
    return render(request, 'custom_admin/order/edit_wishlist.html', {'form': form, 'wishlist': wishlist})


# Delete View
def delete_wishlist_view(request, pk):
    wishlist = get_object_or_404(Wishlist, pk=pk)
    if request.method == 'POST':
        wishlist.delete()
        return redirect('custom_admin:wishlist_list')
    return render(request, 'custom_admin/order/delete_wishlist.html', {'wishlist': wishlist})


def user_addresses_view(request, user_id):
    # Fetch user
    user = get_object_or_404(User, id=user_id)

    # Fetch user's shipping and billing addresses
    shipping_addresses = ShippingAddress.objects.filter(user=user)
    billing_addresses = BillingAddress.objects.filter(user=user)

    context = {
        'user': user,
        'shipping_addresses': shipping_addresses,
        'billing_addresses': billing_addresses
    }

    return render(request, 'custom_admin/order/user_addresses.html', context)


# Blog List View
def blog_list_view(request):
    blogs = Blog.objects.all()
    return render(request, 'custom_admin/order/blog_list.html', {'blogs': blogs})

def add_blog_view(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:blog_list')
    else:
        form = BlogForm()
    return render(request, 'custom_admin/order/add_blog.html', {'form': form})

def edit_blog_view(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:blog_list')
    else:
        form = BlogForm(instance=blog)
    return render(request, 'custom_admin/order/edit_blog.html', {'form': form, 'blog': blog})

@require_POST
def delete_blog_view(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    blog.delete()
    return redirect('custom_admin:blog_list')


@staff_member_required
def banner_list_view(request):
    banners = BannerImage.objects.all()
    return render(request, 'custom_admin/order/banner_list.html', {'banners': banners})

@staff_member_required
def add_banner_view(request):
    if request.method == 'POST':
        form = BannerImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:banner_list')
    else:
        form = BannerImageForm()
    return render(request, 'custom_admin/order/add_banner.html', {'form': form})

@staff_member_required
def edit_banner_view(request, pk):
    banner = get_object_or_404(BannerImage, pk=pk)
    if request.method == 'POST':
        form = BannerImageForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:banner_list')
    else:
        form = BannerImageForm(instance=banner)
    return render(request, 'custom_admin/order/edit_banner.html', {'form': form, 'banner': banner})

@staff_member_required
def delete_banner_view(request, pk):
    banner = get_object_or_404(BannerImage, pk=pk)
    if request.method == 'POST':
        banner.delete()
        return redirect('custom_admin:banner_list')
    return render(request, 'custom_admin/order/delete_banner.html', {'banner': banner})


@staff_member_required
def customer_list_view(request):
    customers = User.objects.filter(is_staff=False)
    return render(request, 'custom_admin/order/customer_list.html', {'customers': customers})

@staff_member_required
def add_customer_view(request):
    if request.method == 'POST':
        user_form = CustomerForm(request.POST)
        profile_form = ProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user = user_form.save()
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
            return redirect('custom_admin:customer_list')
    else:
        user_form = CustomerForm()
        profile_form = ProfileForm()

    return render(request, 'custom_admin/order/add_customer.html', {'user_form': user_form, 'profile_form': profile_form})

@staff_member_required
def edit_customer_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile = user.profile

    if request.method == 'POST':
        user_form = CustomerForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
            return redirect('custom_admin:customer_list')
    else:
        user_form = CustomerForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'custom_admin/order/edit_customer.html', {'user_form': user_form, 'profile_form': profile_form, 'customer': user})

@staff_member_required
def delete_customer_view(request, pk):
    customer = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('custom_admin:customer_list')
    return render(request, 'custom_admin/order/delete_customer.html', {'customer': customer})



@staff_member_required
def about_list_view(request):
    about_items = About.objects.all()
    return render(request, 'custom_admin/order/about_list.html', {'about_items': about_items})


@staff_member_required
def add_about_view(request):
    if request.method == 'POST':
        form = AboutForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:about_list')
    else:
        form = AboutForm()

    return render(request, 'custom_admin/order/add_about.html', {'form': form})


@staff_member_required
def edit_about_view(request, pk):
    about_item = get_object_or_404(About, pk=pk)
    if request.method == 'POST':
        form = AboutForm(request.POST, request.FILES, instance=about_item)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:about_list')
    else:
        form = AboutForm(instance=about_item)

    return render(request, 'custom_admin/order/edit_about.html', {'form': form, 'about_item': about_item})

@staff_member_required
def delete_about_view(request, pk):
    about_item = get_object_or_404(About, pk=pk)
    if request.method == 'POST':
        about_item.delete()
        return redirect('custom_admin:about_list')
    return render(request, 'custom_admin/order/delete_about.html', {'about_item': about_item})