from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from database import Database
from config import ADMIN_ID, BRAND_LOGO

class AdminModule:
    def __init__(self, application, db):
        self.application = application
        self.db = db
        self._setup_handlers()
    
    def _setup_handlers(self):
        self.application.add_handler(CommandHandler('admin', self.handle_admin))
    
    async def handle_admin(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # 检查是否为管理员
        if user_id != ADMIN_ID:
            await self.application.bot.send_message(chat_id, "您没有管理员权限。💕")
            return
        
        keyboard = [[InlineKeyboardButton("审核应聘", callback_data="review_applications"),
                     InlineKeyboardButton("审核注册", callback_data="review_registrations"),
                     InlineKeyboardButton("设置小管理员", callback_data="set_subadmin"),
                     InlineKeyboardButton("修改最低直播时长", callback_data="set_min_stream_time")]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await self.application.bot.send_message(chat_id, "管理员菜单", reply_markup=reply_markup)
    
    async def process_callback(self, update: Update, context: CallbackContext):
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        chat_id = query.message.chat.id
        
        if user_id != ADMIN_ID:
            await self.application.bot.send_message(chat_id, "您没有管理员权限。💕")
            return
        
        if query.data == "review_applications":
            pending = self.db.get_pending_applications()
            if not pending:
                await self.application.bot.send_message(chat_id, "目前没有待审核的应聘申请。💕")
                return
            
            for uid, video_url, photo_url in pending:
                admin_message = format_application_message(uid, video_url, photo_url)
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("通过", callback_data=f"approve_application_{uid}"),
                     InlineKeyboardButton("拒绝", callback_data=f"reject_application_{uid}")]
                ])
                
                await self.application.bot.send_message(chat_id, admin_message, reply_markup=keyboard)
        
        elif query.data == "review_registrations":
            pending = self.db.get_pending_registrations()
            if not pending:
                await self.application.bot.send_message(chat_id, "目前没有待审核的注册申请。💕")
                return
            
            for uid, username, streamer_id, nickname in pending:
                admin_message = format_registration_message(uid, username, streamer_id, nickname)
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("通过", callback_data=f"approve_registration_{uid}"),
                     InlineKeyboardButton("拒绝", callback_data=f"reject_registration_{uid}")]
                ])
                
                await self.application.bot.send_message(chat_id, admin_message, reply_markup=keyboard)
        
        elif query.data == "set_subadmin":
            await self.application.bot.send_message(chat_id, "请输入小管理员的用户ID：")
        
        elif query.data == "set_min_stream_time":
            await self.application.bot.send_message(chat_id, "请输入新的最低直播时长（分钟）：")
        
        elif query.data.startswith("approve_application_"):
            uid = int(query.data.split("_")[-1])
            self.db.update_application_status(uid, "approved")
            await self.application.bot.send_message(uid, "恭喜！您的主播申请已通过审核。💕 接下来请完成注册流程。")
            await self.application.bot.edit_message_text("申请已通过", query.message.chat.id, query.message.message_id)
            
            # 触发注册流程
            await self.application.bot.send_message(uid, """
请发送以下信息完成注册：
1. 用户名（邮箱或手机号）
2. ID（大写字母与数字）
3. 昵称（汉字数字字母）
            """)
        
        elif query.data.startswith("reject_application_"):
            uid = int(query.data.split("_")[-1])
            self.db.update_application_status(uid, "rejected")
            await self.application.bot.send_message(uid, "很抱歉，您的申请未通过审核。💕 您可以重新申请。")
            await self.application.bot.edit_message_text("申请已拒绝", query.message.chat.id, query.message.message_id)
        
        elif query.data.startswith("approve_registration_"):
            uid = int(query.data.split("_")[-1])
            self.db.update_registration_status(uid, "approved")
            await self.application.bot.send_message(uid, "恭喜！您的注册已通过审核。💕 您可以开始使用打卡功能了。")
            await self.application.bot.edit_message_text("注册已通过", query.message.chat.id, query.message.message_id)
        
        elif query.data.startswith("reject_registration_"):
            uid = int(query.data.split("_")[-1])
            self.db.update_registration_status(uid, "rejected")
            await self.application.bot.send_message(uid, "很抱歉，您的注册未通过审核。💕 您可以重新申请。")
            await self.application.bot.edit_message_text("注册已拒绝", query.message.chat.id, query.message.message_id)
