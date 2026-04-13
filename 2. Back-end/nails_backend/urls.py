from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    ServiceViewSet,
    EmployeeViewSet,
    BookingViewSet,
    UserProfileView
)

router = DefaultRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'bookings', BookingViewSet, basename='booking')

app_name = 'nails_backend'

urlpatterns = [
    # API
    path('api/', include(router.urls)),
    path('profile/', UserProfileView.as_view(), name='user-profile'),

    # ==================== KHÁCH HÀNG ====================
    path('TrangChu_KH/', views.TrangChu_KH, name='TrangChu_KH'),
    path('TrangChu_KH_AfterLogin/', views.TrangChu_KH_AfterLogin, name='TrangChu_KH_AfterLogin'),

    path('DangNhap_KH/', views.DangNhap_KH, name='DangNhap_KH'),
    path('DangXuat_KH/', views.DangXuat_KH, name='DangXuat_KH'),  # Tách riêng

    path('DatLichHen/', views.DatLichHen, name='DatLichHen'),
    path('LichHenCuaToi/', views.LichHenCuaToi, name='LichHenCuaToi'),
    path('QuanLyTaiKhoan_KH/', views.QuanLyTaiKhoan_KH, name='QuanLyTaiKhoan_KH'),

    # ==================== NHÂN VIÊN & QUẢN LÝ ====================
    path('', views.DangNhap_QLNV, name='DangNhap_QLNV'),
    path('TrangChu_NV/', views.TrangChu_NV, name='TrangChu_NV'),
    path('TrangChu_QL/', views.TrangChu_QL, name='TrangChu_QL'),
    path('DangXuat_QLNV/', views.DangXuat_QLNV, name='DangXuat_QLNV'),  # Tách riêng
    path('QuanLyCaLam_NV/', views.QuanLyCaLam_NV, name='QuanLyCaLam_NV'),
    path('QuanLyTaiKhoan_NV/', views.QuanLyTaiKhoan_NV, name='QuanLyTaiKhoan_NV'),
    path('quan-ly/dich-vu/', views.quan_ly_dv_view, name='quan_ly_dv'),
    path('quan-ly/dich-vu/save/', views.save_service_api, name='save_service_api'),
    path('quan-ly/dich-vu/delete/', views.delete_service_api, name='delete_service_api'),
    path('quan-ly/nhan-vien/', views.quan_ly_nv_view, name='quan_ly_nv'),
    path('quan-ly/nhan-vien/save/', views.save_employee_api, name='save_employee_api'),
    path('quan-ly/nhan-vien/delete/', views.delete_employee_api, name='delete_employee_api'),
]