from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
from cachetools import TTLCache

# Sử dụng biến môi trường để bảo mật TOKEN
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8004946642:AAE-Cfgd2VBVMBB8CDiJpcbQxvTuX_kYcWU")

# Lưu danh sách coin trong bộ nhớ cache
coin_cache = None
price_cache = TTLCache(maxsize=100, ttl=60)  # Cache giá trong 60 giây

# Lấy danh sách các coin từ CoinGecko
def get_coin_list():
    global coin_cache
    if coin_cache is None:
        url = "https://api.coingecko.com/api/v3/coins/list"
        response = requests.get(url)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
        coin_cache = response.json()
    return coin_cache

# Chuyển đổi ticker sang ID
def convert_ticker_to_id(ticker):
    """
    Chuyển đổi ký hiệu coin (symbol) thành ID trên CoinGecko.
    """
    coin_list = get_coin_list()
    ticker = ticker.lower()
    for coin in coin_list:
        if coin["symbol"] == ticker:  # Tìm theo symbol
            print(f"Ticker '{ticker}' được chuyển thành ID '{coin['id']}'")  # Debug
            return coin["id"]
    print(f"Không tìm thấy ID cho ticker '{ticker}'")  # Debug
    return None

# Hàm định dạng giá
def format_price(price):
    """
    Định dạng giá trị float thành chuỗi dễ đọc.
    - Hiển thị 2 chữ số thập phân với giá trị lớn hơn 1.
    - Hiển thị tối đa 5 chữ số thập phân với giá trị nhỏ hơn 1.
    """
    if price >= 1:
        return f"{price:,.2f}"  # Giá trị lớn: 2 chữ số thập phân
    else:
        return f"{price:.5f}"  # Giá trị nhỏ: tối đa 5 chữ số thập phân

# Lấy giá từ CoinGecko API
def get_crypto_price(crypto: str):
    try:
        # Kiểm tra cache trước
        if crypto in price_cache:
            return format_price(price_cache[crypto])

        # Chuyển đổi ticker sang ID
        coin_id = convert_ticker_to_id(crypto)
        if not coin_id:
            return None

        # Gọi API lấy giá
        url = f'https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd'
        response = requests.get(url)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
        data = response.json()

        # Lấy giá trị USD từ API
        if coin_id in data and "usd" in data[coin_id]:
            price = data[coin_id]["usd"]
            price_cache[crypto] = price  # Lưu vào cache
            return format_price(price)
        else:
            print(f"Dữ liệu không hợp lệ cho ID '{coin_id}': {data}")  # Debug
            return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        return None
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

# Lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xin chào! Gõ tên đồng coin (vd: btc, eth) để xem giá.\n"
        "Sử dụng lệnh /help để biết thêm chi tiết."
    )

# Lệnh /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hướng dẫn:\n"
        "- Nhập tên ký hiệu đồng coin (ticker) để lấy giá (vd: btc, eth).\n"
        "- Lệnh /start để bắt đầu.\n"
        "- Lệnh /help để hiển thị hướng dẫn."
    )

# Xử lý tin nhắn của người dùng
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    crypto = update.message.text.strip().lower()
    price = get_crypto_price(crypto)
    if price:
        await update.message.reply_text(f"Giá {crypto.upper()} hiện tại: ${price}")
    else:
        await update.message.reply_text(
            "Không tìm thấy thông tin về đồng coin này!\n"
            "Vui lòng kiểm tra ký hiệu hoặc thử lại sau."
        )

# Chạy bot
def main():
    # Kiểm tra token
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN":
        print("Vui lòng đặt TOKEN bot trong biến môi trường TELEGRAM_BOT_TOKEN.")
        return

    # Khởi tạo bot
    application = Application.builder().token(TOKEN).build()

    # Thêm handler cho các lệnh và tin nhắn
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Bắt đầu bot
    application.run_polling()

if __name__ == "__main__":
    main()
