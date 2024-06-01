from django.urls import path 
from . import views   
from django.contrib.auth import views as auth_views 
from .models import Post 
from django.views.generic import ListView 
from django.conf import settings
from django.conf.urls.static import static
from .views import logout_view
# call to url_shortener/views.py 
urlpatterns = [ 
    path('', views.index, name='index'), 
    path('DangKy/', views.register, name="register"),
    path('DangNhap/', auth_views.LoginView.as_view(template_name="page/dangnhap.html"), name="DangNhap"), 
    # path('DangXuat/', auth_views.LogoutView.as_view(next_page='/home'),name='DangXuat'),
    path('dstheLoai/', views.list, name='list'),
    # path('themLoai/', views.themLoai, name="themLoai"),
    path('DSSP/<int:ml>/', views.DSSPTheoLoai, name ='DSSPTheoLoai'),
    path('danhSachSanPham/', views.danhSachSanPham, name='danhSachSanPham'),
    # path('themSanPham/', views.themSanPham, name='themSanPham'),
    path('chiTietSanPham/<int:pk>/', views.chiTietSanPham, name='chiTietSanPham'),
    path('cart/', views.cart_view, name='cart'),  # Đổi 'views.cart' thành 'views.cart_view' để xem danh sách sản phẩm trong giỏ hàng
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('increase-quantity/<int:pk>/', views.increase_quantity, name='increase_quantity'),
    path('decrease-quantity/<int:pk>/', views.decrease_quantity, name='decrease_quantity'),
    path('DSSPTheoLoai/<int:MaLoai>/', views.DSSPTheoLoai, name='DSSPTheoLoai'),
    path('tim-kiem-san-pham/', views.tim_kiem_san_pham, name='tim_kiem_san_pham'),
    path('logout/', views.logout_view, name='logout'),
    path('thanhtoan/', views.thanh_toan, name='thanh_toan'),
    path('orders/', views.view_orders, name='view_orders'),
    path('send_message/<int:receiver_id>/', views.send_message, name='send_message'),
    path('inbox/', views.inbox, name='inbox'),
   #Quên mật khẩu - reset mật khẩu
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset_password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    #comment
    path('comment/<int:pk>/', views.add_comment, name='add_comment'),
    #Đánh giá
    path('submit_rating/<int:pk>/', views.submit_rating, name='submit_rating'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)