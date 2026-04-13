from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from datetime import time


# ==========================================
# 1. BẢNG NGƯỜI DÙNG (CỔNG XÁC THỰC CHUNG)
# ==========================================
class User(AbstractUser):
    class RoleType(models.TextChoices):
        MANAGER = 'MANAGER', 'Quản lý'
        STAFF = 'STAFF', 'Nhân viên'
        CUSTOMER = 'CUSTOMER', 'Khách hàng'

    role = models.CharField(max_length=10, choices=RoleType.choices, default=RoleType.CUSTOMER)

    phone_regex = RegexValidator(regex=r'^\d{10}$', message="Số điện thoại phải có đúng 10 chữ số.")
    phone_number = models.CharField(validators=[phone_regex], max_length=10, unique=True, null=True, blank=True)

    # Thêm trường Họ và tên gộp chung
    full_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Họ và tên")
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # Thêm dòng này
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',  # Thêm dòng này
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='user',
    )

    def __str__(self):
        # Ưu tiên hiển thị full_name, nếu chưa nhập thì hiển thị username
        return self.full_name or self.username


# ==========================================
# 2. BẢNG NHÂN VIÊN
# ==========================================
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_code = models.CharField(max_length=20, unique=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Nam'), ('F', 'Nữ'), ('O', 'Khác')])
    salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # Cấu hình giờ làm việc mặc định
    start_working_hour = models.TimeField(default=time(8, 0))
    end_working_hour = models.TimeField(default=time(22, 0))

    def __str__(self):
        return self.user.full_name or self.user.username


# ==========================================
# 3. BẢNG KHÁCH HÀNG
# ==========================================
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    customer_code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.user.full_name or self.user.username


# ==========================================
# 4. BẢNG DỊCH VỤ
# ==========================================
class Service(models.Model):
    name = models.CharField(max_length=255)
    duration = models.IntegerField(help_text="Thời gian làm (phút)")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Giá (VNĐ)")
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='services/', null=True, blank=True)

    # Cờ đánh dấu xóa mềm
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# ==========================================
# 5. BẢNG KHUYẾN MÃI
# ==========================================
class Promotion(models.Model):
    class PromoType(models.TextChoices):
        PERCENT = 'PERCENT', 'Giảm theo %'
        AMOUNT = 'AMOUNT', 'Giảm theo tiền'

    class PromoStatus(models.TextChoices):
        UPCOMING = 'UPCOMING', 'Sắp diễn ra'
        ACTIVE = 'ACTIVE', 'Đang áp dụng'
        EXPIRED = 'EXPIRED', 'Hết hạn'

    name = models.CharField(max_length=255)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='promotions')
    promo_type = models.CharField(max_length=10, choices=PromoType.choices)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=PromoStatus.choices, default=PromoStatus.UPCOMING)
    conditions = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


# ==========================================
# 6. BẢNG LỊCH ĐẶT (BOOKING)
# ==========================================
class Booking(models.Model):
    class BookingStatus(models.TextChoices):
        PENDING = 'PENDING', 'Chờ xác nhận'
        CONFIRMED = 'CONFIRMED', 'Đã xác nhận'
        COMPLETED = 'COMPLETED', 'Đã hoàn thành'
        CANCELED = 'CANCELED', 'Đã hủy'

    # Nối trực tiếp Khách - Thợ - Dịch vụ
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='bookings')
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='bookings')

    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=BookingStatus.choices, default=BookingStatus.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Đưa lịch mới nhất lên đầu
        ordering = ['-booking_date', '-start_time']

    def __str__(self):
        return f"Booking {self.id} - {self.customer.user.full_name or self.customer.user.username}"


# ==========================================
# 7. BẢNG THÔNG BÁO
# ==========================================
class Notification(models.Model):
    class NotificationType(models.TextChoices):
        EMAIL = 'EMAIL', 'Email'
        SMS = 'SMS', 'Tin nhắn SMS'
        SYSTEM = 'SYSTEM', 'Hệ thống'

    class NotificationStatus(models.TextChoices):
        PENDING = 'PENDING', 'Chờ gửi'
        SENT = 'SENT', 'Đã gửi'
        FAILED = 'FAILED', 'Gửi thất bại'

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='notifications')
    noti_type = models.CharField(max_length=10, choices=NotificationType.choices, default=NotificationType.EMAIL)
    status = models.CharField(max_length=10, choices=NotificationStatus.choices, default=NotificationStatus.PENDING)

    title = models.CharField(max_length=255)
    content = models.TextField()

    scheduled_time = models.DateTimeField(help_text="Thời gian dự kiến gửi")
    sent_at = models.DateTimeField(null=True, blank=True, help_text="Thời gian thực tế đã gửi")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.status}] Booking ID: {self.booking.id}"


# ==========================================
# 8. BẢNG ĐÁNH GIÁ
# ==========================================
class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review {self.rating} stars for Booking {self.booking.id}"


