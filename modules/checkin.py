from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters
from database import Database
from config import MIN_DAILY_STREAM_TIME, BRAND_LOGO
from utils import format_checkin_reminder, format_monthly_summary
from datetime import datetime, timedelta
import schedule
import time
from apscheduler.schedulers.background import BackgroundScheduler

class CheckinModule:
    def __init__(self, application, db):
        self.application = application
        self.db = db
        self._setup_handlers()
        self._setup_scheduler()
    
    def _setup_handlers(self):
        self.application.add_handler(CommandHandler('checkin', self.handle_checkin))
        self.application.add_handler(CommandHandler('checkout', self.handle_checkout))
        self.application.add_handler(CommandHandler('stats', self.handle_stats))
    
    async def handle_checkin(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # 检查是否已打卡
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute('SELECT start_time FROM checkins WHERE user_id = ? AND checkin_date = ?', (user_id, today))
        result = self.cursor.fetchone()
        
        if result:
            await self.application.bot.send_message(chat_id, "您今天已经打过卡了。💕")
            return
        
        # 记录打卡时间
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.record_checkin(user_id, now)
        await self.application.bot.send_message(chat_id, "打卡成功！💕 请在直播结束后再次打卡。")
    
    async def handle_checkout(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # 检查是否已打卡
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute('SELECT start_time FROM checkins WHERE user_id = ? AND checkin_date = ?', (user_id, today))
        result = self.cursor.fetchone()
        
        if not result:
            await self.application.bot.send_message(chat_id, "您今天尚未打卡。💕 请先使用/checkin命令打卡。")
            return
        
        # 记录下播时间
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.record_checkout(user_id, now)
        await self.application.bot.send_message(chat_id, "下播打卡成功！💕 今天的直播时长已记录。")
    
    async def handle_stats(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        monthly_total = self.db.get_monthly_stats(user_id)
        await self.application.bot.send_message(chat_id, f"本月累计直播时长：{monthly_total} 分钟。💕")
    
    def _setup_scheduler(self):
        # 创建调度器
        scheduler = BackgroundScheduler()
        
        # 每天检查打卡情况
        scheduler.add_job(self._daily_check, 'cron', hour=23, minute=59)
        
        # 每月最后一天发送总结
        scheduler.add_job(self._monthly_summary, 'cron', day='30-31', hour=23, minute=59)
        
        scheduler.start()
    
    def _daily_check(self):
        # 获取所有注册用户
        self.cursor.execute('SELECT user_id FROM registrations WHERE status = "approved"')
        users = self.cursor.fetchall()
        
        today = datetime.now().strftime("%Y-%m-%d")
        min_daily = MIN_DAILY_STREAM_TIME
        
        for user_id, in users:
            # 检查今日是否已打卡
            self.cursor.execute('SELECT duration FROM checkins WHERE user_id = ? AND checkin_date = ?', (user_id, today))
            result = self.cursor.fetchone()
            
            if not result:
                # 未打卡，发送提醒
                self.application.bot.send_message(user_id, "今天还没打卡哦！💕 请记得使用/checkin命令开始直播打卡。")
                continue
            
            duration = result[0]
            if duration < min_daily:
                # 未达到最低时长，发送提醒
                monthly_total = self.db.get_monthly_stats(user_id)
                self.application.bot.send_message(user_id, format_checkin_reminder(user_id, monthly_total, min_daily))
    
    def _monthly_summary(self):
        # 获取所有注册用户
        self.cursor.execute('SELECT user_id FROM registrations WHERE status = "approved"')
        users = self.cursor.fetchall()
        
        for user_id, in users:
            monthly_total = self.db.get_monthly_stats(user_id)
            self.application.bot.send_message(user_id, format_monthly_summary(user_id, monthly_total))
