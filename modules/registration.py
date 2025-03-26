from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, MessageHandler, Filters, CallbackQueryHandler
from database import Database
from config import ADMIN_ID
from utils import format_registration_message

class RegistrationModule:
    def __init__(self, application, db):
        self.application = application
        self.db = db
        self._setup_handlers()
    
    def _setup_handlers(self):
        self.application.add_handler(MessageHandler(Filters.text & Filters.reply, self.handle_registration))
    
    async def handle_registration(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        if not update.effective_message.reply_to_message or \
           not update.effective_message.reply_to_message.text == "请发送以下信息完成注册：\n1. 用户名（邮箱或手机号）\n2. ID（大写字母与数字）\n3. 昵称（汉字数字字母）":
            return
        
        content = update.effective_message.text.split('\n')
        
        if len(content) != 3:
            await self.application.bot.send_message(chat_id, "请按照格式发送三条信息。💕")
            return
        
        username, streamer_id, nickname = content
        
        # 保存到数据库
        self.db.add_registration(user_id, username, streamer_id, nickname)
        
        # 通知管理员
        admin_message = format_registration_message(user_id, username, streamer_id, nickname)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("通过", callback_data=f"approve_registration_{user_id}"),
             InlineKeyboardButton("拒绝", callback_data=f"reject_registration_{user_id}")]
        ])
        
        await self.application.bot.send_message(ADMIN_ID, admin_message, reply_markup=keyboard)
        
        await self.application.bot.send_message(chat_id, "您的注册信息已提交，我们将在24小时内审核。💕")
    
    async def process_callback(self, update: Update, context: CallbackContext):
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("approve_registration_"):
            user_id = int(query.data.split("_")[-1])
            self.db.update_registration_status(user_id, "approved")
            await self.application.bot.send_message(user_id, "恭喜！您的注册已通过审核。💕 您可以开始使用打卡功能了。")
            await self.application.bot.edit_message_text("注册已通过", query.message.chat.id, query.message.message_id)
        
        elif query.data.startswith("reject_registration_"):
            user_id = int(query.data.split("_")[-1])
            self.db.update_registration_status(user_id, "rejected")
            await self.application.bot.send_message(user_id, "很抱歉，您的注册未通过审核。💕 您可以重新申请。")
            await self.application.bot.edit_message_text("注册已拒绝", query.message.chat.id, query.message.message_id)
