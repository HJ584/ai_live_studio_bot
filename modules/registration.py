from telebot import TeleBot, types
from database import Database
from config import ADMIN_ID
from utils import format_registration_message

class RegistrationModule:
    def __init__(self, bot: TeleBot, db: Database):
        self.bot = bot
        self.db = db
        self._setup_handlers()
    
    def _setup_handlers(self):
        @self.bot.message_handler(func=lambda message: message.reply_to_message and 
                                          message.reply_to_message.text == "请发送以下信息完成注册：\n1. 用户名（邮箱或手机号）\n2. ID（大写字母与数字）\n3. 昵称（汉字数字字母）")
        def handle_registration(message):
            user_id = message.from_user.id
            content = message.text.split('\n')
            
            if len(content) != 3:
                self.bot.reply_to(message, "请按照格式发送三条信息。💕")
                return
            
            username, streamer_id, nickname = content
            
            # 保存到数据库
            self.db.add_registration(user_id, username, streamer_id, nickname)
            
            # 通知管理员
            admin_message = format_registration_message(user_id, username, streamer_id, nickname)
            keyboard = types.InlineKeyboardMarkup()
            approve_btn = types.InlineKeyboardButton("通过", callback_data=f"approve_registration_{user_id}")
            reject_btn = types.InlineKeyboardButton("拒绝", callback_data=f"reject_registration_{user_id}")
            keyboard.add(approve_btn, reject_btn)
            
            self.bot.send_message(ADMIN_ID, admin_message, reply_markup=keyboard)
            
            self.bot.reply_to(message, "您的注册信息已提交，我们将在24小时内审核。💕")
    
    def process_callback(self, call):
        if call.data.startswith("approve_registration_"):
            user_id = int(call.data.split("_")[-1])
            self.db.update_registration_status(user_id, "approved")
            self.bot.answer_callback_query(call.id, "注册已通过！")
            self.bot.send_message(user_id, "恭喜！您的注册已通过审核。💕 您可以开始使用打卡功能了。")
            self.bot.edit_message_text("注册已通过", call.message.chat.id, call.message.message_id)
        
        elif call.data.startswith("reject_registration_"):
            user_id = int(call.data.split("_")[-1])
            self.db.update_registration_status(user_id, "rejected")
            self.bot.answer_callback_query(call.id, "注册已拒绝")
            self.bot.send_message(user_id, "很抱歉，您的注册未通过审核。💕 您可以重新申请。")
            self.bot.edit_message_text("注册已拒绝", call.message.chat.id, call.message.message_id)
