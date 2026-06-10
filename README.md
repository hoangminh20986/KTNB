# 💎 Anomaly Transaction Detection Web App (Apple Liquid Glass UI)

Ứng dụng Web phát hiện giao dịch bất thường (Anomaly Detection) thời gian thực sử dụng thuật toán học máy **Isolation Forest**, được xây dựng bằng **Streamlit** và trực quan hóa tương tác bằng **Plotly**. 

Giao diện ứng dụng được thiết kế theo phong cách thiết kế **Liquid Glass** của Apple với tông màu tối thời thượng (Deep Dark Mode), hiệu ứng kính mờ (glassmorphism), phản chiếu ánh sáng gradient mịn màng và các nút điều khiển bo góc phát sáng.

---

## 🌟 Tính năng chính (Key Features)

* **Phân tích dữ liệu tự động**: Tự động tải tệp dữ liệu giao dịch mẫu `transactions_Q1_demo.csv` có sẵn hoặc cho phép kéo thả tệp CSV tùy chỉnh từ người dùng.
* **Cấu hình mô hình thời gian thực**: Thay đổi tham số `contamination` (tỉ lệ bất thường giả định) và số lượng cây quyết định `n_estimators` trực quan ngay trên Sidebar.
* **Thẻ thống kê Glassmorphism**: Hiển thị tổng quan các chỉ số giao dịch (Tổng số, Bình thường, Cảnh báo, Khẩn cấp) dưới dạng thẻ mờ sương cao cấp.
* **Trực quan hóa 3D tương tác**: Biểu đồ phân tán 3D không gian đặc trưng (Số tiền, Giờ, Nhân viên) giúp nhìn rõ ranh giới phân tách các điểm bất thường.
* **Bộ lọc và Xuất dữ liệu**: Tìm kiếm, lọc giao dịch bất thường và tải về dưới dạng tệp **Excel (.xlsx)** hoặc **CSV**.
* **Trình kiểm tra Ad-hoc nhanh**: Nhập nhanh các chỉ số của một giao dịch đơn lẻ để nhận kết quả phân tích rủi ro và đo bằng thước đo (Gauge Chart) trực quan.

---

## 🛠️ Cài đặt và Chạy cục bộ (Local Installation & Setup)

Để chạy ứng dụng trên máy tính của bạn, hãy thực hiện theo các bước sau:

### 1. Chuẩn bị môi trường Python
Yêu cầu phiên bản Python từ **3.8** đến **3.11**. Nên tạo một môi trường ảo (virtual environment) để tránh xung đột thư viện:

```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo (Windows)
.\venv\Scripts\activate

# Kích hoạt môi trường ảo (macOS/Linux)
source venv/bin/activate
```

### 2. Cài đặt các thư viện phụ thuộc
Cài đặt toàn bộ các thư viện được khai báo trong `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Khởi chạy ứng dụng Web
Chạy lệnh khởi động Streamlit từ thư mục chứa tệp `app.py`:

```bash
streamlit run app.py
```
Ứng dụng sẽ tự động được mở trên trình duyệt web mặc định của bạn tại địa chỉ: `http://localhost:8501`.

---

## 🚀 Hướng dẫn đẩy lên GitHub và Deploy Streamlit Cloud

Streamlit cung cấp nền tảng hosting miễn phí, rất dễ sử dụng để chia sẻ ứng dụng của bạn với mọi người.

### Bước 1: Đẩy mã nguồn lên GitHub
1. Tạo một repository mới trên GitHub (ví dụ tên: `transaction-anomaly-app`).
2. Khởi tạo Git tại thư mục dự án cục bộ và đẩy lên GitHub:

```bash
git init
git add app.py requirements.txt transactions_Q1_demo.csv README.md
git commit -m "Initial commit for Streamlit app"
git branch -M main
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/transaction-anomaly-app.git
git push -u origin main
```

### Bước 2: Deploy lên Streamlit Community Cloud
1. Truy cập trang web [share.streamlit.io](https://share.streamlit.io/) và đăng nhập bằng tài khoản GitHub của bạn.
2. Click vào nút **"New app"** ở góc trên cùng bên phải.
3. Cấu hình các thông số deploy như sau:
   - **Repository**: Chọn repository bạn vừa tạo (`<YOUR_GITHUB_USERNAME>/transaction-anomaly-app`).
   - **Branch**: Chọn `main`.
   - **Main file path**: Điền `app.py`.
4. Click nút **"Deploy!"** và đợi hệ thống thiết lập môi trường trong khoảng 1-2 phút. 
5. Ứng dụng của bạn sẽ hoạt động trực tuyến với đường dẫn chia sẻ công khai!

---

## 📊 Kiến trúc kỹ thuật của Mô hình

Mô hình học máy trong ứng dụng sử dụng thuật toán **Isolation Forest** (Rừng cô lập) từ thư viện `scikit-learn`.
* **Đặc trưng huấn luyện**: `amount` (Số tiền), `hour` (Giờ thực hiện giao dịch), `is_employee_int` (Nhân viên/Khách hàng).
* **Tiền xử lý**: Các đặc trưng số được đưa về phân phối chuẩn thông qua `StandardScaler` giúp cải thiện hiệu quả phân tách ranh giới của cây quyết định.
* **Phân loại cấp độ**:
  - Giao dịch có nhãn dự đoán `is_anomaly == True` sẽ được xếp vào dạng bất thường.
  - Phân loại **Khẩn cấp (Emergency)** được xác định cho các giao dịch có điểm bất thường thuộc 25% nhóm thấp nhất (rủi ro cao nhất).
  - Phân loại **Cảnh báo (Warning)** được xác định cho các giao dịch bất thường còn lại.
