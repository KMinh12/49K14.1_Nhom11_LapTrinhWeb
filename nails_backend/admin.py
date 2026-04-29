from django.contrib import admin
from django.apps import apps
from .models import User
# Thay đổi dòng chữ "Django administration" ở trang đăng nhập
admin.site.site_header = "HỆ THỐNG QUẢN LÝ 2000 NAILS & EYELASH"
# Thay đổi chữ "Site administration" ở trang chủ Admin
admin.site.index_title = "Bảng điều khiển quản trị"
# Thay đổi tiêu đề trên tab trình duyệt
admin.site.site_title = "2000 NAILS & EYELASH"

# Lấy tất cả các models từ app 'nails_backend'
app_models = apps.get_app_config('nails_backend').get_models()

for model in app_models:
    # 1. Kiểm tra nếu là model User thì cấu hình riêng theo yêu cầu của bạn
    if model == User:
        class UserAdminCustom(admin.ModelAdmin):
            # Hiển thị đúng các cột: ID, Role, Họ và Tên, Phone Number
            list_display = ('id', 'role', 'full_name', 'phone_number')
            search_fields = ('full_name', 'phone_number', 'username')
            list_filter = ('role',)  # Thêm bộ lọc bên phải theo Role cho tiện

        try:
            admin.site.register(User, UserAdminCustom)
        except admin.sites.AlreadyRegistered:
            pass

    # 2. Đối với các model khác, tiếp tục hiển thị tất cả các cột tự động
    else:
        class DynamicAdmin(admin.ModelAdmin):
            list_display = [field.name for field in model._meta.fields]
            # Tự động tạo ô tìm kiếm nếu có các trường tên thông dụng
            search_fields = [f.name for f in model._meta.fields if
                             f.name in ['name', 'full_name', 'employee_code', 'customer_code']]

        try:
            admin.site.register(model, DynamicAdmin)
        except admin.sites.AlreadyRegistered:
            pass