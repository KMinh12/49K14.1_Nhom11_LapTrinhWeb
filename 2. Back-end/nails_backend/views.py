from django.db import transaction
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
import json
from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder

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


def quan_ly_dv_view(request):
    # Thêm filter(is_active=True) để không hiện các dịch vụ đã xóa mềm
    services_qs = Service.objects.filter(is_active=True).values(
        'id', 'name', 'duration', 'price', 'description', 'image'
    )

    services_list = list(services_qs)
    for service in services_list:
        service['time'] = service.pop('duration')
        if service['image']:
            service['image'] = '/media/' + service['image']
        else:
            service['image'] = ""

    services_json = json.dumps(services_list, cls=DjangoJSONEncoder)
    return render(request, 'QuanLy/QuanLyDichVu.html', {'services_json': services_json})


# 2. HÀM MỚI: Xử lý Thêm mới và Cập nhật (hỗ trợ cả file ảnh)
def save_service_api(request):
    if request.method == 'POST':
        service_id = request.POST.get('id')
        name = request.POST.get('name')
        duration = request.POST.get('time')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image = request.FILES.get('image')  # Lấy file ảnh nếu có

        if service_id:
            # Nếu có ID gửi lên -> CẬP NHẬT
            service = Service.objects.get(id=service_id)
            service.name = name
            service.duration = duration
            service.price = price
            service.description = description
            if image:
                service.image = image  # Chỉ cập nhật ảnh nếu user chọn ảnh mới
            service.save()
        else:
            # Nếu không có ID -> THÊM MỚI
            service = Service.objects.create(
                name=name,
                duration=duration,
                price=price,
                description=description,
                image=image
            )

        # Trả về dữ liệu vừa lưu thành công
        img_url = service.image.url if service.image else ""
        return JsonResponse({
            'status': 'success',
            'service': {
                'id': service.id,
                'name': service.name,
                'time': service.duration,
                'price': float(service.price),
                'description': service.description,
                'image': img_url
            }
        })
    return JsonResponse({'status': 'error'}, status=400)


# 3. HÀM MỚI: Xử lý Xóa mềm
def delete_service_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        service_id = data.get('id')

        # Tìm dịch vụ và chuyển is_active thành False
        service = Service.objects.get(id=service_id)
        service.is_active = False
        service.save()

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


def quan_ly_nv_view(request):

    employees_qs = Employee.objects.select_related('user').filter(user__is_active=True)

    employees_list = []
    for emp in employees_qs:
        employees_list.append({
            'id': emp.employee_code,
            'name': emp.user.full_name or "",
            'phone': emp.user.phone_number or "",
            'username': emp.user.username,
            # Ta không gửi password thật xuống frontend
        })

    employees_json = json.dumps(employees_list)
    return render(request, 'QuanLy/QuanLyNhanVien.html', {'employees_json': employees_json})


def save_employee_api(request):
    if request.method == 'POST':
        emp_code = request.POST.get('id')
        full_name = request.POST.get('name')
        phone = request.POST.get('phone')
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            with transaction.atomic():
                if emp_code:
                    # CẬP NHẬT
                    emp = Employee.objects.get(employee_code=emp_code)
                    user = emp.user
                    user.full_name = full_name
                    user.phone_number = phone
                    user.username = username
                    if password:  # Quản lý cấp lại mật khẩu mới
                        user.set_password(password)
                    user.save()
                else:
                    # TẠO MỚI
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        full_name=full_name,
                        phone_number=phone,
                        role='STAFF'
                    )

                    # SỬA LỖI Ở ĐÂY: Dùng zfill(3) thay vì padStart(3, '0')
                    last_emp = Employee.objects.order_by('-id').first()
                    new_num = (last_emp.id + 1) if last_emp else 1
                    new_code = f"NV{str(new_num).zfill(3)}"

                    emp = Employee.objects.create(
                        user=user,
                        employee_code=new_code
                    )

                return JsonResponse({
                    'status': 'success',
                    'employee': {
                        'id': emp.employee_code,
                        'name': user.full_name,
                        'phone': user.phone_number,
                        'username': user.username
                    }
                })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error'}, status=400)


def delete_employee_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        emp_code = data.get('id')

        try:
            emp = Employee.objects.get(employee_code=emp_code)
            user = emp.user
            # Xóa mềm bằng cách set is_active = False
            user.is_active = False
            user.save()
            return JsonResponse({'status': 'success'})
        except Employee.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Không tìm thấy nhân viên'}, status=404)

    return JsonResponse({'status': 'error'}, status=400)