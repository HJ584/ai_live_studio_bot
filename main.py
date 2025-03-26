import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from config import BOT_TOKEN, BRAND_LOGO
from database import Database
from modules.application import ApplicationModule
from modules.registration import RegistrationModule
from modules.checkin import CheckinModule
from modules.admin import AdminModule
from utils import setup_logging, format_welcome_message

# 设置日志
logger = setup_logging()

# 初始化数据库
db = Database("ai_live_studio.db")

# 初始化机器人
application = ApplicationBuilder().token(BOT_TOKEN).build()

# 初始化功能模块
application_module = ApplicationModule(application, db)
registration_module = RegistrationModule(application, db)
checkin_module = CheckinModule(application, db)
admin_module = AdminModule(application, db)

# 处理回调查询
application.add_handler(CallbackQueryHandler(
    lambda update, context: application_module.process_callback(update, context) or
                            registration_module.process_callback(update, context) or
                            admin_module.process_callback(update, context)
))

# 欢迎消息
async def send_welcome(update: Update):
    user_name = update.effective_user.first_name
    welcome_msg = format_welcome_message(user_name)
    await update.message.reply_text(welcome_msg)

application.add_handler(CommandHandler('start', send_welcome))

# 启动机器人
if __name__ == "__main__":
    application.run_polling()
