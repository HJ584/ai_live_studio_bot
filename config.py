import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 管理员ID
ADMIN_ID = os.getenv("ADMIN_ID")

# 数据库配置
DB_NAME = os.getenv("DB_NAME", "ai_live_studio.db")

# 每日最低直播时长（分钟）
MIN_DAILY_STREAM_TIME = int(os.getenv("MIN_DAILY_STREAM_TIME", 60))

# 品牌信息
BRAND_NAME = "爱即直播工作室"
BRAND_LOGO = "💖"
