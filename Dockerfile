# Sử dụng image Python chính thức
FROM python:3.9-slim

# Tạo thư mục làm việc
WORKDIR /app

# Tạo người dùng mới không phải root
RUN useradd -m myuser

# Chuyển quyền sở hữu thư mục /app cho người dùng mới
RUN chown -R myuser:myuser /app

# Chạy dưới quyền người dùng không phải root
USER myuser

# Sao chép các file vào container
COPY . .

# Cài đặt thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Khởi chạy ứng dụng
CMD ["python", "getnew.py"]
