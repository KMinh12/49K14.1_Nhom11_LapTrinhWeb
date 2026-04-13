from rest_framework import serializers
from .models import User, Employee, Booking, Service, Customer, Promotion, Review


# --- 1. SERIALIZER CHO TÀI KHOẢN (Sử dụng trong Quản lý tài khoản cá nhân) ---
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'phone_number', 'email', 'role', 'gender', 'birthday', 'address']
        # Mật khẩu chỉ dùng để ghi (đổi mật khẩu), không hiện ra khi xem
        extra_kwargs = {'password': {'write_only': True}}


# --- 2. SERIALIZER CHO DỊCH VỤ (Sử dụng trong Quản lý dịch vụ & Xem chi tiết) ---
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'duration', 'price', 'description', 'image']
        # Tương ứng với: Tên dịch vụ, Thời gian làm, Giá, Mô tả trong Xem.pdf


# --- 3. SERIALIZER CHO NHÂN VIÊN (Sử dụng trong Quản lý nhân viên) ---
class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'employee_code', 'full_name', 'phone_number', 'salary', 'user']
        # Tương ứng với bảng: Mã NV, Họ và tên NV, SĐT, Lương trong quản lý nhân viên_xoá.pdf


# --- 4. SERIALIZER CHO KHUYẾN MÃI (Sử dụng trong Quản lý khuyến mãi) ---
class PromotionSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = Promotion
        fields = ['id', 'name', 'description', 'discount_value', 'start_date', 'end_date', 'status', 'service',
                  'service_name']
        # Tương ứng với: Tên chương trình, Giá trị/mã, Thời gian và trạng thái trong thiết kế


# --- 5. SERIALIZER CHO ĐẶT LỊCH (Trọng tâm của Quản lý đặt lịch & Thông tin ca làm) ---
class BookingSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.user.full_name', read_only=True)
    customer_phone = serializers.CharField(source='customer.user.phone_number', read_only=True)
    employee_name = serializers.CharField(source='employee.user.full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'customer', 'customer_name', 'customer_phone',
            'service', 'service_name', 'employee', 'employee_name',
            'booking_date', 'start_time', 'end_time', 'status', 'total_price'
        ]
        # Các field này giúp hiển thị đúng bảng: Mã KH, Họ tên KH, SĐT, Thời gian hẹn, Trạng thái...


# --- 6. SERIALIZER CHI TIẾT CA LÀM (Phục vụ file Thong tin ca làm.pdf) ---
class BookingDetailSerializer(serializers.ModelSerializer):
    """Serializer mở rộng để hiển thị chi tiết chuẩn bị dụng cụ và mô tả dịch vụ"""
    service_detail = ServiceSerializer(source='service', read_only=True)

    class Meta: 
        model = Booking
        fields = [
            'booking_date', 'start_time', 'end_time', 'status',
            'service_detail', 'preparation_notes'  # Ghi chú chuẩn bị dụng cụ
        ]