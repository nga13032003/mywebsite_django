from django import forms 
from .models import Comment 
import re
from django.contrib.auth.models import User
# from .models import Comment
from django.shortcuts import render
from .models import SanPham
from .models import Loai, DanhGia
from .models import CartItem
from django.contrib.auth.forms import AuthenticationForm
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }
def register_view(request):
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()  # Save the form data
        # Redirect to a success page or return a response
    return render(request, 'page/dangky.html', {'form': form})

class RegistrationForm(forms.Form): 
    username = forms.CharField(label='Tài khoản') 
    email = forms.EmailField(label='Email') 
    password1 = forms.CharField(label='Mật khẩu',  
   widget = forms.PasswordInput()) 
    password2 = forms.CharField(label='Nhập lại mật khẩu',  
   widget=forms.PasswordInput()) 

    def clean_password2(self): 
        if 'password1' in self.cleaned_data: 
            password1 = self.cleaned_data['password1'] 
            password2 = self.cleaned_data['password2'] 
            if password1 == password2 and password1: 
                return password2 
        raise forms.ValidationError("Mật khẩu không hợp lệ")
    def clean_username(self): 
        username = self.cleaned_data['username'] 
        if not re.search(r'^\w+$', username): 
            raise forms.ValidationError("Tên tài khoản có kí tự đặc biệt") 
        try: 
            User.objects.get(username=username) 
        except User.DoesNotExist: 
            return username 
        raise forms.ValidationError("Tài khoản đã tồn tại") 
 
    def save(self): 
        User.objects.create_user(username=self.cleaned_data['username'],  
        email=self.cleaned_data['email'],  
       password=self.cleaned_data['password1'])
#class comment
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']  # Chỉ lấy trường 'body' từ model Comment

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Nhận thêm user từ kwargs
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        comment = super().save(commit=False)
        if self.user:
            comment.user = self.user  # Gán user vào comment nếu có
        comment.save()
        return comment


class TheLoaiForm(forms.Form):
    TenLoai = forms.CharField(label='Tên thể loại', max_length=100)

    def clean_TenLoai(self):
        TenLoai = self.cleaned_data['TenLoai']
        try:
            Loai.objects.get(TenLoai=TenLoai)
        except Loai.DoesNotExist:
            return TenLoai
        raise forms.ValidationError("Tên thể loại đã tồn tại")

    def save(self):
        Loai.objects.create(TenLoai=self.cleaned_data['TenLoai'])


class SanPhamForm(forms.ModelForm):
    class Meta:
        model = SanPham
        fields = ['TenSP', 'DonGia', 'HinhAnh', 'MoTa', 'MaLoai', 'SoLuong', 'khuyen_mai']
from django import forms
from .models import CartItem

class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CartItemForm, self).__init__(*args, **kwargs)

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        sanpham = self.instance.sanpham

        if quantity > sanpham.SoLuong:
            raise forms.ValidationError(f"Số lượng không được vượt quá {sanpham.SoLuong}.")

        return quantity
    
def should_be_empty(value):
    if value:
        raise forms.ValidationError('Field is not empty')
    
class ContactForm(forms.Form):
    name = forms.CharField(max_length=80)
    message = forms.CharField(widget=forms.Textarea)
    email = forms.EmailField()
    forcefield = forms.CharField(
        required=False, widget=forms.HiddenInput, label="Leave empty", validators=[should_be_empty])
class PasswordResetForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=254)

class RatingForm(forms.ModelForm):
    class Meta:
        model = DanhGia
        fields = ['rating']

    def __init__(self, *args, **kwargs):
        super(RatingForm, self).__init__(*args, **kwargs)
        
        # Thêm class CSS cho các sao
        self.fields['rating'].widget.attrs.update({
            'class': 'rating-widget',  # Đây là class CSS để tùy chỉnh giao diện
        })

        # Tạo các sao nhấp vào để đánh giá
        self.fields['rating'].widget.template_name = 'widgets/rating_widget.html'  # Đường dẫn đến template rating_widget.html
        
        # Optional: Có thể thêm nhãn cho form nếu cần
        self.fields['rating'].label = 'Đánh giá của bạn'
