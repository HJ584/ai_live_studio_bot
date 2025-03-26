import logging
from telebot import TeleBot
from config import BOT_TOKEN, BRAND_LOGO
from database import Database
from modules.application import ApplicationModule
from modules.registration import RegistrationModule
from modules.checkin import CheckinModule
from modules.admin import AdminModule
from utils import setup_logging

# 设置日志
logger = setup_logging()

# 初始化数据库
db = Database("ai_live_studio.db")

# 初始化机器人
bot = TeleBot(BOT_TOKEN)

# 初始化功能模块
application_module = ApplicationModule(bot, db)
registration_module = RegistrationModule(bot, db)
checkin_module = CheckinModule(bot, db)
admin_module = AdminModule(bot, db)

# 处理回调查询
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    application_module.process_callback(call)
    registration_module.process_callback(call)
    admin_module.process_callback(call)

# 欢迎消息
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_msg = format_welcome_message(user_name)
    bot.reply_to(message, welcome_msg)

# 主程序
if __name__ == "__main__":
    logger.info("爱即直播工作室机器人已启动！💕")
    bot.polling()
