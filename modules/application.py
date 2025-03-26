from telebot import TeleBot, types
from database import Database
from config import BRAND_LOGO, ADMIN_ID
from utils import format_application_message

class ApplicationModule:
    def __init__(self, bot: TeleBot, db: Database):
        self.bot = bot
        self.db = db
        self._setup_handlers()
    
    def _setup_handlers(self):
        @self.bot.message_handler(commands=['apply'])
        def handle_apply(message):
            user_id = message.from_user.id
            chat_id = message.chat.id
            
            # 检查是否有未完成的申请
            pending = self.db.get_pending_applications()
            if any(user_id == uid for uid, _, _ in pending):
                self.bot.reply_to(message, "您已经有待审核的申请，请耐心等待。💕")
                return
            
            self.bot.reply_to(message, """
请发送一段自我介绍视频和一张自拍照，我们将尽快审核您的申请。💕
            
注意：请先发送视频，然后发送照片。
            """)
            self.bot.register_next_step_handler(message, self._handle_video)
        
        @self.bot.message_handler(content_types=['video'])
        def handle_video(message):
            if message.reply_to_message and message.reply_to_message.text == "请发送一段自我介绍视频和一张自拍照，我们将尽快审核您的申请。💕":
                self._handle_video(message)
        
        @self.bot.message_handler(content_types=['photo'])
        def handle_photo(message):
            if message.reply_to_message and message.reply_to_message.text == "请发送一张自拍照。💕":
                self._handle_photo(message)
    
    def _handle_video(self, message):
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        # 保存视频URL
        video_url = self.bot.get_file_url(message.video.file_id)
        
        self.bot.reply_to(message, "请发送一张自拍照。💕")
        self.bot.register_next_step_handler(message, self._handle_photo, video_url=video_url)
    
    def _handle_photo(self, message, video_url=None):
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        if not message.photo:
            self.bot.reply_to(message, "请发送一张照片。💕")
            self.bot.register_next_step_handler(message, self._handle_photo, video_url=video_url)
            return
        
        # 保存照片URL
        photo_url = self.bot.get_file_url(message.photo[-1].file_id)
        
        # 保存到数据库
        self.db.add_application(user_id, video_url, photo_url)
        
        # 通知管理员
        admin_message = format_application_message(user_id, video_url, photo_url)
        keyboard = types.InlineKeyboardMarkup()
        approve_btn = types.InlineKeyboardButton("通过", callback_data=f"approve_application_{user_id}")
        reject_btn = types.InlineKeyboardButton("拒绝", callback_data=f"reject_application_{user_id}")
        keyboard.add(approve_btn, reject_btn)
        
        self.bot.send_message(ADMIN_ID, admin_message, reply_markup=keyboard)
        
        self.bot.reply_to(message, "您的申请已提交，我们将在24小时内审核。💕")
    
    def process_callback(self, call):
        if call.data.startswith("approve_application_"):
            user_id = int(call.data.split("_")[-1])
            self.db.update_application_status(user_id, "approved")
            self.bot.answer_callback_query(call.id, "申请已通过！")
            self.bot.send_message(user_id, "恭喜！您的主播申请已通过审核。💕 接下来请完成注册流程。")
            self.bot.edit_message_text("申请已通过", call.message.chat.id, call.message.message_id)
            
            # 触发注册流程
            self.bot.send_message(user_id, """
请发送以下信息完成注册：
1. 91APP 用户名（邮箱或手机号）
2. 91APP ID（大写字母与数字）
3. 91APP 昵称（汉字数字字母）
            """)
        
        elif call.data.startswith("reject_application_"):
            user_id = int(call.data.split("_")[-1])
            self.db.update_application_status(user_id, "rejected")
            self.bot.answer_callback_query(call.id, "申请已拒绝")
            self.bot.send_message(user_id, "很抱歉，您的申请未通过审核。💕 您可以重新申请。")
            self.bot.edit_message_text("申请已拒绝", call.message.chat.id, call.message.message_id)
