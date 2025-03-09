import telebot
import sqlite3

# توکن رو اینجا بذارید
bot = telebot.TeleBot("bot367060:8f4318cd-fa00-4a2c-8d08-b15c2410beb8")

# دیتابیس ساده
conn = sqlite3.connect("requests.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS requests 
                  (id INTEGER PRIMARY KEY, user_id TEXT, category TEXT, text TEXT, status TEXT)''')
conn.commit()

# منوی شروع
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("کارگزینی", "آموزش", "رفاهی", "پیگیری درخواست")
    bot.reply_to(message, "به ربات سازمان خوش آمدید! گزینه مورد نظر را انتخاب کنید:", reply_markup=markup)

# ثبت درخواست
@bot.message_handler(func=lambda message: message.text in ["کارگزینی", "آموزش", "رفاهی"])
def handle_category(message):
    category = message.text
    msg = bot.reply_to(message, "لطفاً متن درخواست خود را وارد کنید:")
    bot.register_next_step_handler(msg, lambda m: save_request(m, category))

def save_request(message, category):
    user_id = message.chat.id
    text = message.text
    cursor.execute("INSERT INTO requests (user_id, category, text, status) VALUES (?, ?, ?, ?)", 
                   (user_id, category, text, "در انتظار"))
    conn.commit()
    request_id = cursor.lastrowid
    code = f"TVTO-{category[:2]}-{request_id:03d}"
    bot.reply_to(message, f"درخواست شما ثبت شد!\nکد رهگیری: {code}\nبرای پیگیری از این کد استفاده کنید.")

# پیگیری
@bot.message_handler(func=lambda message: message.text == "پیگیری درخواست")
def track_request(message):
    msg = bot.reply_to(message, "لطفاً کد رهگیری خود را وارد کنید:")
    bot.register_next_step_handler(msg, show_status)

def show_status(message):
    code = message.text
    bot.reply_to(message, f"وضعیت درخواست {code}: در انتظار (نسخه آزمایشی)")

bot.polling()