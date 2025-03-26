from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from database import Database
from config import BRAND_LOGO, ADMIN_ID
from utils import format_application_message

class ApplicationModule:
    def __init__(self, application, db):
        self.application = application
        self.db = db
        self._setup_handlers()
    
    def _setup_handlers(self):
        self.application.add_handler(CommandHandler('apply', self.handle_apply))
        self.application.add_handler(MessageHandler(Filters.video & Filters.reply, self.handle_video))
        self.application.add_handler(MessageHandler(Filters.photo & Filters.reply, self.handle_photo))
    
    async def handle_apply(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # 检查是否有未完成的申请
        pending = self.db.get_pending_applications()
        if any(user_id == uid for uid, _, _ in pending):
            await self.application.bot.send_message(chat_id, "您已经有待审核的申请，请耐心等待。💕")
            return
        
        await self.application.bot.send_message(chat_id, """
请发送一段自我介绍视频和一张自拍照，我们将尽快审核您的申请。💕
            
注意：请先发送视频，然后发送照片。
            """)
    
    async def handle_video(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # 保存视频URL
        video_url = update.effective_message.video.file_id
        
        await self.application.bot.send_message(chat_id, "请发送一张自拍照。💕")
    
    async def handle_photo(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        if not update.effective_message.photo:
            await self.application.bot.send_message(chat_id, "请发送一张照片。💕")
            return
        
        # 保存照片URL
        photo_url = update.effective_message.photo[-1].file_id
        
        # 保存到数据库
        self.db.add_application(user_id, video_url, photo_url)
        
        # 通知管理员
        admin_message = format_application_message(user_id, video_url, photo_url)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("通过", callback_data=f"approve_application_{user_id}"),
             InlineKeyboardButton("拒绝", callback_data=f"reject_application_{user_id}")]
        ])
        
        await self.application.bot.send_message(ADMIN_ID, admin_message, reply_markup=keyboard)
        
        await self.application.bot.send_message(chat_id, "您的申请已提交，我们将在24小时内审核。💕")
    
    async def process_callback(self, update: Update, context: CallbackContext):
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("approve_application_"):
            user_id = int(query.data.split("_")[-1])
            self.db.update_application_status(user_id, "approved")
            await self.application.bot.send_message(user_id, "恭喜！您的主播申请已通过审核。💕 接下来请完成注册流程。")
            await self.application.bot.edit_message_text("申请已通过", query.message.chat.id, query.message.message_id)
            
            # 触发注册流程
            await self.application.bot.send_message(user_id, """
请发送以下信息完成注册：
1. 用户名（邮箱或手机号）
2. ID（大写字母与数字）
3. 昵称（汉字数字字母）
            """)
        
        elif query.data.startswith("reject_application_"):
            user_id = int(query.data.split("_")[-1])
            self.db.update_application_status(user_id, "rejected")
            await self.application.bot.send_message(user_id, "很抱歉，您的申请未通过审核。💕 您可以重新申请。")
            await self.application.bot.edit_message_text("申请已拒绝", query.message.chat.id, query.message.message_id)
