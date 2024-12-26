# Sử dụng image Python chính thức
FROM python:3.9-slim

# Thiết lập biến môi trường
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TELEGRAM_BOT_TOKEN="8004946642:AAE-Cfgd2VBVMBB8CDiJpcbQxvTuX_kYcWU"

# Tạo thư mục làm việc
WORKDIR /app

# Cài đặt các gói cần thiết
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Tạo người dùng không phải root
RUN useradd -m myuser && chown -R myuser:myuser /app

# Chuyển sang người dùng không phải root
USER myuser

# Sao chép các file ứng dụng vào container
COPY --chown=myuser:myuser . .

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Câu lệnh khởi chạy ứng dụng
CMD ["python", "getnew.py"]
