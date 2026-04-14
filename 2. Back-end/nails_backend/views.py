from django.shortcuts import render, redirect, reverse
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.http import JsonResponse
from django.db.models import Sum, Count
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Booking # Nhớ kiểm tra xem đã import Booking chưa nhé
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.contrib.auth.decorators import login_required
from datetime import date
from rest_framework.decorators import api_view
from .models import Service, Employee, Promotion, Booking, User, Customer, Review
from .serializers import (
    ServiceSerializer, EmployeeSerializer, PromotionSerializer, BookingCreateSerializer,
    BookingSerializer, UserSerializer, BookingDetailSerializer, CustomerRegisterSerializer
)
def is_manager(user):
    return user.is_authenticated and getattr(user, 'role', None) == 'MANAGER'
# ====================== PHẦN KHÁCH HÀNG ======================


def TrangChu_KH(request):
   return render(request, 'KhachHang/TrangChu/TrangChu_KH.html')


def TrangChu_KH_AfterLogin(request):
   if not request.user.is_authenticated or request.user.role != 'CUSTOMER':
       return redirect('nails_backend:TrangChu_KH')
   return render(request, 'KhachHang/TrangChu/TrangChu_KH_AfterLogin.html', {'user': request.user})


def DangNhap_KH(request):
   if request.method == 'POST':
       username = request.POST.get('username')
       password = request.POST.get('password')
       user = authenticate(request, username=username, password=password)
       if user is not None and user.role == 'CUSTOMER':
           login(request, user)
           return JsonResponse({'success': True, 'redirect_url': '/TrangChu_KH_AfterLogin/'})
       else:
           return JsonResponse({'success': False, 'message': 'Tên đăng nhập hoặc mật khẩu không đúng!'})
   return JsonResponse({'success': False, 'message': 'Yêu cầu không hợp lệ'}, status=400)


def DangXuat_KH(request):
   logout(request)
   return redirect('nails_backend:TrangChu_KH')


def DatLichHen(request):
   if not request.user.is_authenticated or request.user.role != 'CUSTOMER':
       return redirect('nails_backend:TrangChu_KH')
   services = Service.objects.filter(is_active=True)
   return render(request, 'KhachHang/DatLich/DatLich_KH.html', {'user': request.user, 'services': services})




def LichHenCuaToi(request):
   # Kiểm tra đăng nhập + quyền CUSTOMER
   if not request.user.is_authenticated or request.user.role != 'CUSTOMER':
       return redirect('nails_backend:TrangChu_KH')   # hoặc trang đăng nhập khách hàng


   bookings = Booking.objects.filter(
       customer__user=request.user          # an toàn hơn sau khi đã check is_authenticated
   ).select_related('service', 'employee__user') \
    .order_by('-booking_date', '-start_time')


   return render(request, 'KhachHang/LichHen/LichHen_KH.html', {
       'user': request.user,
       'bookings': bookings
   })




# ====================== HUỶ LỊCH ======================
@login_required
def HuyLich(request, booking_id):
   if request.method == 'POST':
       booking = get_object_or_404(Booking, id=booking_id)


       # Chỉ cho phép khách hàng huỷ lịch của chính mình
       if booking.customer.user != request.user:
           return JsonResponse({'success': False, 'message': 'Bạn không có quyền huỷ lịch này'}, status=403)


       # Chỉ cho phép huỷ khi đang ở trạng thái PENDING hoặc CONFIRMED
       if booking.status in ['PENDING', 'CONFIRMED']:
           booking.status = 'CANCELED'
           booking.save()
           return JsonResponse({'success': True, 'message': 'Lịch hẹn đã được huỷ thành công!'})
       else:
           return JsonResponse({'success': False, 'message': 'Không thể huỷ lịch này'}, status=400)


   return JsonResponse({'success': False, 'message': 'Phương thức không hợp lệ'}, status=405)


# ====================== CẬP NHẬT LỊCH ======================
@login_required
def CapNhatLich(request, booking_id):
   if request.method == 'POST':
       booking = get_object_or_404(Booking, id=booking_id)


       # Kiểm tra quyền: Chỉ cho phép người đặt lịch tự sửa
       if booking.customer.user != request.user:
           return JsonResponse({'success': False, 'message': 'Bạn không có quyền cập nhật lịch này'}, status=403)


       # Chỉ cho phép cập nhật khi trạng thái đang PENDING
       if booking.status != 'PENDING':
           return JsonResponse({'success': False, 'message': 'Chỉ có thể cập nhật lịch đang chờ xác nhận'}, status=400)


       # Nhận dữ liệu dưới dạng chuỗi (String) từ giao diện
       service_id = request.POST.get('service')
       employee_id = request.POST.get('employee')
       booking_date_str = request.POST.get('booking_date')
       start_time_str = request.POST.get('start_time')


       try:
           from datetime import timedelta, datetime


           # 1. Ép kiểu chuỗi thành định dạng Date và Time của Python
           parsed_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
           parsed_time = datetime.strptime(start_time_str, '%H:%M').time()


           # 2. Lấy thông tin Dịch vụ MỚI để biết giá và thời gian làm
           new_service = get_object_or_404(Service, id=service_id)


           # 3. Tính toán lại thời gian kết thúc (end_time)
           start_dt = datetime.combine(parsed_date, parsed_time)
           new_end_time = (start_dt + timedelta(minutes=new_service.duration)).time()


           # 4. Ghi đè dữ liệu mới vào DB
           booking.service_id = service_id
           booking.employee_id = employee_id
           booking.booking_date = parsed_date
           booking.start_time = parsed_time
           booking.end_time = new_end_time
           booking.total_price = new_service.price  # Cập nhật lại giá tiền dịch vụ


           booking.save()
           return JsonResponse({'success': True, 'message': 'Cập nhật lịch hẹn thành công!'})


       except Exception as e:
           # In chi tiết lỗi ra màn hình Terminal (Console) của Pycharm để bạn dễ theo dõi
           print("Lỗi Cập nhật lịch:", str(e))
           return JsonResponse({'success': False, 'message': f'Dữ liệu lỗi: {str(e)}'}, status=400)


   return JsonResponse({'success': False, 'message': 'Phương thức không hợp lệ'}, status=405)


# ====================== ĐÁNH GIÁ LỊCH ======================
@login_required
def DanhGiaLich(request, booking_id):
   if request.method == 'POST':
       booking = get_object_or_404(Booking, id=booking_id)


       # Kiểm tra quyền: Chỉ cho phép người đặt tự đánh giá
       if booking.customer.user != request.user:
           return JsonResponse({'success': False, 'message': 'Bạn không có quyền đánh giá lịch này'}, status=403)


       # Chỉ cho phép đánh giá khi lịch đã hoàn thành (COMPLETED)
       if booking.status != 'COMPLETED':
           return JsonResponse({'success': False, 'message': 'Chỉ có thể đánh giá lịch đã hoàn thành'}, status=400)


       # Lấy dữ liệu từ form
       rating = request.POST.get('rating')
       comment = request.POST.get('comment', '')
       if not rating:
           return JsonResponse({'success': False, 'message': 'Vui lòng chọn số sao'}, status=400)

       try:
           rating = int(rating)
           if rating < 1 or rating > 5:
               raise ValueError

           # Dùng update_or_create để đề phòng khách bấm gửi 2 lần hoặc muốn sửa đánh giá
           Review.objects.update_or_create(
               booking=booking,
               defaults={
                   'rating': rating,
                   'comment': comment
               }
           )
           return JsonResponse({'success': True, 'message': 'Cảm ơn bạn đã đánh giá dịch vụ!'})


       except Exception as e:
           print("Lỗi lưu đánh giá:", str(e))
           return JsonResponse({'success': False, 'message': 'Dữ liệu không hợp lệ'}, status=400)

   return JsonResponse({'success': False, 'message': 'Phương thức không hợp lệ'}, status=405)


# ====================== QUẢN LÝ TÀI KHOẢN KHÁCH HÀNG ======================
def QuanLyTaiKhoan_KH(request):
    if not request.user.is_authenticated or request.user.role != 'CUSTOMER':
        return redirect('nails_backend:TrangChu_KH')

    user = request.user
    customer = getattr(user, 'customer_profile', None)

    if request.method == 'POST':
        action = request.POST.get('action')
        # Cập nhật thông tin cá nhân
        if action == 'update_info':
            user.full_name = request.POST.get('full_name', '').strip()
            user.email = request.POST.get('email', '').strip()
            user.phone_number = request.POST.get('phone_number', '').strip()
            user.gender = request.POST.get('gender', '').strip()
            user.address = request.POST.get('address', '').strip()

            birthday_str = request.POST.get('birthday', '').strip()
            if birthday_str:
                try:
                    user.birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date()
                except ValueError:
                    messages.error(request, 'Ngày sinh không đúng định dạng.')
                    return redirect('nails_backend:QuanLyTaiKhoan_KH')
            else:
                user.birthday = None

            user.save()
            messages.success(request, 'Cập nhật thông tin thành công.')
            return redirect('nails_backend:QuanLyTaiKhoan_KH')




        # Đổi mật khẩu
        elif action == 'change_password':
            current_password = request.POST.get('current_password', '').strip()
            new_password = request.POST.get('new_password', '').strip()
            confirm_password = request.POST.get('confirm_password', '').strip()

            if not current_password or not new_password or not confirm_password:
                messages.error(request, 'Vui lòng nhập đầy đủ thông tin đổi mật khẩu.')
                return redirect('nails_backend:QuanLyTaiKhoan_KH')

                if not user.check_password(current_password):
                    messages.error(request, 'Mật khẩu hiện tại không đúng.')
                    return redirect('nails_backend:QuanLyTaiKhoan_KH')

                if len(new_password) < 6:
                    messages.error(request, 'Mật khẩu mới phải có ít nhất 6 ký tự.')
                    return redirect('nails_backend:QuanLyTaiKhoan_KH')

                if new_password != confirm_password:
                    messages.error(request, 'Xác nhận mật khẩu không khớp.')
                    return redirect('nails_backend:QuanLyTaiKhoan_KH')

                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)

                messages.success(request, 'Đổi mật khẩu thành công.')
                return redirect('nails_backend:QuanLyTaiKhoan_KH')

        context = {
            'user': user,
            'customer': customer,
            'gender_display': user.get_gender_display() if hasattr(user, 'get_gender_display') and user.gender else '',
        }
        return render(request, 'KhachHang/QuanLyTaiKhoan/TaiKhoan_KH.html', context)

# ==================== PHẦN QUẢN LÝ & NHÂN VIÊN ====================

def DangNhap_QLNV(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')  # Lấy từ radio button ('quanly' hoặc 'nhanvien')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # KIỂM TRA QUYỀN TRUY CẬP
            if role == 'quanly' and not user.is_staff:
                return JsonResponse({
                    "success": False,
                    "message": "Tài khoản này không có quyền Quản lý."
                })

            if role == 'nhanvien' and user.is_staff:
                return JsonResponse({
                    "success": False,
                    "message": "Tài khoản Quản lý vui lòng chọn đúng vai trò."
                })

            login(request, user)

            # Tạo URL chuyển hướng dựa trên tên (name) đã đặt trong urls.py
            if role == 'quanly':
                redirect_url = reverse('nails_backend:TrangChu_QL')
            else:
                redirect_url = reverse('nails_backend:TrangChu_NV')

            return JsonResponse({
                "success": True,
                "message": "Đăng nhập thành công!",
                "redirect_url": redirect_url
            })
        else:
            return JsonResponse({
                "success": False,
                "message": "Tài khoản hoặc mật khẩu không chính xác."
            })

    return render(request, 'DangNhap/DangNhap_QLNV.html')

def TrangChu_QL(request):
    return render(request, 'QuanLy/TrangChu/TrangChu_QL.html')

def TrangChu_NV(request):
    # Kiểm tra đăng nhập và quyền hạn
    if not request.user.is_authenticated:
        return redirect('nails_backend:DangNhap_QLNV')

    context = {
        'ten_nhan_vien': getattr(request.user, 'full_name', 'Nhân viên'),
    }
    return render(request, 'NhanVien/TrangChu/TrangChu_NV.html', context)

def QuanLyCaLam_NV(request):
    context = {
        'ten_nhan_vien': getattr(request.user, 'full_name', 'Nhân viên'),
    }
    return render(request, 'NhanVien/QuanLyCaLamCaNhan/QuanLyCaLam_NV.html')


def QuanLyCaLam_QL(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('nails_backend:DangNhap_QLNV')

    from .models import Employee
    # Lấy danh sách nhân viên từ database
    employees = Employee.objects.select_related('user').all().order_by('id')

    shifts_data = []

    # enumerate(..., 1) giúp tạo số thứ tự bắt đầu từ 1
    for i, emp in enumerate(employees, start=1):
        # Tạo mã ca: CA- + số thứ tự được làm đầy bằng 3 chữ số (001, 002...)
        ma_ca_duy_nhat = f"CA-{str(i).zfill(3)}"

        shifts_data.append({
            "id": ma_ca_duy_nhat,
            "employee_name": emp.user.full_name,
            "work_date": "13/04/2026",
            "start_time": "08:00",
            "end_time": "12:00"
        })

    context = {
        'ten_quan_ly': getattr(request.user, 'full_name', 'Quản lý'),
        'shifts_json': json.dumps(shifts_data, cls=DjangoJSONEncoder),
    }
    return render(request, 'QuanLy/QuanLyCaLam/QuanLyCaLam_QL.html', context)

def QuanLyTaiKhoan_NV(request):
    context = {
        'ten_nhan_vien': getattr(request.user, 'full_name', 'Nhân viên'),
    }
    # Bạn sẽ tạo file này sau trong thư mục templates phù hợp
    return render(request, 'NhanVien/QuanLyTaiKhoanCaNhan/QuanLyTaiKhoan_NV.html')

def DangXuat_QLNV(request):
    logout(request)
    return redirect('nails_backend:DangNhap_QLNV')

# ==================== API VIEWSETS (GIỮ NGUYÊN) ====================
class PromotionViewSet(viewsets.ModelViewSet):
   queryset = Promotion.objects.select_related('service').all().order_by('-id')
   serializer_class = PromotionSerializer

   def update(self, request, *args, **kwargs):
       instance = self.get_object()
       if instance.status == 'EXPIRED':
           return Response(
               {'error': 'Chương trình đã hết hạn, không thể chỉnh sửa.'},
               status=status.HTTP_400_BAD_REQUEST
           )
       return super().update(request, *args, **kwargs)

   def destroy(self, request, *args, **kwargs):
       instance = self.get_object()
       if instance.status != 'EXPIRED':
           return Response(
               {'error': 'Chỉ có thể xoá chương trình đã hết hạn.'},
               status=status.HTTP_400_BAD_REQUEST
           )
       return super().destroy(request, *args, **kwargs)

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by('-id')
    serializer_class = ServiceSerializer
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if Booking.objects.filter(service=instance).exists():
            return Response({"error": "Đã có lịch đặt không thể xoá."}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

class EmployeeViewSet(viewsets.ModelViewSet):
   queryset = Employee.objects.all().order_by('employee_code')
   serializer_class = EmployeeSerializer


   @action(detail=True, methods=['get'], url_path='available-slots')
   def available_slots(self, request, pk=None):
       """API lấy lịch trống của nhân viên theo ngày"""
       try:
           employee = self.get_object()
       except Exception:
           return Response({"error": "Không tìm thấy nhân viên"}, status=404)


       date_str = request.query_params.get('date')


       if not date_str:
           return Response({"error": "Thiếu tham số date (YYYY-MM-DD)"}, status=400)


       try:
           booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
       except ValueError:
           return Response({"error": "Định dạng ngày không đúng (YYYY-MM-DD)"}, status=400)


       # 1. Lấy thời gian hiện tại để chặn đặt lịch trong quá khứ
       now = timezone.localtime()
       current_time = now.time()
       is_today = booking_date == now.date()
       start_hour = employee.start_working_hour
       end_hour = employee.end_working_hour


       # 2. Lấy danh sách lịch ĐÃ ĐẶT (chờ xác nhận hoặc đã xác nhận)
       existing_bookings = Booking.objects.filter(
           employee=employee,
           booking_date=booking_date,
           status__in=['PENDING', 'CONFIRMED']
       ).order_by('start_time')


       slots = []
       current = datetime.combine(booking_date, start_hour)
       end_time_limit = datetime.combine(booking_date, end_hour)


       while current < end_time_limit:
           slot_end = current + timedelta(minutes=30)
           slot_str = current.strftime('%H:%M')


           # Kiểm tra xem slot này có nằm trong quá khứ của ngày hôm nay không
           is_past = is_today and current.time() <= current_time


           # 3. Kiểm tra trùng lịch: Nếu khung giờ này nằm giữa start_time và end_time của một booking đã tồn tại
           # (end_time đã được tính = start_time + duration của dịch vụ ở bước tạo booking)
           is_booked = any(
               current < datetime.combine(booking_date, b.end_time) and
               slot_end > datetime.combine(booking_date, b.start_time)
               for b in existing_bookings
           )


           # Slot chỉ khả dụng khi KHÔNG bị đặt VÀ KHÔNG nằm trong quá khứ
           slots.append({
               'time': slot_str,
               'is_available': not is_booked and not is_past
           })
           current = slot_end


       return Response({
           'employee_id': employee.id,
           'date': date_str,
           'slots': slots
       })


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().order_by('-booking_date')
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    # Chỉ cho phép quản lý (Staff + Manager) xem danh sách và chi tiết
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'details']:
            return [IsAuthenticated()]  # Sau này có thể nâng thành permission cho quản lý
        return [IsAuthenticated()]

    # Sử dụng serializer phù hợp
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'details':
            return BookingDetailSerializer
        return BookingSerializer

    # === API CHI TIẾT BOOKING ===
    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        booking = self.get_object()
        # Chỉ cho phép xem booking của chính mình hoặc quản lý
        if booking.customer.user != request.user and not request.user.role in ['MANAGER', 'STAFF']:
            return Response({"error": "Bạn không có quyền xem lịch này"}, status=403)

        serializer = BookingDetailSerializer(booking)
        return Response(serializer.data)


# === API LẤY LỊCH TRỐNG CỦA NHÂN VIÊN ===
   # Giữ lại nhưng sửa để rõ ràng hơn: nên gọi qua Employee thay vì Booking
@action(detail=False, methods=['get'], url_path='available-slots')
def available_slots(self, request):
       """API lấy lịch trống theo employee_id và date"""
       employee_id = request.query_params.get('employee_id')
       date_str = request.query_params.get('date')


       if not employee_id or not date_str:
           return Response({"error": "Thiếu employee_id hoặc date"}, status=400)


       try:
           employee = Employee.objects.get(id=employee_id)
           booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
       except Employee.DoesNotExist:
           return Response({"error": "Không tìm thấy nhân viên"}, status=404)
       except ValueError:
           return Response({"error": "Định dạng ngày không đúng"}, status=400)


       # Lấy lịch đã đặt
       existing_bookings = Booking.objects.filter(
           employee=employee,
           booking_date=booking_date,
           status__in=['PENDING', 'CONFIRMED']
       ).order_by('start_time')


       # Tạo slot 30 phút
       slots = []
       current = datetime.combine(booking_date, employee.start_working_hour)
       end_time = datetime.combine(booking_date, employee.end_working_hour)


       while current < end_time:
           slot_end = current + timedelta(minutes=30)
           slot_str = current.strftime('%H:%M')


           is_booked = any(
               current < datetime.combine(booking_date, b.end_time) and
               slot_end > datetime.combine(booking_date, b.start_time)
               for b in existing_bookings
           )


           slots.append({
               'time': slot_str,
               'is_available': not is_booked
           })
           current = slot_end


       return Response({
           'employee_id': employee.id,
           'date': date_str,
           'slots': slots
       })

# Đăng ký Tài khoản Khách hàng
class CustomerRegisterView(generics.CreateAPIView):
   serializer_class = CustomerRegisterSerializer
   permission_classes = []


   def create(self, request, *args, **kwargs):
       serializer = self.get_serializer(data=request.data)
       if serializer.is_valid():
           user = serializer.save()
           return Response({
               "success": True,
               "message": "Đăng ký thành công!",
               "user": {
                   "id": user.id,
                   "username": user.username,
                   "full_name": user.full_name,
                   "phone_number": user.phone_number,
                   "role": user.role
               }
           }, status=status.HTTP_201_CREATED)


       return Response({
           "success": False,
           "errors": serializer.errors
       }, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user

# ==================== API THÔNG TIN KHÁCH HÀNG HIỆN TẠI ====================




@api_view(['GET'])
def current_customer_info(request):
  if not request.user.is_authenticated or request.user.role != 'CUSTOMER':
      return Response({'error': 'Không có quyền truy cập'}, status=403)




  try:
      customer = Customer.objects.select_related('user').get(user=request.user)
  except Customer.DoesNotExist:
      return Response({'error': 'Không tìm thấy thông tin khách hàng'}, status=404)




  return Response({
      'customer_code': customer.customer_code,
      'username': customer.user.username,
      'full_name': customer.user.full_name,
      'email': customer.user.email,
      'phone_number': customer.user.phone_number,
      'gender': getattr(customer.user, 'gender', None),
      'birthday': getattr(customer.user, 'birthday', None),
      'address': getattr(customer.user, 'address', None),
  })


@api_view(['POST'])
def change_password(request):
  if not request.user.is_authenticated:
      return Response({'error': 'Chưa đăng nhập'}, status=401)
  current_password = request.data.get('current_password')
  new_password = request.data.get('new_password')
  confirm_password = request.data.get('confirm_password')

  if not current_password or not new_password or not confirm_password:
      return Response({'error': 'Vui lòng nhập đầy đủ thông tin.'}, status=400)

  if not request.user.check_password(current_password):
      return Response({'error': 'Mật khẩu hiện tại không đúng.'}, status=400)

  if new_password != confirm_password:
      return Response({'error': 'Xác nhận mật khẩu không khớp.'}, status=400)

  if len(new_password) < 6:
      return Response({'error': 'Mật khẩu mới phải có ít nhất 6 ký tự.'}, status=400)

  request.user.set_password(new_password)
  request.user.save()
  update_session_auth_hash(request, request.user)

  return Response({'message': 'Đổi mật khẩu thành công.'})


# ====================== API DÀNH RIÊNG CHO KHÁCH HÀNG ĐẶT LỊCH ======================
class BookingCreateAPIView(generics.CreateAPIView):
    serializer_class = BookingCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        service = serializer.validated_data['service']
        booking_date = serializer.validated_data['booking_date']
        start_time = serializer.validated_data['start_time']

        # Tính toán end_time dựa trên duration ở bảng Service
        start_dt = datetime.combine(booking_date, start_time)
        end_dt = start_dt + timedelta(minutes=service.duration)

        user = self.request.user
        customer_profile = user.customer_profile

        # Tạo bản ghi mới vào bảng Booking với trạng thái PENDING
        return serializer.save(
            customer=customer_profile,
            end_time=end_dt.time(),
            total_price=service.price,
            status='PENDING'
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

def quan_ly_kh_view(request):
   # Lấy danh sách khách hàng và thông tin User liên kết
   customers_qs = Customer.objects.select_related('user').all()


   customers_list = []
   for cust in customers_qs:
       # Lấy tất cả đánh giá của khách hàng này thông qua các Booking của họ
       reviews_qs = Review.objects.filter(booking__customer=cust).select_related('booking__service')


       user_reviews = []
       for rev in reviews_qs:
           user_reviews.append({
               'service': rev.booking.service.name,
               'date': rev.created_at.strftime("%d/%m/%Y"),
               'rating': rev.rating,
               'comment': rev.comment or "Không có bình luận."
           })


       customers_list.append({
           'id': cust.customer_code,
           'name': cust.user.full_name or cust.user.username,
           'phone': cust.user.phone_number or "",
           'email': cust.user.email or "",
           'user': cust.user.username,
           'reviews': user_reviews  # Gửi kèm danh sách đánh giá vào biến JS
       })


   import json
   from django.core.serializers.json import DjangoJSONEncoder
   customers_json = json.dumps(customers_list, cls=DjangoJSONEncoder)

   return render(request, 'QuanLy/QuanLyKhachHang.html', {'customers_json': customers_json})

def quan_ly_dat_lich_view(request):
   # Lấy toàn bộ lịch đặt kèm theo thông tin Khách, Thợ, và Dịch vụ
   bookings_qs = Booking.objects.select_related('customer__user', 'employee__user', 'service').all()


   # 1. Đếm số lượng cho các ô thống kê
   stats = {
       'pending': bookings_qs.filter(status='PENDING').count(),
       'confirmed': bookings_qs.filter(status='CONFIRMED').count(),
       'completed': bookings_qs.filter(status='COMPLETED').count(),
       'canceled': bookings_qs.filter(status='CANCELED').count(),
   }

   # 2. Map trạng thái sang Tiếng Việt cho khớp với Giao diện
   status_map = {
       'PENDING': 'Chờ xác nhận',
       'CONFIRMED': 'Đã xác nhận',
       'COMPLETED': 'Hoàn thành',
       'CANCELED': 'Đã hủy'
   }

   bookings_list = []
   for b in bookings_qs:
       # Nối ngày và giờ thành chuẩn ISO để Javascript dễ đọc (VD: "2026-02-03T14:30")
       dt_string = f"{b.booking_date.strftime('%Y-%m-%d')}T{b.start_time.strftime('%H:%M')}"


       bookings_list.append({
           'id': b.id,  # Dùng ID của Booking
           'name': b.customer.user.full_name or b.customer.user.username,
           'phone': b.customer.user.phone_number or "",
           'time': dt_string,
           'service': b.service.name if b.service else "",
           'staff': b.employee.user.full_name or b.employee.user.username,
           'status': status_map.get(b.status, 'Chờ xác nhận'),
           'price': float(b.total_price) if b.total_price else 0
       })


   import json
   from django.core.serializers.json import DjangoJSONEncoder
   bookings_json = json.dumps(bookings_list, cls=DjangoJSONEncoder)

   return render(request, 'QuanLy/QuanLyDatLich.html', {
       'bookings_json': bookings_json,
       'stats': stats  # Gửi thêm biến đếm sang HTML
   })

def save_booking_api(request):
   if request.method == 'POST':
       booking_id = request.POST.get('id')
       edit_date = request.POST.get('date')
       edit_time = request.POST.get('time')
       status_vn = request.POST.get('status')


       # Ánh xạ từ Tiếng Việt (giao diện) về code Database
       status_map_reverse = {
           'Chờ xác nhận': 'PENDING',
           'Đã xác nhận': 'CONFIRMED',
           'Hoàn thành': 'COMPLETED',
           'Đã hủy': 'CANCELED'
       }


       try:
           booking = Booking.objects.get(id=booking_id)


           # Cập nhật thông tin
           if edit_date:
               booking.booking_date = edit_date
           if edit_time:
               booking.start_time = edit_time
           if status_vn and status_vn in status_map_reverse:
               booking.status = status_map_reverse[status_vn]


           booking.save()
           return JsonResponse({'status': 'success'})


       except Exception as e:
           return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


   return JsonResponse({'status': 'error'}, status=400)

def delete_booking_api(request):
    def delete_booking_api(request):
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                booking_id = data.get('id')

                booking = Booking.objects.get(id=booking_id)

                # KIỂM TRA TRẠNG THÁI TRƯỚC KHI XÓA
                if booking.status != 'CANCELED':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Chỉ có thể xóa các lịch hẹn đã ở trạng thái "Đã hủy".'
                    }, status=403)

                booking.delete()
                return JsonResponse({'status': 'success'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error'}, status=400)

def quan_ly_tai_khoan_view(request):
   # Lấy thông tin người dùng ĐANG ĐĂNG NHẬP
   user = request.user


   # Nếu chưa đăng nhập thì chuyển hướng hoặc báo lỗi (Tạm thời lấy 1 user test nếu dev)
   if not user.is_authenticated:
       # Tạm lấy user đầu tiên để bạn dễ test giao diện nếu chưa code trang Login
       from .models import User
       user = User.objects.filter(role='MANAGER').first() or User.objects.first()


   # Lấy thông tin nhân viên (để lấy mã NV và giới tính)
   employee = getattr(user, 'employee_profile', None)


   context = {
       'full_name': user.full_name or user.username,
       'email': user.email or "",
       'phone': user.phone_number or "",
       'username': user.username,
       'gender': employee.gender if employee else "F",
   }


   return render(request, 'QuanLy/QuanLyTaiKhoan.html', context)




# 2. API Cập nhật thông tin cơ bản
def update_profile_api(request):
   if request.method == 'POST':
       user = request.user
       if not user.is_authenticated:
           from .models import User
           user = User.objects.filter(role='MANAGER').first() or User.objects.first()


       name = request.POST.get('name')
       email = request.POST.get('email')
       phone = request.POST.get('phone')
       gender = request.POST.get('gender')


       try:
           # Cập nhật bảng User
           user.full_name = name
           user.email = email
           user.phone_number = phone
           user.save()


           # Cập nhật bảng Employee
           if hasattr(user, 'employee_profile'):
               user.employee_profile.gender = gender
               user.employee_profile.save()


           return JsonResponse({'status': 'success'})
       except Exception as e:
           return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


   return JsonResponse({'status': 'error'}, status=400)




# 3. API Đổi mật khẩu
def change_password_api(request):
   if request.method == 'POST':
       user = request.user
       if not user.is_authenticated:
           from .models import User
           user = User.objects.filter(role='MANAGER').first() or User.objects.first()


       current_pass = request.POST.get('current_password')
       new_pass = request.POST.get('new_password')


       # Kiểm tra mật khẩu cũ có đúng không
       if not user.check_password(current_pass):
           return JsonResponse({'status': 'error', 'message': 'Mật khẩu hiện tại không chính xác!'})


       # Đổi mật khẩu mới
       user.set_password(new_pass)
       user.save()


       # Hàm này giúp user KHÔNG bị văng ra (đăng xuất) sau khi đổi pass thành công
       update_session_auth_hash(request, user)


       return JsonResponse({'status': 'success'})


   return JsonResponse({'status': 'error'}, status=400)

# 1. Hàm hiển thị giao diện
def quan_ly_km_view(request):
   promotions = Promotion.objects.select_related('service').all()


   # Cập nhật trạng thái tự động mỗi khi tải trang (phòng trường hợp qua ngày mới)
   today = date.today()
   for p in promotions:
       old_status = p.status
       if p.end_date < today:
           p.status = 'EXPIRED'
       elif p.start_date > today:
           p.status = 'UPCOMING'
       else:
           p.status = 'ACTIVE'


       if old_status != p.status:
           p.save(update_fields=['status'])


   promo_list = []
   for p in promotions:
       # Map dữ liệu DB ra dạng mà HTML Javascript của bạn đang hiểu
       type_mapped = 'percent' if p.promo_type == 'PERCENT' else 'money'


       promo_list.append({
           'id': p.id,
           'name': p.name,
           'service': p.service.name if p.service else "",
           'type': type_mapped,
           'value': float(p.value),
           'start': p.start_date.strftime("%Y-%m-%d"),
           'end': p.end_date.strftime("%Y-%m-%d"),
           'condition': p.conditions or "",
           'status': p.status.lower()  # active, upcoming, expired
       })


   services = list(Service.objects.values('id', 'name'))


   from django.core.serializers.json import DjangoJSONEncoder
   context = {
       'promos_json': json.dumps(promo_list, cls=DjangoJSONEncoder),
       'services_json': json.dumps(services, cls=DjangoJSONEncoder)
   }
   return render(request, 'QuanLy/QuanLyKhuyenMai.html', context)




# 2. API Lưu (Thêm mới / Cập nhật)
def save_promo_api(request):
   if request.method == 'POST':
       try:
           promo_id = request.POST.get('id')
           name = request.POST.get('name')
           service_name = request.POST.get('service')


           # Map ngược lại từ giao diện (percent/money) vào Database (PERCENT/AMOUNT)
           js_type = request.POST.get('type')
           db_promo_type = 'PERCENT' if js_type == 'percent' else 'AMOUNT'


           value = request.POST.get('value')
           start_date = request.POST.get('start')
           end_date = request.POST.get('end')
           condition = request.POST.get('condition')
           status = request.POST.get('status').upper()  # ACTIVE, UPCOMING, EXPIRED


           service_obj = Service.objects.filter(name=service_name).first()


           if promo_id and promo_id != 'null':
               promo = Promotion.objects.get(id=promo_id)
               promo.name = name
               promo.service = service_obj
               promo.promo_type = db_promo_type
               promo.value = value
               promo.start_date = start_date
               promo.end_date = end_date
               promo.conditions = condition
               promo.status = status
               promo.save()
           else:
               Promotion.objects.create(
                   name=name,
                   service=service_obj,
                   promo_type=db_promo_type,
                   value=value,
                   start_date=start_date,
                   end_date=end_date,
                   conditions=condition,
                   status=status
               )
           return JsonResponse({'status': 'success'})
       except Exception as e:
           return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
   return JsonResponse({'status': 'error'}, status=400)




# 3. API Xóa
def delete_promo_api(request):
   if request.method == 'POST':
       try:
           data = json.loads(request.body)
           promo_id = data.get('id')
           Promotion.objects.filter(id=promo_id).delete()
           return JsonResponse({'status': 'success'})
       except Exception as e:
           return JsonResponse({'status': 'error', 'message': str(e)}, status=400)



def quan_ly_bao_cao_view(request):
   today = timezone.now().date()
   current_month = today.month
   current_year = today.year


   # 1. THỐNG KÊ CÁC Ô CARD (Tính dựa trên trạng thái ĐÃ XÁC NHẬN)
   # Lấy các lịch hẹn ĐÃ XÁC NHẬN trong tháng hiện tại
   confirmed_bookings = Booking.objects.filter(
       booking_date__month=current_month,
       booking_date__year=current_year,
       status='CONFIRMED'  # Đã đổi logic ở đây
   )


   # Tính tổng doanh thu tháng từ các lịch Đã xác nhận
   monthly_revenue = confirmed_bookings.aggregate(Sum('total_price'))['total_price__sum'] or 0
   formatted_revenue = f"{int(monthly_revenue):,}".replace(',', '.') + "đ"


   # Tổng số lịch hẹn trong tháng (Trừ những lịch Đã hủy)
   monthly_bookings_count = Booking.objects.filter(
       booking_date__month=current_month,
       booking_date__year=current_year
   ).exclude(status='CANCELED').count()


   # Dịch vụ phổ biến nhất (Tính theo số lượng lịch Đã xác nhận)
   popular_service_query = confirmed_bookings.values('service__name').annotate(
       booking_count=Count('id')
   ).order_by('-booking_count').first()


   popular_service = popular_service_query['service__name'] if popular_service_query else "Chưa có dữ liệu"


   # 2. DỮ LIỆU CHO BIỂU ĐỒ VÀ BẢNG
   # Gom nhóm doanh thu theo từng dịch vụ từ các lịch Đã xác nhận
   services_revenue = Booking.objects.filter(status='CONFIRMED').values('service__name').annotate(
       total_revenue=Sum('total_price'),
       booking_count=Count('id')
   ).order_by('-total_revenue')


   chart_labels = []
   chart_data = []
   table_data = []


   for item in services_revenue:
       chart_labels.append(item['service__name'])
       chart_data.append(float(item['total_revenue'] or 0))


       table_data.append({
           'service_name': item['service__name'],
           'booking_count': item['booking_count'],
           'revenue': float(item['total_revenue'] or 0)
       })


   context = {
       'formatted_revenue': formatted_revenue,
       'monthly_bookings_count': monthly_bookings_count,
       'popular_service': popular_service,
       'chart_labels': json.dumps(chart_labels, cls=DjangoJSONEncoder),
       'chart_data': json.dumps(chart_data, cls=DjangoJSONEncoder),
       'table_data_json': json.dumps(table_data, cls=DjangoJSONEncoder),
   }
   return render(request, 'QuanLy/QuanLyBaoCao.html', context)

# ==================== TRANG CHỦ NHÂN VIÊN ====================
@login_required(login_url='/dang-nhap/')  # Bắt buộc phải đăng nhập mới được vào
def TrangChu_NV(request):
   # Lấy full_name từ DB, nếu không có thì lấy username
   ten_nhan_vien = getattr(request.user, 'full_name', request.user.username)


   context = {
       'ten_nhan_vien': ten_nhan_vien,
   }
   return render(request, 'NhanVien/TrangChu/TrangChu_NV.html', context)




# ==================== QUẢN LÝ CA LÀM CÁ NHÂN ====================
@login_required(login_url='/DangNhap_QLNV/')
def QuanLyCaLam_NV(request):
   try:
       # Truy vấn trực tiếp: Tìm Employee nào có cột user khớp với người đang đăng nhập
       employee = Employee.objects.filter(user=request.user).first()


       if employee:
           # Nếu tìm thấy nhân viên, lấy toàn bộ ca làm của nhân viên đó
           danh_sach_ca = Booking.objects.filter(employee=employee).order_by('-booking_date', '-start_time')
       else:
           danh_sach_ca = []
   except Exception as e:
       danh_sach_ca = []


   context = {
       'danh_sach_ca': danh_sach_ca
   }
   return render(request, 'NhanVien/QuanLyCaLamCaNhan/QuanLyCaLam_NV.html', context)


# ==================== API CẬP NHẬT TRẠNG THÁI CA LÀM ====================
@login_required(login_url='/DangNhap_QLNV/')
def API_CapNhatTrangThaiCaLam(request):
   if request.method == 'POST':
       try:
           # Nhận dữ liệu JSON từ giao diện gửi lên
           data = json.loads(request.body)
           booking_id = data.get('booking_id')
           new_status = data.get('status')


           if not booking_id or not new_status:
               return JsonResponse({'success': False, 'message': 'Thiếu thông tin!'})


           # Tìm ca làm trong Database và cập nhật
           booking = Booking.objects.get(id=booking_id)
           booking.status = new_status
           booking.save()


           return JsonResponse({'success': True, 'message': 'Đã cập nhật trạng thái!'})


       except Booking.DoesNotExist:
           return JsonResponse({'success': False, 'message': 'Không tìm thấy ca làm này trong hệ thống!'})
       except Exception as e:
           return JsonResponse({'success': False, 'message': f'Lỗi hệ thống: {str(e)}'})


   return JsonResponse({'success': False, 'message': 'Phương thức không hợp lệ!'})

# ==================== QUẢN LÝ TÀI KHOẢN CÁ NHÂN ====================
@login_required(login_url='/DangNhap_QLNV/')
def QuanLyTaiKhoan_NV(request):
       try:
           # Truy vấn trực tiếp: Tìm thông tin Employee khớp với tài khoản User
           employee = Employee.objects.filter(user=request.user).first()
       except Exception as e:
           employee = None

       context = {
           'employee': employee
       }
       return render(request, 'NhanVien/QuanLyTaiKhoanCaNhan/QuanLyTaiKhoan_NV.html', context)


   # ==================== API CẬP NHẬT THÔNG TIN CÁ NHÂN ====================
@login_required(login_url='/DangNhap_QLNV/')
def API_CapNhatThongTin(request):
       if request.method == 'POST':
           try:
               # Nếu dùng fetch API với Content-Type application/json
               if request.content_type == 'application/json':
                   data = json.loads(request.body)
               else:  # Nếu form submit thông thường
                   data = request.POST

               full_name = data.get('full_name')
               gender = data.get('gender')
               email = data.get('email')
               phone = data.get('phone')

               user = request.user

               # Cập nhật thông tin trong bảng User
               if full_name:
                   user.full_name = full_name
               if email:
                   user.email = email
               if phone:
                   user.phone_number = phone
               user.save()

               # Cập nhật giới tính trong bảng Employee
               try:
                   employee = Employee.objects.get(user=user)
                   if gender:
                       employee.gender = gender
                   employee.save()
               except Employee.DoesNotExist:
                   pass  # Bỏ qua nếu user không phải là nhân viên

               return JsonResponse({'success': True, 'message': 'Cập nhật thông tin thành công!'})


           except Exception as e:
               return JsonResponse({'success': False, 'message': f'Lỗi hệ thống: {str(e)}'})

       return JsonResponse({'success': False, 'message': 'Phương thức không hợp lệ!'})

   # ==================== API ĐỔI MẬT KHẨU ====================
@login_required(login_url='/DangNhap_QLNV/')
def API_DoiMatKhau(request):
       if request.method == 'POST':
           try:
               if request.content_type == 'application/json':
                   data = json.loads(request.body)
               else:
                   data = request.POST

               old_password = data.get('old_password')
               new_password = data.get('new_password')

               user = request.user

               # Kiểm tra mật khẩu cũ có đúng không
               if not user.check_password(old_password):
                   return JsonResponse({'success': False, 'message': 'Mật khẩu hiện tại không đúng!'})

               # Đổi mật khẩu mới
               user.set_password(new_password)
               user.save()

               # Giữ trạng thái đăng nhập sau khi đổi mật khẩu
               update_session_auth_hash(request, user)

               return JsonResponse({'success': True, 'message': 'Đổi mật khẩu thành công!'})


           except Exception as e:
               return JsonResponse({'success': False, 'message': f'Lỗi hệ thống: {str(e)}'})

       return JsonResponse({'success': False, 'message': 'Phương thức không hợp lệ!'})

   # ==================== ĐĂNG XUẤT ====================
def DangXuat(request):
       logout(request)
       return redirect('nv:DangNhap_QLNV')