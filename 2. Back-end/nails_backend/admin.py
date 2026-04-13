from django.contrib import admin
from django.apps import apps
from .models import User, Employee  # Nhớ import thêm Employee ở đây

# Thay đổi dòng chữ "Django administration" ở trang đăng nhập
admin.site.site_header = "HỆ THỐNG QUẢN LÝ 2000 NAILS & EYELASH"
# Thay đổi chữ "Site administration" ở trang chủ Admin
admin.site.index_title = "Bảng điều khiển quản trị"
# Thay đổi tiêu đề trên tab trình duyệt
admin.site.site_title = "2000 NAILS & EYELASH"


# 1. Cấu hình riêng cho bảng User (Tài khoản)
class UserAdminCustom(admin.ModelAdmin):
    # Hiển thị thêm cột is_active để dễ theo dõi tài khoản nào bị khóa
    list_display = ('id', 'username', 'role', 'full_name', 'phone_number', 'is_active')
    search_fields = ('full_name', 'phone_number', 'username')
    list_filter = ('role', 'is_active')


# 2. Cấu hình riêng cho bảng Employee (Nhân viên)
class EmployeeAdminCustom(admin.ModelAdmin):
    # Hiển thị các cột của Employee và thêm cột trạng thái lấy từ User
    list_display = ('id', 'employee_code', 'get_full_name', 'is_user_active')
    search_fields = ('employee_code', 'user__full_name', 'user__phone_number')
    list_filter = ('gender',)

    # Hàm lấy Họ tên từ bảng User liên kết
    def get_full_name(self, obj):
        return obj.user.full_name

    get_full_name.short_description = 'Họ và tên'

    # Hàm lấy trạng thái Active từ bảng User liên kết
    def is_user_active(self, obj):
        return obj.user.is_active

    is_user_active.boolean = True  # Hiển thị icon xanh (True) / đỏ (False)
    is_user_active.short_description = 'Trạng thái (Active)'


# 3. Đăng ký các Model đặc biệt trước
try:
    admin.site.register(User, UserAdminCustom)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(Employee, EmployeeAdminCustom)
except admin.sites.AlreadyRegistered:
    pass

# 4. Tự động đăng ký tất cả các models còn lại trong app 'nails_backend'
app_models = apps.get_app_config('nails_backend').get_models()

for model in app_models:
    # Bỏ qua những model đã được đăng ký thủ công ở trên
    if model == User or model == Employee:
        continue


    class DynamicAdmin(admin.ModelAdmin):
        list_display = [field.name for field in model._meta.fields]
        search_fields = [f.name for f in model._meta.fields if
                         f.name in ['name', 'full_name', 'employee_code', 'customer_code']]


    try:
        admin.site.register(model, DynamicAdmin)
    except admin.sites.AlreadyRegistered:
        pass