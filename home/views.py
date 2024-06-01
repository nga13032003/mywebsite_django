from .models import Post, Comment 
from .forms import RegistrationForm 
from django.http import HttpResponseRedirect 
from .forms import CommentForm 
from django.http import HttpResponse 
from django.shortcuts import render, redirect, get_object_or_404
from .models import Loai
from .models import SanPham, DanhGia
from .models import CartItem, Order, OrderItem
from django.http import JsonResponse
from .forms import CartItemForm,RatingForm
from .forms import TheLoaiForm, SanPhamForm
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db import transaction  # Thêm thư viện transaction để quản lý giao dịch
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.contrib import messages
from .models import Message
from .forms import MessageForm
from django.contrib.auth.models import User
# Hàm hiện danh sách Loại sản phẩm
def list(request):
    DM_loai = Loai.objects.all()
    data = {
        'DM_loai': DM_loai,
    }
    return render(request, 'page/dsLoai.html', data)
# Hàm đăng ký
def register(request):
    DM_loai = Loai.objects.all()  # Lấy danh sách tất cả các loại sản phẩm

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('DangNhap'))
    else:
        form = RegistrationForm()

    context = {
        'form': form,
        'DM_loai': DM_loai,
    }
    return render(request, 'page/dangky.html', context)
#Hàm index 
def index(request):
    DM_loai = Loai.objects.all()
    sanphams = SanPham.objects.all()

    context = {
        'DM_loai': DM_loai,
        'sanphams': sanphams,
    }

    return render(request, 'page/danhSachSanPham.html', context)

# def themLoai(request):
#     DM_loai = Loai.objects.all()
#     if request.method == 'POST':
#         form = TheLoaiForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect('/Sach/')
#     else:
#         form = TheLoaiForm()
    
#     return render(request, 'page/ThemLoai.html', {'form': form, 'DM_loai': DM_loai})
# Hàm danh sách sản phẩm theo loại 
def DSSPTheoLoai(request, ml):
    DM_loai = Loai.objects.all()
    loai = get_object_or_404(Loai, id=ml)
    sanphams = SanPham.objects.filter(MaLoai=loai)
    return render(request, 'page/DsspTheoLoai.html', {'loai': loai, 'sanphams': sanphams, 'DM_loai': DM_loai})

#Hàm lấy danh sách sản phẩm
def danhSachSanPham(request):
    DM_loai = Loai.objects.all()
    sanphams = SanPham.objects.all()
    return render(request, 'page/danhSachSanPham.html', {'sanphams': sanphams, 'DM_loai': DM_loai})

# def themSanPham(request):
#     DM_loai = Loai.objects.all()
#     if request.method == 'POST':
#         form = SanPhamForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect('/Sach/')
#     else:
#         form = SanPhamForm()
    
#     return render(request, 'page/ThemSanPham.html', {'form': form, 'DM_loai': DM_loai})
# Hàm chi tiết sản phẩm
def chiTietSanPham(request, pk):
    DM_loai = Loai.objects.all()
    sanpham = get_object_or_404(SanPham, id=pk)
    return render(request, 'page/chiTietSanPham.html', {'sanpham': sanpham, 'DM_loai': DM_loai})
#Hàm thêm sản phẩm vào giỏ hàng
@login_required
def add_to_cart(request, pk):
    DM_loai = Loai.objects.all()
    sanpham = get_object_or_404(SanPham, pk=pk)

    if request.method == 'POST':
        # Check if the product already exists in the user's cart
        existing_cart_item = CartItem.objects.filter(user=request.user, sanpham=sanpham).first()

        if existing_cart_item:
            # If the product already exists, update the quantity
            existing_cart_item.quantity += 1
            existing_cart_item.save()
            if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({'message': 'Sản phẩm đã có trong giỏ hàng. Số lượng đã được cập nhật.'}, status=200)
            else:
                return redirect('cart')
        else:
            # If the product does not exist in the cart, create a new CartItem
            form = CartItemForm(user=request.user, data=request.POST, instance=CartItem(sanpham=sanpham, user=request.user))
            if form.is_valid():
                form.save()
                if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                    return JsonResponse({'message': 'Đã thêm vào giỏ hàng!'}, status=200)
                else:
                    return redirect('cart')
    else:
        form = CartItemForm(user=request.user, instance=CartItem(sanpham=sanpham, user=request.user))

    context = {
        'sanpham': sanpham,
        'form': form,
        'DM_loai': DM_loai,
    }

    return render(request, 'page/add_to_cart.html', context)

#Hàm giỏ hàng
def cart(request):
    DM_loai = Loai.objects.all()
    cart_items = CartItem.objects.all()
    total = sum(item.subtotal() for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total': total,
        'DM_loai': DM_loai,
    }

    return render(request, 'page/cart.html', context)
#Xóa sản phẩm khỏi giỏ hàng
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk)
    cart_item.delete()

    return redirect('cart')
#Hàm tìm kiếm sản phẩm
def tim_kiem_san_pham(request):
    DM_loai = Loai.objects.all()
    query = request.GET.get('q')

    if query:
        sanphams = SanPham.objects.filter(TenSP__icontains=query)
    else:
        sanphams = SanPham.objects.all()

    context = {
        'sanphams': sanphams,
        'query': query,
        'DM_loai': DM_loai,
    }
    return render(request, 'page/ketQuaTimKiem.html', context)

#Hàm đăng xuất 
def logout_view(request):
    DM_loai = Loai.objects.all()
    if request.method == 'POST':
        logout(request)
        return redirect('index')  
    context = {
        'DM_loai': DM_loai,
    }
    return render(request, 'page/logout_confirm.html', context)
# View Giỏ hàng
def cart_view(request):
    DM_loai = Loai.objects.all()
    # Lấy người dùng hiện tại
    user = request.user
    
    # Lọc các mục CartItem dựa trên người dùng hiện tại
    cart_items = CartItem.objects.filter(user=user)
    
    # Tính tổng giá trị giỏ hàng
    total = sum(item.subtotal() for item in cart_items)
    
    # Truyền các mục CartItem vào context
    context = {
        'cart_items': cart_items,
        'total': total,
        'DM_loai': DM_loai,
    }
    
    return render(request, 'page/cart.html', context)
# Tăng số lượng trong giỏ hàng 
def increase_quantity(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk)
    sanpham = cart_item.sanpham

    if cart_item.quantity < sanpham.SoLuong:
        cart_item.quantity += 1
        cart_item.save()
    else:
        # Optional: Add a message to inform the user that the quantity cannot be increased
        return JsonResponse({'error': 'Số lượng trong giỏ hàng không thể vượt quá số lượng có sẵn'}, status=400)

    return redirect('cart')
#Hàm giảm số lượng trong giỏ hàng
def decrease_quantity(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')
#Hàm thanh toán
@login_required
def thanh_toan(request):
    if request.method == 'POST':
        # Lấy tất cả các mục trong giỏ hàng của người dùng
        cart_items = CartItem.objects.filter(user=request.user)

        if cart_items.exists():  # Kiểm tra xem giỏ hàng có mục nào không
            # Bắt đầu giao dịch để đảm bảo tính nhất quán trong dữ liệu
            with transaction.atomic():
                # Tính tổng tiền của giỏ hàng
                total_amount = sum(cart_item.subtotal() for cart_item in cart_items)

                # Lấy địa chỉ giao hàng từ POST request
                shipping_address = request.POST.get('shipping_address', '')

                # Lưu thông tin đơn hàng
                payment_method = 'Thanh toán khi nhận hàng'  # Phương thức thanh toán mặc định

                order = Order.objects.create(
                    user=request.user,
                    total_amount=total_amount,
                    shipping_address=shipping_address,
                    payment_method=payment_method
                )

                # Duyệt qua từng mục trong giỏ hàng để tạo các mục đơn hàng
                for cart_item in cart_items:
                     # Tạo một đối tượng OrderItem từ mỗi CartItem
                    OrderItem.objects.create(
                        order=order,
                        sanpham=cart_item.sanpham,
                        quantity=cart_item.quantity,
                        price=cart_item.sanpham.DonGia,
                        total=cart_item.subtotal()
                    )

                    # Giảm số lượng sản phẩm trong kho
                    sanpham = cart_item.sanpham
                    sanpham.SoLuong -= cart_item.quantity
                    sanpham.save()

                    # Thêm người dùng vào danh sách đã mua của sản phẩm
                    sanpham.buyers.add(request.user)
                    sanpham.save()

                # Xoá các mục trong giỏ hàng của người dùng
                cart_items.delete()

            # Gửi về trang thành công và truyền thông tin đơn hàng
            return render(request, 'page/thanh_toan_thanh_cong.html', {'orders': [order]})

    # Nếu không phải là phương thức POST hoặc giỏ hàng trống, redirect về trang giỏ hàng
    return redirect('cart')
#Hàm danh sách đơn hàng đã mua của User
@login_required
def view_orders(request):
    DM_loai = Loai.objects.all()
    user_orders = Order.objects.filter(user=request.user)  # Lấy danh sách đơn hàng của user đang đăng nhập
    context = {
        'DM_loai': DM_loai,
        'user': request.user,
        'orders': user_orders,
    }
    return render(request, 'page/orders.html', context)

#Hàm gửi tin nhắn

@login_required
def send_message(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('inbox')  # Redirect to inbox after sending message
    else:
        form = MessageForm()

    return render(request, 'page/send_message.html', {'form': form, 'receiver': receiver})

@login_required
def inbox(request):
    received_messages = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    receiver_id = request.user.id  # Lấy ID của người dùng đang đăng nhập
    receiver = User.objects.get(id=receiver_id)  # Lấy thông tin người dùng từ ID
    return render(request, 'page/inbox.html', {'received_messages': received_messages, 'receiver': receiver})
@login_required
def add_comment(request, pk):
    # Lấy sản phẩm dựa vào pk (primary key)
    sanpham = get_object_or_404(SanPham, pk=pk)

    if request.method == 'POST':
        # Lấy nội dung bình luận từ form POST
        body = request.POST.get('body')

        # Tạo bình luận mới
        comment = Comment(user=request.user, sanpham=sanpham, body=body)
        comment.save()

        # Điều hướng người dùng đến trang chi tiết sản phẩm sau khi bình luận thành công
        return redirect('chiTietSanPham', pk=sanpham.pk)
    
    # Nếu không phải là POST request, hoặc form không hợp lệ, có thể xử lý thêm logic ở đây
    # Ví dụ: trả về một template để hiển thị form bình luận

    # Trường hợp này, có thể sử dụng redirect hoặc render template để xử lý.
    # Ở đây mình chỉ đơn giản redirect khi bình luận thành công.
    return redirect('chiTietSanPham', pk=sanpham.pk)

def submit_rating(request, pk):
    sanpham = get_object_or_404(SanPham, pk=pk)
    user = request.user

    # Kiểm tra xem người dùng đã mua sản phẩm chưa
    if user not in sanpham.buyers.all():
        messages.error(request, "Bạn cần mua sản phẩm này trước khi có thể đánh giá.")
        return redirect('chiTietSanPham', pk=pk)

    # Kiểm tra xem người dùng đã đánh giá sản phẩm này chưa
    if DanhGia.objects.filter(sanpham=sanpham, user=user).exists():
        messages.error(request, "Bạn đã đánh giá sản phẩm này rồi.")
        return redirect('chiTietSanPham', pk=pk)

    if request.method == 'POST':
        rating_form = RatingForm(request.POST)
        if rating_form.is_valid():
            rating = rating_form.save(commit=False)
            rating.sanpham = sanpham
            rating.user = user
            rating.save()
            messages.success(request, "Cảm ơn bạn đã đánh giá sản phẩm.")
            return redirect('chiTietSanPham', pk=pk)
    else:
        rating_form = RatingForm()

    return render(request, 'page/chiTietSanPham.html', {'rating_form': rating_form, 'sanpham': sanpham})