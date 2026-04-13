from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    ServiceViewSet, EmployeeViewSet, BookingViewSet, UserProfileView
)

# Khởi tạo router để tự động tạo các đường dẫn API
router = DefaultRouter()

# 1. Đăng ký các ViewSet (Cho phép các thao tác GET, POST, PUT, DELETE)
router.register(r'services', ServiceViewSet, basename='service')    # /api/services/
router.register(r'employees', EmployeeViewSet, basename='employee')  # /api/employees/
router.register(r'bookings', BookingViewSet, basename='booking')    # /api/bookings/
# router.register(r'promotions', PromotionViewSet, basename='promotion') # /api/promotions/
app_name = 'nv'
urlpatterns = [
    path('', views.DangNhap_QLNV, name='DangNhap_QLNV'),
    # Kết nối toàn bộ các đường dẫn từ router
    path('api/', include((router.urls, 'api'))),

    # 2. Đường dẫn riêng cho hồ sơ cá nhân (Tương ứng file quản lý tài khoản.pdf)
    # Vì UserProfileView là generics.RetrieveUpdateAPIView (không phải ViewSet) nên khai báo riêng
    path('profile/', UserProfileView.as_view(), name='user-profile'),

    # Trang chủ nhân viên
    path('TrangChu_NV/', views.TrangChu_NV, name='TrangChu_NV'),

    # Quản lý ca làm cá nhân (bạn sẽ tạo sau)
    path('QuanLyCaLam_NV/', views.QuanLyCaLam_NV, name='QuanLyCaLam_NV'),

    # Quản lý tài khoản cá nhân (bạn sẽ tạo sau)
    path('QuanLyTaiKhoan_NV/', views.QuanLyTaiKhoan_NV, name='QuanLyTaiKhoan_NV'),

    # Đăng nhập chung (QL + NV)
    path('DangNhap_QLNV/', views.DangNhap_QLNV, name='DangNhap_QLNV'),

    # Đăng xuất
    path('DangXuat/', views.DangXuat, name='DangXuat'),
]