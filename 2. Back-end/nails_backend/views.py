from django.shortcuts import render, redirect, reverse
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from .models import Service, Employee, Promotion, Booking, User
from .serializers import (
    ServiceSerializer, EmployeeSerializer, PromotionSerializer,
    BookingSerializer, UserSerializer, BookingDetailSerializer
)

# ====================== PHẦN KHÁCH HÀNG ======================

def TrangChu_KH(request):
    return render(request, 'KhachHang/TrangChu/TrangChu_KH.html')

def TrangChu_KH_AfterLogin(request):
    if not request.user.is_authenticated or request.user.role != 'CUSTOMER':
        return redirect('nails_backend:TrangChu_KH')
    return render(request, 'KhachHang/TrangChu/TrangChu_KH_AfterLogin.html', {'user': request.user})

def DangNhap_KH(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.role == 'CUSTOMER':
            login(request, user)
            return JsonResponse({'success': True, 'redirect_url': '/TrangChu_KH_AfterLogin/'})
        else:
            return JsonResponse({'success': False, 'message': 'Tên đăng nhập hoặc mật khẩu không đúng!'})
    return JsonResponse({'success': False, 'message': 'Yêu cầu không hợp lệ'}, status=400)

def DangXuat_KH(request):
    logout(request)
    return redirect('nails_backend:TrangChu_KH')

def DatLichHen(request):
    if not request.user.is_authenticated or request.user.role != 'CUSTOMER':
        return redirect('nails_backend:TrangChu_KH')
    services = Service.objects.filter(is_active=True)
    return render(request, 'KhachHang/DatLich/DatLich_KH.html', {'user': request.user, 'services': services})

def LichHenCuaToi(request):
    if not request.user.is_authenticated or request.user.role != 'CUSTOMER':
        return redirect('nails_backend:TrangChu_KH')
    bookings = Booking.objects.filter(customer__user=request.user).order_by('-booking_date', '-start_time')
    return render(request, 'KhachHang/LichHen/LichHen_KH.html', {'user': request.user, 'bookings': bookings})

def QuanLyTaiKhoan_KH(request):
    if not request.user.is_authenticated or request.user.role != 'CUSTOMER':
        return redirect('nails_backend:TrangChu_KH')
    return render(request, 'KhachHang/QuanLyTaiKhoan/TaiKhoan_KH.html', {'user': request.user})

# ==================== PHẦN QUẢN LÝ & NHÂN VIÊN ====================

def DangNhap_QLNV(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')  # Lấy từ radio button ('quanly' hoặc 'nhanvien')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # KIỂM TRA QUYỀN TRUY CẬP
            if role == 'quanly' and not user.is_staff:
                return JsonResponse({
                    "success": False,
                    "message": "Tài khoản này không có quyền Quản lý."
                })

            if role == 'nhanvien' and user.is_staff:
                return JsonResponse({
                    "success": False,
                    "message": "Tài khoản Quản lý vui lòng chọn đúng vai trò."
                })

            login(request, user)

            # Tạo URL chuyển hướng dựa trên tên (name) đã đặt trong urls.py
            if role == 'quanly':
                redirect_url = reverse('nails_backend:TrangChu_QL')
            else:
                redirect_url = reverse('nails_backend:TrangChu_NV')

            return JsonResponse({
                "success": True,
                "message": "Đăng nhập thành công!",
                "redirect_url": redirect_url
            })
        else:
            return JsonResponse({
                "success": False,
                "message": "Tài khoản hoặc mật khẩu không chính xác."
            })

    return render(request, 'DangNhap/DangNhap_QLNV.html')

def TrangChu_QL(request):
    return render(request, 'QuanLy/TrangChu/TrangChu_QL.html')

def TrangChu_NV(request):
    context = {
        'ten_nhan_vien': getattr(request.user, 'ten_nhan_vien', 'Nhân viên'),
    }
    return render(request, 'NhanVien/TrangChu/TrangChu_NV.html', context)

def QuanLyCaLam_NV(request):
    # Đường dẫn khớp với cấu trúc QuanLy/QuanLyCaLamCaNhan/
    return render(request, 'QuanLy/QuanLyCaLamCaNhan/QuanLyCaLamCaNhan_NV.html')

def QuanLyTaiKhoan_NV(request):
    # Bạn sẽ tạo file này sau trong thư mục templates phù hợp
    return render(request, 'QuanLy/QuanLyTaiKhoan_NV.html')

def DangXuat_QLNV(request):
    logout(request)
    return redirect('nails_backend:DangNhap_QLNV')

# ==================== API VIEWSETS (GIỮ NGUYÊN) ====================

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by('-id')
    serializer_class = ServiceSerializer
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if Booking.objects.filter(service=instance).exists():
            return Response({"error": "Đã có lịch đặt không thể xoá."}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('employee_code')
    serializer_class = EmployeeSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().order_by('-booking_date')
    serializer_class = BookingSerializer
    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        booking = self.get_object()
        serializer = BookingDetailSerializer(booking)
        return Response(serializer.data)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user