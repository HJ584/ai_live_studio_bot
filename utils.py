import logging
from datetime import datetime

# 设置日志
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ai_live_studio_bot.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    return logger

# 格式化消息
def format_welcome_message(user_name):
    return f"""
💖 欢迎加入爱即直播工作室！💖
    
亲爱的 {user_name}，感谢您选择我们！

为了完成您的主播注册，请发送以下信息：
1. 91APP 用户名（邮箱或手机号）
2. 91APP ID（大写字母与数字）
3. 91APP 昵称（汉字数字字母）

我们将尽快审核您的信息。💕
    """

def format_application_message(user_id, video_url, photo_url):
    return f"""
🔔 新的主播应聘申请！🔔
    
应聘者ID: {user_id}
视频: {video_url}
照片: {photo_url}

请审核此申请。💕
    """

def format_registration_message(user_id, username, streamer_id, nickname):
    return f"""
🔔 新的主播注册申请！🔔
    
91APP 注册者ID: {user_id}
91APP 用户名: {username}
91APP 主播ID: {streamer_id}
91APP 昵称: {nickname}

请审核此申请。💕
    """

def format_checkin_reminder(user_name, monthly_total, daily_min):
    return f"""
⏰ 91APP 直播提醒！⏰
    
亲爱的 {user_name}，本月已直播 {monthly_total} 分钟。

请确保每天至少直播 {daily_min} 分钟，以满足最低要求哦！💕
    """

def format_monthly_summary(user_name, total_minutes):
    return f"""
🎉 月度总结！🎉
    
亲爱的 {user_name}，本月您总共直播了 {total_minutes} 分钟！

感谢您的努力工作，期待下个月更精彩的表现！💕
    """
