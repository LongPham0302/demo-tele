from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os

# Sử dụng biến môi trường để bảo mật TOKEN
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

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

# Hàm lấy giá từ Binance
def get_crypto_price_binance(ticker: str):
    """
    Lấy giá trị USD của đồng coin từ API Binance.
    """
    try:
        # Chuyển đổi ticker thành format của Binance
        symbol = f"{ticker.upper()}USDT"

        # Gọi API Binance
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
        data = response.json()

        # Kiểm tra dữ liệu trả về
        if "price" in data:
            price = float(data["price"])
            print(f"Giá của {ticker.upper()} là {price} USD")  # Debug
            return format_price(price)
        else:
            print(f"Dữ liệu không hợp lệ từ Binance: {data}")  # Debug
            return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        return None
    except Exception as e:
        print(f"Error fetching price from Binance: {e}")
        return None

# Lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xin chào! Gõ tên đồng coin (vd: BTC, ETH) để xem giá.\n"
        "Sử dụng lệnh /help để biết thêm chi tiết."
    )

# Lệnh /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hướng dẫn:\n"
        "- Nhập tên ký hiệu đồng coin (ticker) để lấy giá (vd: BTC, ETH).\n"
        "- Lệnh /start để bắt đầu.\n"
        "- Lệnh /help để hiển thị hướng dẫn."
    )

# Xử lý tin nhắn của người dùng
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    crypto = update.message.text.strip().upper()
    price = get_crypto_price_binance(crypto)
    if price:
        await update.message.reply_text(f"Giá {crypto} hiện tại: ${price}")
    else:
        await update.message.reply_text(
            "Không tìm thấy thông tin về đồng coin này!\n"
            "Vui lòng kiểm tra ký hiệu hoặc thử lại sau."
        )

# Chạy bot
def main():
    """
    Chạy bot Telegram.
    """
    if not TOKEN or TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
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
