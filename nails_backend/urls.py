from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
   ServiceViewSet,
   EmployeeViewSet,
   BookingViewSet,
   UserProfileView,
   CustomerRegisterView,
   BookingCreateAPIView
)

router = DefaultRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'promotions', views.PromotionViewSet, basename='promotion')
app_name = 'nails_backend'

urlpatterns = [
    # API
    path('api/bookings/create/', views.BookingCreateAPIView.as_view(), name='booking-create'),
    path('api/', include(router.urls)),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/cap-nhat-trang-thai-ca/', views.API_CapNhatTrangThaiCaLam, name='api_cap_nhat_trang_thai_ca'),
    path('api/cap-nhat-thong-tin/', views.API_CapNhatThongTin, name='api_cap_nhat_thong_tin'),  #thêm
    path('api/doi-mat-khau/', views.API_DoiMatKhau, name='api_doi_mat_khau'),
    # ==================== NHÂN VIÊN & QUẢN LÝ ====================
    path('quanly_nhanvien', views.DangNhap_QLNV, name='DangNhap_QLNV'),
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
    path('quan-ly/khach-hang/', views.quan_ly_kh_view, name='quan_ly_kh'),
    path('quan-ly/dat-lich/', views.quan_ly_dat_lich_view, name='quan_ly_dat_lich'),
    path('quan-ly/dat-lich/save/', views.save_booking_api, name='save_booking_api'),
    path('quan-ly/dat-lich/delete/', views.delete_booking_api, name='delete_booking_api'),
    path('quan-ly/tai-khoan/', views.quan_ly_tai_khoan_view, name='quan_ly_tai_khoan'),
    path('quan-ly/tai-khoan/update/', views.update_profile_api, name='update_profile_api'),
    path('quan-ly/tai-khoan/change-password/', views.change_password_api, name='change_password_api'),
    path('quan-ly/khuyen-mai/', views.quan_ly_km_view, name='quan_ly_km'),
    path('quan-ly/bao-cao/', views.quan_ly_bao_cao_view, name='quan_ly_bao_cao'),
    path('quan-ly/khuyen-mai/save/', views.save_promo_api, name='save_promo_api'),
    path('quan-ly/khuyen-mai/delete/', views.delete_promo_api, name='delete_promo_api'),
    # ==================== KHÁCH HÀNG ====================
    path('register/', CustomerRegisterView.as_view(), name='customer-register'),
    path('', views.TrangChu_KH, name='TrangChu_KH'),
    path('TrangChu_KH_AfterLogin/', views.TrangChu_KH_AfterLogin, name='TrangChu_KH_AfterLogin'),
    path('DangNhap_KH/', views.DangNhap_KH, name='DangNhap_KH'),
    path('DangXuat_KH/', views.DangXuat_KH, name='DangXuat_KH'),  # Tách riêng
    path('DatLichHen/', views.DatLichHen, name='DatLichHen'),
    path('LichHenCuaToi/', views.LichHenCuaToi, name='LichHenCuaToi'),
    path('huy-lich/<int:booking_id>/', views.HuyLich, name='huy-lich'),
    path('cap-nhat-lich/<int:booking_id>/', views.CapNhatLich, name='cap-nhat-lich'),
    path('danh-gia-lich/<int:booking_id>/', views.DanhGiaLich, name='danh-gia-lich'),
    path('QuanLyTaiKhoan_KH/', views.QuanLyTaiKhoan_KH, name='QuanLyTaiKhoan_KH'),
    path('api/customer/me/', views.current_customer_info, name='current_customer_info'),
    path('api/change-password/', views.change_password, name='change_password'),
]