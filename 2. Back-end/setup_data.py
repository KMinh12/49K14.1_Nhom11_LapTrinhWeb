import os
import django
import random
from datetime import datetime, date, time, timedelta
from django.utils import timezone
# BƯỚC 1: Cấu hình môi trường (PHẢI LÀM ĐẦU TIÊN)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NAILS.settings')
django.setup()

# BƯỚC 2: Sau khi setup xong mới được import Model
from nails_backend.models import User, Service, Employee, Customer, Booking, Promotion, Review, Notification

# ==========================================
# 1. IMPORT SERVICE
# ==========================================
def run():
    services_data = [
        # NAILS
        ("Cắt da", 30, 30000),
        ("Cắt da + sơn gel", 80, 80000),
        ("Fen đầu móng", 30, 30000),
        ("Tráng gương full", 50, 50000),
        ("Mắt mèo", 30, 30000),
        ("Úp móng", 80, 80000),
        ("Nối móng đắp gel", 150, 150000),
        ("Nối móng đắp bột", 200, 200000),
        ("Trang trí", 15, 15000), # Lấy trung bình 5-30
        ("Đính charm, đá", 15, 15000), # Lấy trung bình 5-30

        # NỐI MI
        ("Nối mi tự nhiên", 150, 150000),
        ("Nối mi thiết kế, dày", 180, 180000),
        ("Uốn mi", 120, 120000),
        ("Tháo mi", 30, 30000),

        # GỘI ĐẦU
        ("Gội dầu cơ bản", 30, 30000),
        ("Gội thảo dược", 40, 40000),
        ("Gội dầu cặp", 40, 40000),
        ("Rửa mặt", 15, 5000),
        ("Mát xa mặt", 20, 20000),
        ("Nước nóng", 10, 5000),
        ("Tẩy da chết mặt", 15, 10000),

        # DỊCH VỤ KHÁC
        ("Cạo mặt", 20, 20000),
        ("Chà gót tẩy da chết chân", 60, 60000),
    ]

    print("--- Bắt đầu nhập danh sách dịch vụ ---")
    for name, duration, price in services_data:
        obj, created = Service.objects.get_or_create(
            name=name,
            defaults={'duration': duration, 'price': price}
        )
        if created:
            print(f"✅ Đã thêm: {name}")
        else:
            print(f"ℹ️ Đã tồn tại: {name}")

    print("--- Hoàn thành ---")

if __name__ == "__main__":
    run()
# ==========================================
# 2. ADD_CUSTOMER
# ==========================================
def create_customers():
    # Danh sách dữ liệu khách hàng mới
    new_customers = [
        {"username": "khach02", "name": "Hoàng Thu Hà", "code": "KH002", "phone": "0912345678"},
        {"username": "khach03", "name": "Phạm Diệu Linh", "code": "KH003", "phone": "0987654321"},
    ]

    print("--- Đang tạo thêm khách hàng ---")

    for data in new_customers:
        # 1. Tạo User với Role là CUSTOMER
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'full_name': data['name'],
                'role': 'CUSTOMER',
                'phone_number': data['phone']
            }
        )

        if created:
            user.set_password("123456")  # Mật khẩu mặc định
            user.save()

            # 2. Tạo Customer profile liên kết với User
            Customer.objects.create(
                user=user,
                customer_code=data['code']
            )
            print(f"✅ Đã tạo khách hàng: {data['name']} ({data['code']})")
        else:
            print(f"ℹ️ Username '{data['username']}' đã tồn tại, bỏ qua.")

    print("--- Hoàn thành ---")

if __name__ == "__main__":
    create_customers()

# ==========================================
# 3. ADD_MORE_CUSTOMER
# ==========================================
def add_3_more_customers():
    # Danh sách 3 khách hàng tiếp theo
    more_customers = [
        {"username": "khach_quynh", "name": "Lê Như Quỳnh", "code": "KH004", "phone": "0334556677"},
        {"username": "khach_minh", "name": "Nguyễn Quang Minh", "code": "KH005", "phone": "0355667788"},
        {"username": "khach_thanh", "name": "Vũ Tuyết Thanh", "code": "KH006", "phone": "0399112233"},
    ]

    print("--- Đang tạo thêm 3 khách hàng mới ---")

    for data in more_customers:
        # 1. Tạo User
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'full_name': data['name'],
                'role': 'CUSTOMER',
                'phone_number': data['phone']
            }
        )

        if created:
            user.set_password("123456")  # Mật khẩu mặc định
            user.save()

            # 2. Tạo Customer profile
            Customer.objects.create(
                user=user,
                customer_code=data['code']
            )
            print(f"✅ Đã tạo khách hàng: {data['name']} ({data['code']})")
        else:
            print(f"ℹ️ Username '{data['username']}' đã tồn tại, bỏ qua.")

    print("--- Hoàn thành ---")

if __name__ == "__main__":
    add_3_more_customers()

# ==========================================
# 4. ADD STAFF
# ==========================================
def create_more_employees():
    # Danh sách dữ liệu nhân viên mới
    new_staff = [
        {"username": "staff_lan", "name": "Nguyễn Ngọc Lan", "code": "NV002", "gender": "F", "salary": 8000000},
        {"username": "staff_mai", "name": "Lê Thị Tuyết Mai", "code": "NV003", "gender": "F", "salary": 7500000},
        {"username": "staff_tu", "name": "Trần Anh Tú", "code": "NV004", "gender": "M", "salary": 9000000},
        {"username": "staff_vy", "name": "Đặng Thúy Vy", "code": "NV005", "gender": "F", "salary": 8200000},
    ]

    print("--- Đang tạo thêm nhân viên ---")

    for data in new_staff:
        # 1. Tạo User
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'full_name': data['name'],
                'role': 'STAFF',
                'is_staff': True  # Cho phép vào admin nếu cần
            }
        )

        if created:
            user.set_password("123456")  # Mật khẩu mặc định
            user.save()

            # 2. Tạo Employee profile
            Employee.objects.create(
                user=user,
                employee_code=data['code'],
                gender=data['gender'],
                salary=data['salary']
            )
            print(f"✅ Đã tạo nhân viên: {data['name']} ({data['code']})")
        else:
            print(f"ℹ️ Username '{data['username']}' đã tồn tại, bỏ qua.")

    print("--- Hoàn thành ---")


if __name__ == "__main__":
    create_more_employees()

# ==========================================
# 5. BẢNG BOOKING
# ==========================================

def create_9_bookings():
    # Lấy toàn bộ dữ liệu hiện có
    customers = list(Customer.objects.all())
    employees = list(Employee.objects.all())
    services = list(Service.objects.all())

    if not customers or not employees or not services:
        print("❌ Lỗi: Bạn cần có ít nhất 1 Khách hàng, 1 Nhân viên và 1 Dịch vụ trong DB!")
        return

    statuses = ['PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELED']

    print("--- Đang tạo 9 lịch đặt (Booking) ---")

    for i in range(9):
        # Chọn ngẫu nhiên các đối tượng
        customer = random.choice(customers)
        employee = random.choice(employees)
        service = random.choice(services)

        # Tạo ngày đặt (trong khoảng 7 ngày trước đến 7 ngày sau)
        booking_date = date.today() + timedelta(days=random.randint(-7, 7))

        # Tạo giờ bắt đầu ngẫu nhiên từ 8h đến 20h
        start_hour = random.randint(8, 20)
        start_time = time(start_hour, 0)

        # Tính giờ kết thúc (dựa trên duration của dịch vụ)
        # Vì model end_time là TimeField, ta tính toán qua datetime
        dummy_dt = datetime.combine(date.today(), start_time) + timedelta(minutes=service.duration)
        end_time = dummy_dt.time()

        # Chọn trạng thái ngẫu nhiên
        status = random.choice(statuses)

        # Tạo Booking
        Booking.objects.create(
            customer=customer,
            employee=employee,
            service=service,
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            total_price=service.price,
            status=status
        )
        print(f"✅ Booking {i + 1}: Khách {customer.user.full_name} - Dịch vụ {service.name} ({status})")

    print("--- Hoàn thành tạo 9 lịch đặt ---")


if __name__ == "__main__":
    create_9_bookings()

# ==========================================
# 6. ADD_PROMOTIONS
# ==========================================
def create_promotions():
    # Lấy danh sách dịch vụ hiện có để gán khuyến mãi
    all_services = list(Service.objects.all())
    if not all_services:
        print("❌ Lỗi: Bạn cần nhập danh sách dịch vụ trước khi tạo khuyến mãi!")
        return

    # Danh sách 7 khuyến mãi mẫu
    promo_list = [
        # 3 Cái đã ngưng hoạt động (Ngày kết thúc là quá khứ)
        {"name": "Khai trương hồng phát", "type": "PERCENT", "value": 20, "days_ago_start": 60, "days_ago_end": 30,
         "status": "EXPIRED"},
        {"name": "Chào mừng 8/3", "type": "AMOUNT", "value": 20000, "days_ago_start": 40, "days_ago_end": 35,
         "status": "EXPIRED"},
        {"name": "Giờ vàng giá sốc tháng 3", "type": "PERCENT", "value": 50, "days_ago_start": 30, "days_ago_end": 20,
         "status": "EXPIRED"},

        # 4 Cái còn hiệu lực (Ngày kết thúc là tương lai)
        {"name": "Ưu đãi tháng 4", "type": "PERCENT", "value": 10, "days_ago_start": 5, "days_ahead_end": 20,
         "status": "ACTIVE"},
        {"name": "Combo Gội đầu thư giãn", "type": "AMOUNT", "value": 15000, "days_ago_start": 2, "days_ahead_end": 15,
         "status": "ACTIVE"},
        {"name": "Tri ân khách hàng thân thiết", "type": "PERCENT", "value": 15, "days_ago_start": 1,
         "days_ahead_end": 30, "status": "ACTIVE"},
        {"name": "Cuối tuần rực rỡ", "type": "PERCENT", "value": 5, "days_ago_start": 0, "days_ahead_end": 3,
         "status": "ACTIVE"},
    ]

    print("--- Đang tạo danh sách khuyến mãi ---")

    today = date.today()

    for p in promo_list:
        # Chọn ngẫu nhiên một dịch vụ để áp dụng
        service = random.choice(all_services)

        # Tính toán ngày
        if "days_ago_end" in p:
            start_date = today - timedelta(days=p["days_ago_start"])
            end_date = today - timedelta(days=p["days_ago_end"])
        else:
            start_date = today - timedelta(days=p["days_ago_start"])
            end_date = today + timedelta(days=p["days_ahead_end"])

        obj, created = Promotion.objects.get_or_create(
            name=p["name"],
            defaults={
                'service': service,
                'promo_type': p["type"],
                'value': p["value"],
                'start_date': start_date,
                'end_date': end_date,
                'status': p["status"],
                'conditions': f"Áp dụng cho dịch vụ {service.name}"
            }
        )

        if created:
            print(f"✅ Đã tạo: {p['name']} (Trạng thái: {p['status']})")
        else:
            print(f"ℹ️ Khuyến mãi '{p['name']}' đã tồn tại.")

    print("--- Hoàn thành ---")


if __name__ == "__main__":
    create_promotions()

# ==========================================
# 7. ADD REVIEWS
# ==========================================
def create_6_reviews():
    # Lấy danh sách tất cả các booking hiện có
    all_bookings = list(Booking.objects.all())

    if len(all_bookings) < 6:
        print(f"❌ Cảnh báo: Bạn chỉ có {len(all_bookings)} booking. Script sẽ tạo review cho tất cả.")
        bookings_to_review = all_bookings
    else:
        # Lấy ngẫu nhiên 6 booking từ danh sách
        bookings_to_review = random.sample(all_bookings, 6)

    # Danh sách các lời bình luận mẫu
    comments = [
        "Dịch vụ rất tuyệt vời, nhân viên làm rất kỹ!",
        "Móng làm xong rất bền và đẹp, mình sẽ quay lại.",
        "Nhân viên nhiệt tình nhưng đợi hơi lâu một chút.",
        "Giá cả hợp lý, không gian tiệm rất sạch sẽ.",
        "Màu sơn gel rất chuẩn, mình rất ưng ý.",
        "Gội đầu thảo dược rất thư giãn, tay nghề thợ rất tốt.",
        "Làm mi rất tự nhiên, không bị cộm mắt.",
        "Rất hài lòng với thái độ phục vụ của tiệm."
    ]

    print("--- Đang tạo 6 đánh giá (Review) ---")

    count = 0
    for booking in bookings_to_review:
        # Kiểm tra xem booking này đã có review chưa (tránh lỗi OneToOne)
        if hasattr(booking, 'review'):
            print(f"ℹ️ Booking ID {booking.id} đã có đánh giá, bỏ qua.")
            continue

        rating = random.randint(4, 5)  # Đa số là 4-5 sao cho "đẹp" dữ liệu
        comment = random.choice(comments)

        Review.objects.create(
            booking=booking,
            rating=rating,
            comment=comment
        )
        count += 1
        print(f"✅ Đã tạo Review cho Booking ID {booking.id}: {rating} sao.")

    print(f"--- Hoàn thành tạo {count} đánh giá ---")


if __name__ == "__main__":
    create_6_reviews()

# ==========================================
# 8. NOTIFICATION
# ==========================================
def create_notifications_for_bookings():
    # Lấy toàn bộ Booking hiện có (bao gồm cả 1 cái từ seed.py và 9 cái từ add_bookings.py)
    bookings = Booking.objects.all()

    if not bookings.exists():
        print("❌ Lỗi: Không tìm thấy Booking nào để tạo thông báo!")
        return

    print(f"--- Đang tạo thông báo cho {bookings.count()} Booking hiện có ---")

    count = 0
    for booking in bookings:
        # Kiểm tra tránh tạo trùng thông báo cho cùng một Booking
        if Notification.objects.filter(booking=booking).exists():
            continue

        # Lấy thông tin hiển thị
        customer_name = booking.customer.user.full_name or booking.customer.user.username
        service_name = booking.service.name
        booking_status = booking.status

        title = f"Thông báo dịch vụ: {service_name}"

        # Logic nội dung dựa trên trạng thái Booking thực tế
        if booking_status == 'PENDING':
            content = f"Chào {customer_name}, lịch hẹn {service_name} của bạn đang chờ xác nhận từ tiệm."
            status = 'PENDING'
            sent_at = None
        elif booking_status == 'CONFIRMED':
            content = f"Xác nhận: Lịch hẹn {service_name} của {customer_name} vào lúc {booking.start_time} ngày {booking.booking_date} đã sẵn sàng."
            status = 'SENT'
            sent_at = timezone.now()
        elif booking_status == 'COMPLETED':
            content = f"Cảm ơn {customer_name} đã ghé tiệm! Đừng quên để lại đánh giá cho dịch vụ {service_name} nhé."
            status = 'SENT'
            sent_at = timezone.now()
        elif booking_status == 'CANCELED':
            content = f"Thông báo: Lịch hẹn {service_name} ngày {booking.booking_date} đã bị hủy."
            status = 'SENT'
            sent_at = timezone.now()
        else:
            content = f"Cập nhật lịch hẹn cho dịch vụ {service_name}."
            status = 'PENDING'
            sent_at = None

        # Tạo bản ghi Notification
        Notification.objects.create(
            booking=booking,
            noti_type=random.choice(['SYSTEM', 'EMAIL']),
            status=status,
            title=title,
            content=content,
            scheduled_time=timezone.now(),
            sent_at=sent_at
        )
        count += 1
        print(f"✅ Đã tạo Noti cho Booking ID {booking.id} - Trạng thái: {booking_status}")

    print(f"--- Hoàn thành: Đã thêm {count} thông báo mới ---")


if __name__ == "__main__":
    create_notifications_for_bookings()

# ==========================================
# 9. SEED
# ==========================================
def seed_data():
    print("Đang khởi tạo dữ liệu mẫu...")

    # 1. Tạo Dịch vụ
    s1, _ = Service.objects.get_or_create(name="Sơn Gel", duration=45, price=200000)
    s2, _ = Service.objects.get_or_create(name="Cắt da tay", duration=20, price=50000)
    s3, _ = Service.objects.get_or_create(name="Nối mi", duration=60, price=350000)
    print("- Đã tạo xong danh sách dịch vụ.")

    # 5. Tạo User Manager (Quản lý)
    u_man, created = User.objects.get_or_create(username="quanly", role="MANAGER")
    if created:
        u_man.set_password("quanly123")
        u_man.full_name = "Nguyen Minh Khue"
        u_man.is_staff = True  # Cho phép đăng nhập vào trang Admin
        u_man.is_superuser = True  # Cấp quyền tối cao
        u_man.save()
    print("- Đã tạo xong tài khoản Quản lý (Admin).")

    # 2. Tạo User & Employee (Nhân viên)
    u_emp, created = User.objects.get_or_create(username="nhanvien01", role="STAFF")
    if created:
        u_emp.set_password("123456")
        u_emp.full_name = "Nguyễn Thị Tuyết"
        u_emp.save()
        Employee.objects.create(user=u_emp, employee_code="NV001", gender="F", salary=7000000)
    print("- Đã tạo xong nhân viên.")

    # 3. Tạo User & Customer (Khách hàng)
    u_cus, created = User.objects.get_or_create(username="khachhang01", role="CUSTOMER")
    if created:
        u_cus.set_password("123456")
        u_cus.full_name = "Trần Thị Lan"
        u_cus.save()
        Customer.objects.create(user=u_cus, customer_code="KH001")
    print("- Đã tạo xong khách hàng.")

    # 4. Tạo Lịch đặt (Booking) mẫu
    emp = Employee.objects.get(employee_code="NV001")
    cus = Customer.objects.get(customer_code="KH001")

    Booking.objects.create(
        customer=cus,
        employee=emp,
        service=s1,
        booking_date=date.today(),
        start_time=time(9, 0),
        end_time=time(10, 0),
        total_price=s1.price,
        status="CONFIRMED"
    )
    print("- Đã tạo xong 1 lịch đặt mẫu.")
    print("--- HOÀN THÀNH ---")

if __name__ == '__main__':
    seed_data()