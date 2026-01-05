# Hệ Thống Quản Lý Bảo Hiểm (Insurance Management System)

Chào mừng bạn đến với **Duan_Project1** - Hệ thống quản lý bảo hiểm toàn diện được xây dựng trên nền tảng Django. Hệ thống này cung cấp giải pháp trọn vẹn từ việc quản lý sản phẩm, vòng đời hợp đồng, xử lý bồi thường tích hợp AI, đến quản lý đội ngũ đại lý và báo cáo kinh doanh.

## 🚀 Chi Tiết Tính Năng

### 1. Quản Lý Sản Phẩm Bảo Hiểm (Insurance Products)

Module cho phép định nghĩa linh hoạt các gói sản phẩm:

- **Đa dạng gói cước**: Hỗ trợ 3 cấp độ gói: _Cơ bản (Basic)_, _Tiêu chuẩn (Standard)_, và _Cao cấp (Premium)_.
- **Tùy biến tiền tệ**: Hỗ trợ thanh toán bằng VND hoặc USD.
- **Tự động định dạng**: Hiển thị số tiền thông minh (ví dụ: 2M, 500K).
- **Cấu hình hoa hồng**: Thiết lập mức hoa hồng (%) riêng cho từng sản phẩm dành cho Cộng tác viên (Agent).

### 2. Quản Lý Hợp Đồng (Policy Management)

Quản lý toàn bộ vòng đời của một hợp đồng bảo hiểm:

- **Quy trình trạng thái**: Theo dõi từ _Chờ xử lý (Pending)_ -> _Đang hoạt động (Active)_ -> _Hết hạn (Expired)_ hoặc _Đã hủy (Cancelled)_.
- **Định danh điện tử (eKYC)**: Hệ thống lưu trữ và quản lý tài liệu định danh (CCCD mặt trước/sau, ảnh chân dung, giấy khám sức khỏe) cho từng người thụ hưởng.
- **Tính toán tự động**: Tự động tính toán ngày hết hạn (365 ngày) và tiến độ thực hiện hợp đồng.
- **Gia đình & Người thân**: Cho phép mua bảo hiểm cho người thân (Vợ/Chồng, Con, Cha/Me) trong cùng một hợp đồng.

### 3. Xử Lý Bồi Thường & AI (Claims & Risk Assessment)

Quy trình bồi thường được số hóa và hỗ trợ bởi trí tuệ nhân tạo:

- **Workflow phê duyệt**: Quy trình chặt chẽ: _Chờ xử lý_ -> _Đang xử lý_ -> _Yêu cầu bổ sung_ / _Đã duyệt_ / _Từ chối_.
- **Thông tin y tế chi tiết**: Ghi nhận loại điều trị (Nội trú/Ngoại trú/Phẫu thuật), thông tin bệnh viện, bác sĩ và chi phí điều trị.
- **Đánh giá rủi ro (AI Risk Assessment)**: Tích hợp mô hình AI để chấm điểm rủi ro cho từng yêu cầu, phân loại mức độ rủi ro (_Thấp, Trung bình, Cao_) giúp nhân viên đưa ra quyết định nhanh chóng.
- **OCR tài liệu**: Tự động trích xuất văn bản từ tài liệu bồi thường được tải lên.

### 4. Quản Lý Người Dùng & Đại Lý (Users & Agents)

Phân quyền chặt chẽ theo vai trò người dùng:

- **Khách hàng (Customer)**: Đăng ký, quản lý hồ sơ eKYC, theo dõi hợp đồng và lịch sử bồi thường.
- **Đại lý (Agent)**: Có mã đại lý riêng, theo dõi doanh số bán hàng và hoa hồng nhận được.
- **Nhân viên (Employee)**: Xử lý nghiệp vụ, duyệt hồ sơ.
- **Quản trị viên (Admin)**: Toàn quyền cấu hình hệ thống.

### 5. Bảng Điều Khiển & Báo Cáo (Dashboard)

Giao diện quản trị trực quan cung cấp cái nhìn tổng quan:

- **Thống kê thời gian thực**: Tổng doanh thu, số lượng khách hàng mới, tỷ lệ chốt đơn.
- **Biểu đồ động**: Biểu đồ doanh thu theo tháng, phân tích tỷ trọng các gói bảo hiểm bán ra.
- **Nhật ký hoạt động**: Theo dõi các sự kiện quan trọng (Khách mua mới, Duyệt bồi thường) ngay khi chúng xảy ra.

### 6. Thanh Toán & Thông Báo (Payments & Notifications)

- **Đa phương thức thanh toán**: Hệ thống hỗ trợ ghi nhận thanh toán qua Thẻ tín dụng, Chuyển khoản, hoặc Ví điện tử.
- **Thông báo tự động**: Gửi thông báo cho người dùng khi có sự kiện quan trọng (Hợp đồng sắp hết hạn, Cập nhật trạng thái bồi thường).

## 🛠️ Yêu Cầu Hệ Thống

- **Python**: 3.10+
- **PostgreSQL**: Database server
- **Thư viện**: Django 5.0+, Pillow, psycopg2-binary, google-generativeai (cho tính năng AI).

## 📦 Hướng Dẫn Cài Đặt

### 1. Clone Dự Án

```bash
git clone <đường-dẫn-repo-của-bạn>
cd Duan_Project1
```

### 2. Thiết Lập Môi Trường

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3. Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu Hình Database

Đảm bảo PostgreSQL đang chạy và đã tạo database `BaoHiem`. Cập nhật `insurance_app/settings.py` nếu cần.

### 5. Cấu Hình API Key (Quan trọng)

Để sử dụng tính năng đánh giá rủi ro bằng AI, bạn cần có API Key từ luồng Gemini/Google AI. Thêm vào `settings.py` hoặc biến môi trường:

```python
GEMINI_API_KEY="YOUR_API_KEY"
```

### 6. Khởi Chạy

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 📝 License

Dự án nội bộ.
