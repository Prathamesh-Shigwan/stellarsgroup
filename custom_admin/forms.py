from django import forms
from products.models import MainCategory, SubCategory, Product, ExtraImages, \
    ProductVariant, VariantExtraImage, Inventory, VariantInventory, Order, Cart, \
    Wishlist, BannerImage, About
from django.forms import inlineformset_factory
from accounts.models import User, Profile
from blog.models import Blog
from tinymce.widgets import TinyMCE


class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False,
        label="Start Date"
    )
    end_date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False,
        label="End Date"
    )


class MainCategoryForm(forms.ModelForm):
    class Meta:
        model = MainCategory
        fields = ['title', 'image', 'price']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['title', 'parent_category', 'price', 'image']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter subcategory title',
            }),
            'parent_category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter price',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
        }




class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'pid',  # Include 'pid' for display (read-only)
            'user',  # Include 'user'
            'name', 'title', 'description', 'image', 'price', 'old_price',
            'main_category', 'sub_category', 'product_status', 'status', 'in_stock',
            'featured', 'sku',
        ]

        widgets = {
            'pid': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter pid',

            }),
            'user': forms.Select(attrs={
                'class': 'form-control',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name',
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product description',
                'rows': 4,
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter price',
            }),
            'old_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter old price',
            }),
            'main_category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'sub_category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'product_status': forms.Select(attrs={
                'class': 'form-control',
            }),
            'status': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'in_stock': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter SKU',
            }),
        }




class ExtraImagesForm(forms.ModelForm):
    class Meta:
        model = ExtraImages
        fields = ['id', 'image']  # Include 'id' field for edit functionality
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

ExtraImagesFormSet = inlineformset_factory(
    Product,
    ExtraImages,
    form=ExtraImagesForm,
    extra=3,  # Allows adding one extra image
    can_delete=True  # Allows deletion of extra images
)

# Form for ProductVariant
class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['product', 'color', 'size', 'gender', 'stock_quantity', 'price', 'image']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.Select(attrs={'class': 'form-control'}),
            'size': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter stock quantity'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }



# Form for VariantExtraImage
class VariantExtraImageForm(forms.ModelForm):
    class Meta:
        model = VariantExtraImage
        fields = ['id', 'image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

# Formset for handling VariantExtraImages
VariantExtraImageFormSet = inlineformset_factory(
    ProductVariant,
    VariantExtraImage,
    form=VariantExtraImageForm,
    extra=3,
    can_delete=True
)



class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['product', 'stock_quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class VariantInventoryForm(forms.ModelForm):
    class Meta:
        model = VariantInventory
        fields = ['product_variant', 'stock_quantity']
        widgets = {
            'product_variant': forms.Select(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'user', 'status', 'total', 'payment_method',
            'billing_full_name', 'billing_email', 'billing_address1',
            'billing_address2', 'billing_city', 'billing_state',
            'billing_zipcode', 'billing_country', 'billing_phone',
            'shipping_full_name', 'shipping_email', 'shipping_address1',
            'shipping_address2', 'shipping_city', 'shipping_state',
            'shipping_zipcode', 'shipping_country', 'shipping_phone',
            'feedback_note'
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'total': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_method': forms.TextInput(attrs={'class': 'form-control'}),
            'feedback_note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['user', 'discount_code']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'discount_code': forms.Select(attrs={'class': 'form-control'}),
        }


class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ['user', 'product']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
        }


class BlogForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE())

    class Meta:
        model = Blog
        fields = ['title', 'content', 'author', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter blog title'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Author name'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class BannerImageForm(forms.ModelForm):
    class Meta:
        model = BannerImage
        fields = ['title', 'image', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter banner title'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'username', 'bio']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter bio', 'rows': 4}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'city', 'state', 'zipcode', 'country']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter address', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter city'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter state'}),
            'zipcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ZIP code'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter country'}),
        }


class AboutForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE())

    class Meta:
        model = About
        fields = ['title', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }