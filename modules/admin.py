from telebot import TeleBot, types
from database import Database
from config import ADMIN_ID, BRAND_LOGO

class AdminModule:
    def __init__(self, bot: TeleBot, db: Database):
        self.bot = bot
        self.db = db
        self._setup_handlers()
    
    def _setup_handlers(self):
        @self.bot.message_handler(commands=['admin'])
        def handle_admin(message):
            user_id = message.from_user.id
            chat_id = message.chat.id
            
            # 检查是否为管理员
            if user_id != ADMIN_ID:
                self.bot.reply_to(message, "您没有管理员权限。💕")
                return
            
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("审核应聘")
            btn2 = types.KeyboardButton("审核注册")
            btn3 = types.KeyboardButton("设置小管理员")
            btn4 = types.KeyboardButton("修改最低直播时长")
            keyboard.add(btn1, btn2, btn3, btn4)
            
            self.bot.reply_to(message, "管理员菜单", reply_markup=keyboard)
        
        @self.bot.message_handler(func=lambda message: message.text == "审核应聘")
        def handle_review_applications(message):
            user_id = message.from_user.id
            chat_id = message.chat.id
            
            # 检查是否为管理员
            if user_id != ADMIN_ID:
                self.bot.reply_to(message, "您没有管理员权限。💕")
                return
            
            pending = self.db.get_pending_applications()
            if not pending:
                self.bot.reply_to(message, "目前没有待审核的应聘申请。💕")
                return
            
            for uid, video_url, photo_url in pending:
                admin_message = format_application_message(uid, video_url, photo_url)
                keyboard = types.InlineKeyboardMarkup()
                approve_btn = types.InlineKeyboardButton("通过", callback_data=f"approve_application_{uid}")
                reject_btn = types.InlineKeyboardButton("拒绝", callback_data=f"reject_application_{uid}")
                keyboard.add(approve_btn, reject_btn)
                
                self.bot.send_message(chat_id, admin_message, reply_markup=keyboard)
        
        @self.bot.message_handler(func=lambda message: message.text == "审核注册")
        def handle_review_registrations(message):
            user_id = message.from_user.id
            chat_id = message.chat.id
            
            # 检查是否为管理员
            if user_id != ADMIN_ID:
                self.bot.reply_to(message, "您没有管理员权限。💕")
                return
            
            pending = self.db.get_pending_registrations()
            if not pending:
                self.bot.reply_to(message, "目前没有待审核的注册申请。💕")
                return
            
            for uid, username, streamer_id, nickname in pending:
                admin_message = format_registration_message(uid, username, streamer_id, nickname)
                keyboard = types.InlineKeyboardMarkup()
                approve_btn = types.InlineKeyboardButton("通过", callback_data=f"approve_registration_{uid}")
                reject_btn = types.InlineKeyboardButton("拒绝", callback_data=f"reject_registration_{uid}")
                keyboard.add(approve_btn, reject_btn)
                
                self.bot.send_message(chat_id, admin_message, reply_markup=keyboard)
        
        @self.bot.message_handler(func=lambda message: message.text == "设置小管理员")
        def handle_set_subadmin(message):
            user_id = message.from_user.id
            chat_id = message.chat.id
            
            # 检查是否为超级管理员
            if user_id != ADMIN_ID:
                self.bot.reply_to(message, "您没有权限设置小管理员。💕")
                return
            
            self.bot.reply_to(message, "请输入小管理员的用户ID：")
            self.bot.register_next_step_handler(message, self._handle_set_subadmin)
        
        def _handle_set_subadmin(message):
            try:
                subadmin_id = int(message.text)
                self.db.add_admin(subadmin_id)
                self.bot.reply_to(message, f"已成功设置用户{subadmin_id}为小管理员。💕")
            except ValueError:
                self.bot.reply_to(message, "请输入有效的用户ID。💕")
        
        @self.bot.message_handler(func=lambda message: message.text == "修改最低直播时长")
        def handle_set_min_stream_time(message):
            user_id = message.from_user.id
            chat_id = message.chat.id
            
            # 检查是否为超级管理员
            if user_id != ADMIN_ID:
                self.bot.reply_to(message, "您没有权限修改最低直播时长。💕")
                return
            
            self.bot.reply_to(message, "请输入新的最低直播时长（分钟）：")
            self.bot.register_next_step_handler(message, self._handle_set_min_stream_time)
        
        def _handle_set_min_stream_time(message):
            try:
                new_time = int(message.text)
                # 这里需要将新值保存到配置中，实际应用中可能需要重启服务
                # 或使用更复杂的配置管理机制
                self.bot.reply_to(message, f"已将最低直播时长设置为{new_time}分钟。💕")
            except ValueError:
                self.bot.reply_to(message, "请输入有效的数字。💕")
    
    def process_callback(self, call):
        # 处理其他模块的回调
        pass
