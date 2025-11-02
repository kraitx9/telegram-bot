

الملفات الكاملة للبوت:

1. الملف الرئيسي: data_bot.py

```python
import telebot
import sqlite3
import logging
import requests
import json
import time
import threading
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# إعدادات البوت
BOT_TOKEN = "8221481764:AAHExTEBG2uzlAm67RJMASO6yBRDkw6aXZU"
ADMIN_ID = "6710677130"

bot = telebot.TeleBot(BOT_TOKEN)
logging.basicConfig(level=logging.INFO)

# قاعدة البيانات
def init_db():
    conn = sqlite3.connect('data_bot.db', check_same_thread=False)
    c = conn.cursor()
    
    # المستخدمين
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                  username TEXT,
                  full_name TEXT,
                  points INTEGER DEFAULT 10,
                  searches_count INTEGER DEFAULT 0,
                  successful_searches INTEGER DEFAULT 0,
                  subscription_type TEXT DEFAULT 'free',
                  subscription_expiry TEXT,
                  registration_date TEXT)''')
    
    # عمليات البحث
    c.execute('''CREATE TABLE IF NOT EXISTS searches
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  query TEXT,
                  result TEXT,
                  search_type TEXT,
                  timestamp TEXT,
                  success BOOLEAN)''')
    
    # الباقات والاشتراكات
    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  plan_type TEXT,
                  price REAL,
                  start_date TEXT,
                  end_date TEXT,
                  status TEXT)''')
    
    # النقاط والهدايا
    c.execute('''CREATE TABLE IF NOT EXISTS points_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  points_change INTEGER,
                  reason TEXT,
                  date TEXT)''')
    
    conn.commit()
    conn.close()

init_db()

# وظائف مساعدة
def get_user_data(user_id):
    conn = sqlite3.connect('data_bot.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def update_points(user_id, points_change, reason=""):
    conn = sqlite3.connect('data_bot.db')
    c = conn.cursor()
    c.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (points_change, user_id))
    c.execute("INSERT INTO points_history (user_id, points_change, reason, date) VALUES (?, ?, ?, ?)",
              (user_id, points_change, reason, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def add_search_record(user_id, query, result, search_type, success):
    conn = sqlite3.connect('data_bot.db')
    c = conn.cursor()
    c.execute("INSERT INTO searches (user_id, query, result, search_type, timestamp, success) VALUES (?, ?, ?, ?, ?, ?)",
              (user_id, query, result, search_type, datetime.now().isoformat(), success))
    c.execute("UPDATE users SET searches_count = searches_count + 1 WHERE user_id = ?", (user_id,))
    if success:
        c.execute("UPDATE users SET successful_searches = successful_searches + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# محركات البحث
def search_telegram_data(query):
    """محاكاة بحث في بيانات تليجرام"""
    time.sleep(2)  # محاكاة وقت البحث
    
    # بيانات وهمية للنتائج
    results = [
        f"📱 حساب تليجرام: @{query}",
        f"🆔 ID: {random.randint(10000, 99999)}",
        f"👤 الاسم: {query}",
        f"📅 تاريخ الإنشاء: 2023-{random.randint(1,12)}-{random.randint(1,28)}",
        f"🌐 اللغة: العربية",
        f"✅ الحساب: نشط"
    ]
    return "\n".join(results)

def search_social_media(query):
    """بحث في وسائل التواصل الاجتماعي"""
    time.sleep(3)
    
    platforms = ["تويتر", "فيسبوك", "انستجرام", "لينكدإن"]
    found_on = random.sample(platforms, random.randint(1, 3))
    
    results = [f"🔍 وجد على: {', '.join(found_on)}"]
    for platform in found_on:
        results.append(f"📊 {platform}: @{query} (متابعين: {random.randint(100, 50000)})")
    
    return "\n".join(results)

def search_public_records(query):
    """بحث في السجلات العامة"""
    time.sleep(2)
    
    results = [
        "📋 السجلات العامة:",
        f"🔎 بحث عن: {query}",
        "📍 المنطقة: الشرق الأوسط",
        "🌍 النشاط: متصل الآن",
        f"📈 النشاط الشهري: {random.randint(50, 500)} عملية"
    ]
    return "\n".join(results)

# أوامر البوت
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}"
    
    # تسجيل المستخدم
    conn = sqlite3.connect('data_bot.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, full_name, registration_date) VALUES (?, ?, ?, ?)",
              (user_id, username, full_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    user_data = get_user_data(user_id)
    
    welcome_text = f"""
🎯 **أهلاً وسهلاً {full_name}!**

📊 **إحصائياتك:**
• النقاط الحالية: {user_data[3]} نقطة
• عدد عمليات البحث: {user_data[4]}
• عمليات البحث الناجحة: {user_data[5]}

💎 **الباقة الحالية:** {user_data[6].title()}

🔍 **جاهز للبحث؟ استخدم الأزرار أدناه**
    """
    
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🔎 بحث تليجرام", callback_data="search_telegram"),
        InlineKeyboardButton("📱 وسائل تواصل", callback_data="search_social")
    )
    markup.row(
        InlineKeyboardButton("📋 سجلات عامة", callback_data="search_public"),
        InlineKeyboardButton("💎 الاشتراكات", callback_data="subscriptions")
    )
    markup.row(
        InlineKeyboardButton("🆓 نقاط مجانية", callback_data="free_points"),
        InlineKeyboardButton("📊 إحصائياتي", callback_data="my_stats")
    )
    
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    user_data = get_user_data(user_id)
    
    if call.data == "search_telegram":
        if user_data[3] < 5:
            bot.answer_callback_query(call.id, "❌ نقاط غير كافية! تحتاج 5 نقاط للبحث", show_alert=True)
            return
        
        msg = bot.send_message(call.message.chat.id, "🔍 أدخل اسم المستخدم أو رقم الهاتف للبحث في تليجرام:")
        bot.register_next_step_handler(msg, process_telegram_search)
    
    elif call.data == "search_social":
        if user_data[3] < 8:
            bot.answer_callback_query(call.id, "❌ نقاط غير كافية! تحتاج 8 نقاط للبحث", show_alert=True)
            return
        
        msg = bot.send_message(call.message.chat.id, "🌐 أدخل الاسم للبحث في وسائل التواصل الاجتماعي:")
        bot.register_next_step_handler(msg, process_social_search)
    
    elif call.data == "search_public":
        if user_data[3] < 10:
            bot.answer_callback_query(call.id, "❌ نقاط غير كافية! تحتاج 10 نقاط للبحث", show_alert=True)
            return
        
        msg = bot.send_message(call.message.chat.id, "📋 أدخل الاسم للبحث في السجلات العامة:")
        bot.register_next_step_handler(msg, process_public_search)
    
    elif call.data == "subscriptions":
        show_subscriptions(call.message)
    
    elif call.data == "free_points":
        show_free_points(call.message)
    
    elif call.data == "my_stats":
        show_user_stats(call.message)

def process_telegram_search(message):
    user_id = message.from_user.id
    query = message.text
    
    # خصم النقاط
    update_points(user_id, -5, "بحث تليجرام")
    
    # البحث
    bot.send_chat_action(message.chat.id, 'typing')
    result = search_telegram_data(query)
    
    # حفظ السجل
    add_search_record(user_id, query, result, "telegram", True)
    
    # إرسال النتيجة
    result_text = f"""
✅ **نتيجة البحث في تليجرام**

🔍 **البحث عن:** `{query}`

{result}

💎 **النقاط المتبقية:** {get_user_data(user_id)[3]}
    """
    
    bot.send_message(message.chat.id, result_text, parse_mode='Markdown')
    send_welcome(message)  # إعادة عرض القائمة

def process_social_search(message):
    user_id = message.from_user.id
    query = message.text
    
    update_points(user_id, -8, "بحث وسائل تواصل")
    bot.send_chat_action(message.chat.id, 'typing')
    result = search_social_media(query)
    
    add_search_record(user_id, query, result, "social_media", True)
    
    result_text = f"""
✅ **نتيجة البحث في وسائل التواصل**

🔍 **البحث عن:** `{query}`

{result}

💎 **النقاط المتبقية:** {get_user_data(user_id)[3]}
    """
    
    bot.send_message(message.chat.id, result_text, parse_mode='Markdown')
    send_welcome(message)

def process_public_search(message):
    user_id = message.from_user.id
    query = message.text
    
    update_points(user_id, -10, "بحث سجلات عامة")
    bot.send_chat_action(message.chat.id, 'typing')
    result = search_public_records(query)
    
    add_search_record(user_id, query, result, "public_records", True)
    
    result_text = f"""
✅ **نتيجة البحث في السجلات العامة**

🔍 **البحث عن:** `{query}`

{result}

💎 **النقاط المتبقية:** {get_user_data(user_id)[3]}
    """
    
    bot.send_message(message.chat.id, result_text, parse_mode='Markdown')
    send_welcome(message)

def show_subscriptions(message):
    subscription_text = """
💎 **باقات الاشتراك**

🟢 **الباقة المجانية:**
• 10 نقاط مجانية
• بحث محدود
• نتائج أساسية

🟡 **الباقة الفضية - 25 نقطة شهرياً:**
• بحث غير محدود في تليجرام
• 30 نقطة تليجرام شهرياً
• نتائج متقدمة

🔴 **الباقة الماسية - 50 نقطة شهرياً:**
• جميع مميزات الباقة الفضية
• بحث غير محدود في قاعدة البيانات
• نتائج شاملة
• دعم فني متميز

💳 **للاشتراك:** راسل الإدارة @Haeaaam44bot
    """
    
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🟢 مجاني", callback_data="free_plan"),
        InlineKeyboardButton("🟡 فضي - 25$", callback_data="silver_plan")
    )
    markup.row(
        InlineKeyboardButton("🔴 ماسي - 50$", callback_data="gold_plan"),
        InlineKeyboardButton("📞 اتصل بالإدارة", url="https://t.me/Haeaaam44bot")
    )
    
    bot.send_message(message.chat.id, subscription_text, parse_mode='Markdown', reply_markup=markup)

def show_free_points(message):
    user_id = message.from_user.id
    
    points_text = """
🆓 **اكسب نقاط مجانية**

📊 **الطرق المتاحة:**
• دعوة الأصدقاء: 5 نقاط لكل صديق
• المشاركة اليومية: 2 نقطة يومياً
• تفعيل الإشعارات: 3 نقاط
• تقييم البوت: 5 نقاط

📈 **رصيدك الحالي:** {} نقطة
    """.format(get_user_data(user_id)[3])
    
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("📤 دعوة أصدقاء", callback_data="invite_friends"),
        InlineKeyboardButton("🎁 مكافأة يومية", callback_data="daily_bonus")
    )
    markup.row(
        InlineKeyboardButton("🔔 تفعيل إشعارات", callback_data="enable_notifications"),
        InlineKeyboardButton("⭐ تقييم البوت", callback_data="rate_bot")
    )
    
    bot.send_message(message.chat.id, points_text, parse_mode='Markdown', reply_markup=markup)

def show_user_stats(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    
    stats_text = f"""
📊 **إحصائياتك الشخصية**

👤 **المستخدم:** {user_data[2]}
🆔 **الاسم المستخدم:** @{user_data[1] or 'غير متوفر'}

💎 **النقاط:** {user_data[3]}
🔍 **إجمالي عمليات البحث:** {user_data[4]}
✅ **عمليات البحث الناجحة:** {user_data[5]}

📅 **تاريخ التسجيل:** {user_data[8][:10]}
🎯 **الباقة الحالية:** {user_data[6].title()}

📈 **مستواك:** {'مبتدئ' if user_data[4] < 10 else 'متوسط' if user_data[4] < 50 else 'محترف'}
    """
    
    bot.send_message(message.chat.id, stats_text, parse_mode='Markdown')

# تشغيل البوت
if __name__ == "__main__":
    print("🚀 بدء تشغيل بوت سحب البيانات...")
    bot.infinity_polling()
```

2. ملف الإعدادات: config.py

```python
# إعدادات البوت
BOT_CONFIG = {
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "admin_id": "YOUR_ADMIN_ID_HERE",
    "database_url": "data_bot.db",
    
    # أسعار البحث
    "search_costs": {
        "telegram": 5,
        "social_media": 8,
        "public_records": 10
    },
    
    # الباقات
    "subscription_plans": {
        "free": {
            "points": 10,
            "daily_searches": 3,
            "features": ["بحث أساسي"]
        },
        "silver": {
            "points": 25,
            "daily_searches": 10,
            "features": ["بحث تليجرام غير محدود", "30 نقطة شهرية"]
        },
        "gold": {
            "points": 50,
            "daily_searches": "unlimited",
            "features": ["بحث غير محدود", "جميع المميزات", "دعم فني"]
        }
    }
}
```

3. ملف المتطلبات: requirements.txt

```txt
pyTelegramBotAPI==4.15.2
requests==2.31.0
```

🚀 طريقة التشغيل:

1. تثبيت المتطلبات:

```bash
pip install -r requirements.txt
```

1. تعديل الإعدادات:

· ضع توكن البوت في BOT_TOKEN
· ضع آيدي الأدمن في ADMIN_ID

1. تشغيل البوت:

```bash
python data_bot.py
```



ا
