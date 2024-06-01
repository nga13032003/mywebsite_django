from django.contrib import admin
from .models import Loai, SanPham, CartItem, Order, OrderItem, Post, Comment, Message
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'sanpham', 'user', 'body', 'timestamp')  # Adjusted 'date' to 'timestamp'
    list_filter = ('sanpham', 'user')
    search_fields = ('sanpham__TenSP', 'user__username', 'body')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(user=request.user)

@admin.register(Loai)
class LoaiAdmin(admin.ModelAdmin):
    list_display = ('id', 'TenLoai')
    search_fields = ('TenLoai',)

@admin.register(SanPham)
class SanPhamAdmin(admin.ModelAdmin):
    list_display = ('id', 'TenSP', 'MaLoai', 'DonGia', 'SoLuong')
    list_filter = ('MaLoai',)
    search_fields = ('TenSP', 'MoTa')
    list_editable = ('DonGia', 'SoLuong')
    ordering = ('id',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'sanpham', 'quantity')
    list_filter = ('user',)
    search_fields = ('user__username', 'sanpham__TenSP')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'shipping_address', 'payment_method', 'created_at', 'status')
    list_filter = ('user', 'created_at', 'status')
    search_fields = ('user__username', 'shipping_address')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'sanpham', 'quantity', 'price', 'total')
    list_filter = ('order', 'sanpham')
    search_fields = ('order__user__username', 'sanpham__TenSP')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'date')
    search_fields = ('title', 'body')

# Inline class to display OrderItems within OrderAdmin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

# Adding the inline to OrderAdmin
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('id', 'user', 'total_amount', 'shipping_address', 'payment_method', 'created_at', 'status')
    list_filter = ('user', 'created_at', 'status')
    search_fields = ('user__username', 'shipping_address')

admin.site.unregister(Order)
admin.site.register(Order, OrderAdmin)
from django import forms
class MessageForm(forms.ModelForm):
    reply = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = Message
        fields = ['message']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'timestamp', 'message')
    list_filter = ('sender', 'receiver', 'timestamp')
    search_fields = ('sender__username', 'receiver__username', 'message')
    form = MessageForm
    change_form_template = 'admin/change_form.html'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(sender=request.user) | queryset.filter(receiver=request.user)

    def response_change(self, request, obj):
        if "reply" in request.POST and request.POST["reply"].strip():
            reply_message = request.POST["reply"]
            new_message = Message(
                sender=request.user,
                receiver=obj.sender,
                message=reply_message
            )
            new_message.save()
            self.message_user(request, "Replied successfully.")
            return self.response_post_save_change(request, obj)
        return super().response_change(request, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_reply_form'] = True
        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)