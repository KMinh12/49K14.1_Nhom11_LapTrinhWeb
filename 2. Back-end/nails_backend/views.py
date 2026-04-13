from django.shortcuts import render,redirect

# Create your views here.
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

# --- QUẢN LÝ DỊCH VỤ (Tương ứng file quản lý dịch vụ_xoá.pdf) ---
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by('-id')
    serializer_class = ServiceSerializer

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({"message": "Tạo dịch vụ mới thành công."}, status=status.HTTP_201_CREATED) # Thành công-10.pdf

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({"message": "Dữ liệu dịch vụ đã được cập nhật thành công."}, status=status.HTTP_200_OK) # Thành công-7.pdf

    def destroy(self, request, *args, **kwargs):
        # Kiểm tra logic file Xoá.pdf: Nếu đã có lịch đặt thì không cho xóa
        instance = self.get_object()
        if Booking.objects.filter(service=instance).exists():
            return Response(
                {"error": "Đã có lịch đặt của khách hàng không thể xoá."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

# --- QUẢN LÝ NHÂN VIÊN (Tương ứng file quản lý nhân viên_xoá.pdf) ---
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('employee_code')
    serializer_class = EmployeeSerializer

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({"message": "Tạo nhân viên mới thành công."}, status=status.HTTP_201_CREATED) # Thành công-9.pdf

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({"message": "Dữ liệu nhân viên đã được cập nhật thành công."}, status=status.HTTP_200_OK) # Thành công-8.pdf

# --- QUẢN LÝ ĐẶT LỊCH & CHI TIẾT CA LÀM ---
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().order_by('-booking_date')
    serializer_class = BookingSerializer

    # Action phục vụ cho file "Thong tin ca làm.pdf"
    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        booking = self.get_object()
        serializer = BookingDetailSerializer(booking)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({"message": "Tạo ca làm mới thành công."}, status=status.HTTP_201_CREATED) # Thành công-2.pdf

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        # Trả về message cho file Thành công-3.pdf hoặc Thành công-11.pdf
        return Response({"message": "Cập nhật ca làm/đặt lịch thành công."}, status=status.HTTP_200_OK)

# --- QUẢN LÝ TÀI KHOẢN (Tương ứng file quản lý tài khoản.pdf) ---
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        # Nếu là đổi mật khẩu trả về Thành công-12.pdf, còn lại là Thành công.pdf
        message = "Cập nhật thông tin thành công."
        if 'password' in request.data:
            message = "Đổi mật khẩu thành công."
        return Response({"message": message}, status=status.HTTP_200_OK)

# ==================== ĐĂNG NHẬP ====================
def DangNhap_QLNV(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Chuyển hướng theo vai trò (tạm thời mặc định về NV)
            return JsonResponse({
                'success': True,
                'redirect_url': '/TrangChu_NV/'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Tên đăng nhập hoặc mật khẩu không đúng!'
            })

    return render(request, 'DangNhap_QLNV.html')


# ==================== TRANG CHỦ NHÂN VIÊN ====================
def TrangChu_NV(request):
    context = {
        'ten_nhan_vien': getattr(request.user, 'ten_nhan_vien', 'Nhân viên'),
    }
    return render(request, 'TrangChu_NV.html', context)


# ==================== CÁC TRANG KHÁC (để sau) ====================
def QuanLyCaLam_NV(request):
    return render(request, 'QuanLyCaLam_NV.html')      # bạn sẽ tạo file này sau

def QuanLyTaiKhoan_NV(request):
    return render(request, 'QuanLyTaiKhoan_NV.html')   # bạn sẽ tạo file này sau


def DangXuat(request):
    logout(request)
    return redirect('nv:DangNhap_QLNV')