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
    class Meta:
        model = Promotion
        fields = ['id', 'code', 'name', 'discount_percentage', 'start_date', 'end_date', 'description']

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

# --- 7. SERIALIZER Đăng Ký Tài khoản Khách hàng ---
class CustomerRegisterSerializer(serializers.ModelSerializer):
   password = serializers.CharField(write_only=True, min_length=6)
   full_name = serializers.CharField(required=True)
   phone_number = serializers.CharField(required=True)
   customer_code = serializers.CharField(required=False)  # sẽ tự tạo nếu không truyền


   class Meta:
       model = User
       fields = ['username', 'full_name', 'phone_number', 'email', 'password', 'customer_code']


   def validate_phone_number(self, value):
       if User.objects.filter(phone_number=value).exists():
           raise serializers.ValidationError("Số điện thoại đã tồn tại.")
       return value


   def validate_username(self, value):
       if User.objects.filter(username=value).exists():
           raise serializers.ValidationError("Tên đăng nhập đã tồn tại.")
       return value


   def create(self, validated_data):
       # Tách customer_code ra
       customer_code = validated_data.pop('customer_code', None)


       # Tạo User
       user = User.objects.create_user(
           username=validated_data['username'],
           password=validated_data['password'],
           full_name=validated_data.get('full_name'),
           phone_number=validated_data.get('phone_number'),
           email=validated_data.get('email', ''),
           role='CUSTOMER'
       )


       # Tạo Customer profile
       if not customer_code:
           # Tự tạo mã KH (ví dụ: KH + năm + số thứ tự)
           last_customer = Customer.objects.order_by('-id').first()
           next_id = (last_customer.id + 1) if last_customer else 1
           customer_code = f"KH{str(next_id).zfill(3)}"


       Customer.objects.create(
           user=user,
           customer_code=customer_code
       )


       return user


# --- 8. SERIALIZER Đặt lịch hẹn khách hàng ---


class BookingCreateSerializer(serializers.ModelSerializer):
   class Meta:
       model = Booking
       fields = ['service', 'employee', 'booking_date', 'start_time']


   def validate(self, data):
       service = data.get('service')
       employee = data.get('employee')
       booking_date = data.get('booking_date')
       start_time = data.get('start_time')


       if not all([service, employee, booking_date, start_time]):
           raise serializers.ValidationError("Thiếu thông tin đặt lịch.")


       # Tính toán end_time dự kiến dựa trên duration của dịch vụ
       from datetime import datetime, timedelta
       start_dt = datetime.combine(booking_date, start_time)
       end_time = (start_dt + timedelta(minutes=service.duration)).time()


       # Kiểm tra trùng lịch:
       # Một lịch mới trùng nếu: start_moi < end_cu AND end_moi > start_cu
       overlapping_bookings = Booking.objects.filter(
           employee=employee,
           booking_date=booking_date,
           status__in=['PENDING', 'CONFIRMED']
       ).filter(
           models.Q(start_time__lt=end_time) & models.Q(end_time__gt=start_time)
       )


       if overlapping_bookings.exists():
           raise serializers.ValidationError(
               {"start_time": "Nhân viên này đã có lịch trong khoảng thời gian bạn chọn."})


       # Gán thêm end_time vào dữ liệu đã validate để view sử dụng luôn
       data['end_time'] = end_time
       return data