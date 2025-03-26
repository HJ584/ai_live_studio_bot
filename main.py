import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
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
updater = Updater(BOT_TOKEN)
bot = updater.bot

# 初始化功能模块
application_module = ApplicationModule(bot, db)
registration_module = RegistrationModule(bot, db)
checkin_module = CheckinModule(bot, db)
admin_module = AdminModule(bot, db)

# 处理回调查询
updater.dispatcher.add_handler(CallbackQueryHandler(
    lambda update, context: application_module.process_callback(update, context) or
                            registration_module.process_callback(update, context) or
                            admin_module.process_callback(update, context)
))

# 欢迎消息
def send_welcome(update, context):
    user_name = update.effective_user.first_name
    welcome_msg = format_welcome_message(user_name)
    update.effective_message.reply_text(welcome_msg)

updater.dispatcher.add_handler(CommandHandler('start', send_welcome))

# 启动轮询
updater.start_polling()
updater.idle()
