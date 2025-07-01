from django.contrib import admin
from .models import (
    Category, Product, Cart, CartItem, Wishlist,
    Order, OrderItem, Review, CustomerProfile,
    FAQ, NewsletterSubscriber
)

# ---------- Category Admin ----------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_filter = ['name']


# ---------- Product Admin ----------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'available', 'featured', 'created', 'updated']
    list_filter = ['available', 'featured', 'category', 'created']
    list_editable = ['price', 'stock', 'available', 'featured']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


# ---------- Inline Cart Items in Cart ----------
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


# ---------- Cart Admin ----------
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    inlines = [CartItemInline]
    search_fields = ['user__username', 'user__email']


# ---------- Cart Item Admin ----------
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'added_at', 'updated_at']
    list_filter = ['added_at']
    search_fields = ['cart__user__username', 'product__name']


# ---------- Wishlist Admin ----------
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_at']
    search_fields = ['user__username', 'product__name']


# ---------- Inline Order Items in Order ----------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


# ---------- Order Admin ----------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'created', 'updated', 'total']
    list_filter = ['status', 'created', 'updated']
    inlines = [OrderItemInline]
    search_fields = ['user__username', 'email', 'first_name', 'last_name']
    readonly_fields = ['total']


# ---------- Order Item Admin ----------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'price', 'quantity']
    search_fields = ['order__id', 'product__name']


# ---------- Review Admin ----------
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created', 'updated', 'active']
    list_filter = ['active', 'created', 'rating']
    search_fields = ['product__name', 'user__username', 'comment']


# ---------- Customer Profile Admin ----------
@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'default_city', 'default_state', 'default_country']
    search_fields = ['user__username', 'user__email']


# ---------- FAQ Admin ----------
@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'created', 'updated']
    list_filter = ['category']
    search_fields = ['question', 'answer']


# ---------- Newsletter Subscriber Admin ----------
@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'is_active']
    list_filter = ['is_active']
    search_fields = ['email']
