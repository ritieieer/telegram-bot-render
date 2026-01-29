import os
import telebot
import logging
import threading
import time
from datetime import datetime
from flask import Flask, request, jsonify
from threading import Thread

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get environment variables
TOKEN = os.getenv('TOKEN', '8504170878:AAEFeQ5bzYkDBRgycgLms61dfFEZy2VN9QA')
OWNER_ID = int(os.getenv('OWNER_ID', 8406101760))
ADMIN_ID = int(os.getenv('ADMIN_ID', 8406101760))
PORT = int(os.getenv('PORT', 10000))

# Initialize Flask app
app = Flask(__name__)

# Initialize Telegram bot
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

# Bot start time
BOT_START_TIME = datetime.now()

# Store bot webhook info
WEBHOOK_URL = None

# ========== FLASK ROUTES ==========
@app.route('/')
def home():
    """Home page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Telegram Bot</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .container { max-width: 800px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 20px; backdrop-filter: blur(10px); }
            h1 { font-size: 3em; margin-bottom: 20px; }
            .status { background: rgba(0,255,0,0.2); padding: 15px; border-radius: 10px; margin: 20px 0; }
            .buttons { display: flex; justify-content: center; gap: 20px; margin: 30px 0; flex-wrap: wrap; }
            .btn { background: white; color: #764ba2; padding: 15px 30px; text-decoration: none; border-radius: 50px; font-weight: bold; transition: 0.3s; }
            .btn:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
            .uptime { font-size: 1.5em; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Telegram Bot</h1>
            <div class="status">✅ <strong>Bot is Running</strong></div>
            <div class="uptime">⏱ Uptime: <span id="uptime">Loading...</span></div>
            <div class="buttons">
                <a href="https://t.me/ritikxyzhost" class="btn" target="_blank">📞 Contact Owner</a>
                <a href="https://t.me/ritikxyzhost" class="btn" target="_blank">📢 Updates Channel</a>
                <a href="/health" class="btn">🩺 Health Check</a>
                <a href="/stats" class="btn">📊 Statistics</a>
            </div>
            <p>Bot hosted on <strong>Render.com</strong> | Owner ID: <code>{}</code></p>
        </div>
        <script>
            function updateUptime() {
                fetch('/uptime').then(r => r.json()).then(data => {
                    document.getElementById('uptime').textContent = data.uptime;
                });
            }
            updateUptime();
            setInterval(updateUptime, 1000);
        </script>
    </body>
    </html>
    """.format(OWNER_ID)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "bot": "running" if bot.get_me() else "stopped",
        "timestamp": datetime.now().isoformat(),
        "platform": "Render.com"
    }), 200

@app.route('/uptime')
def uptime_api():
    """Get uptime"""
    uptime = datetime.now() - BOT_START_TIME
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
    return jsonify({"uptime": uptime_str})

@app.route('/stats')
def stats():
    """Bot statistics"""
    return jsonify({
        "start_time": BOT_START_TIME.isoformat(),
        "owner_id": OWNER_ID,
        "admin_id": ADMIN_ID,
        "webhook_set": WEBHOOK_URL is not None,
        "platform": "Render.com"
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Telegram webhook endpoint"""
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'ok', 200
    return 'error', 403

# ========== TELEGRAM BOT COMMANDS ==========
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Welcome message"""
    user = message.from_user
    welcome_text = f"""
<b>👋 Welcome {user.first_name}!</b>

🤖 <b>Bot Status:</b> <code>✅ ONLINE</code>
🏠 <b>Hosted on:</b> <code>Render.com</code>
👑 <b>Owner:</b> @ritikxyzhost

<b>📋 Available Commands:</b>
/start - Show this message
/status - Check bot status
/uptime - Show bot uptime
/ping - Test bot response
/mpx [query] - AI Chat (Claude 3.5)
/id - Get your user ID
/speed - Bot speed test

<b>📁 File Features:</b>
• Upload .py files (view only)
• Basic file management
• AI Chat integration

<b>⚠️ Note:</b> Full script execution requires VPS.
    """
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['status'])
def bot_status(message):
    """Bot status"""
    status_text = f"""
<b>📊 BOT STATUS</b>

✅ <b>Status:</b> Online
🌐 <b>Host:</b> Render.com
🔄 <b>Mode:</b> Webhook
⏱ <b>Uptime:</b> {get_uptime()}
👤 <b>Users:</b> 1 (you)
🔧 <b>Script Execution:</b> Disabled

<b>For full features:</b>
• Use DigitalOcean/VPS
• Full script execution
• File storage
• Process management
    """
    bot.reply_to(message, status_text)

@bot.message_handler(commands=['uptime'])
def uptime_command(message):
    """Show uptime"""
    uptime_str = get_uptime()
    bot.reply_to(message, f"⏱ <b>Bot Uptime:</b> <code>{uptime_str}</code>")

@bot.message_handler(commands=['ping'])
def ping_command(message):
    """Ping command"""
    start = time.time()
    msg = bot.reply_to(message, "🏓 <i>Pinging...</i>")
    end = time.time()
    latency = round((end - start) * 1000, 2)
    bot.edit_message_text(f"🏓 <b>Pong!</b>\n⏱ <b>Latency:</b> <code>{latency}ms</code>",
                         message.chat.id, msg.message_id)

@bot.message_handler(commands=['id'])
def get_id(message):
    """Get user ID"""
    user = message.from_user
    bot.reply_to(message, 
                f"👤 <b>Your Info:</b>\n"
                f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
                f"📛 <b>Name:</b> {user.first_name}\n"
                f"📱 <b>Username:</b> @{user.username or 'N/A'}")

@bot.message_handler(commands=['speed'])
def speed_test(message):
    """Speed test"""
    import random
    start = time.time()
    numbers = [random.randint(1, 1000) for _ in range(10000)]
    sorted_numbers = sorted(numbers)
    end = time.time()
    
    speed_time = round((end - start) * 1000, 2)
    bot.reply_to(message, 
                f"⚡ <b>Speed Test Results:</b>\n"
                f"⏱ <b>Processing Time:</b> <code>{speed_time}ms</code>\n"
                f"📊 <b>Sorted 10,000 numbers</b>\n"
                f"📡 <b>Server:</b> Render.com")

@bot.message_handler(commands=['mpx'])
def ai_chat(message):
    """AI Chat using Claude"""
    if len(message.text.split()) < 2:
        bot.reply_to(message, "Usage: <code>/mpx your question</code>")
        return
    
    query = message.text.split(' ', 1)[1]
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # Simple mock response for testing
        responses = [
            f"🤖 <b>AI Response:</b>\n\n{query} - This is a simulated response. On production, Claude 3.5 will respond.",
            f"🧠 <b>Thinking about:</b>\n\n{query}\n\nThis is test mode. Real AI requires API key.",
            f"💭 <b>Query received:</b>\n\n{query}\n\n✅ AI service would respond here."
        ]
        import random
        response = random.choice(responses)
        bot.reply_to(message, response)
    except Exception as e:
        logger.error(f"AI error: {e}")
        bot.reply_to(message, "⚠️ AI service temporarily unavailable.")

@bot.message_handler(content_types=['document'])
def handle_file(message):
    """Handle file upload"""
    doc = message.document
    if doc.file_name:
        if doc.file_name.endswith('.py'):
            bot.reply_to(message, 
                        f"📄 <b>Python File Received:</b> <code>{doc.file_name}</code>\n"
                        f"📦 <b>Size:</b> {doc.file_size} bytes\n\n"
                        f"⚠️ <i>Note: File saved for viewing only. Script execution disabled on Render.com.</i>\n\n"
                        f"<b>For full execution:</b>\n"
                        f"• Use VPS (DigitalOcean)\n"
                        f"• Full Python/JS execution\n"
                        f"• Process management")
        else:
            bot.reply_to(message, 
                        f"📁 <b>File:</b> <code>{doc.file_name}</code>\n"
                        f"⚠️ <i>Only .py files accepted for viewing.</i>")
    else:
        bot.reply_to(message, "⚠️ Invalid file.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Echo messages"""
    if message.text.lower() in ['hi', 'hello', 'hey']:
        bot.reply_to(message, f"👋 Hello {message.from_user.first_name}!")
    elif message.text.lower() in ['status', 'check']:
        bot_status(message)
    elif message.text.lower() == 'uptime':
        uptime_command(message)
    else:
        bot.reply_to(message, 
                    "Type /start to begin\n"
                    "/help for commands\n"
                    "/mpx [question] for AI chat")

# ========== HELPER FUNCTIONS ==========
def get_uptime():
    """Calculate uptime"""
    uptime = datetime.now() - BOT_START_TIME
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

def setup_webhook():
    """Setup Telegram webhook"""
    global WEBHOOK_URL
    
    # Get Render URL
    render_url = os.getenv('RENDER_EXTERNAL_URL')
    if not render_url:
        # For local testing
        WEBHOOK_URL = None
        logger.info("Running in polling mode (local)")
        return False
    
    WEBHOOK_URL = f"{render_url}/webhook"
    
    try:
        # Remove existing webhook
        bot.remove_webhook()
        time.sleep(1)
        
        # Set new webhook
        bot.set_webhook(url=WEBHOOK_URL)
        logger.info(f"Webhook set: {WEBHOOK_URL}")
        return True
    except Exception as e:
        logger.error(f"Webhook setup failed: {e}")
        return False

def start_polling():
    """Start bot polling (fallback)"""
    logger.info("Starting bot polling...")
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            logger.error(f"Polling error: {e}")
            time.sleep(5)

# ========== MAIN ==========
if __name__ == '__main__':
    logger.info("="*60)
    logger.info("🚀 TELEGRAM BOT STARTING")
    logger.info(f"👑 Owner ID: {OWNER_ID}")
    logger.info(f"🌐 Port: {PORT}")
    logger.info(f"🤖 Bot: @{bot.get_me().username if bot.get_me() else 'Unknown'}")
    logger.info("="*60)
    
    # Try to setup webhook
    webhook_set = setup_webhook()
    
    if webhook_set:
        logger.info("✅ Running in WEBHOOK mode")
        # Flask will handle requests via /webhook
        app.run(host='0.0.0.0', port=PORT, debug=False)
    else:
        logger.info("🔄 Running in POLLING mode")
        # Start polling in background thread
        polling_thread = threading.Thread(target=start_polling)
        polling_thread.daemon = True
        polling_thread.start()
        
        # Start Flask in main thread
        app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)