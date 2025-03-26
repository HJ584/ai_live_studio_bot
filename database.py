import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        # 主播应聘表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            user_id INTEGER PRIMARY KEY,
            video_url TEXT,
            photo_url TEXT,
            status TEXT DEFAULT 'pending',
            apply_date TEXT
        )
        ''')
        
        # 主播注册表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            streamer_id TEXT,
            nickname TEXT,
            status TEXT DEFAULT 'pending',
            register_date TEXT
        )
        ''')
        
        # 直播打卡记录表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS checkins (
            user_id INTEGER,
            checkin_date TEXT,
            start_time TEXT,
            end_time TEXT,
            duration INTEGER,
            PRIMARY KEY (user_id, checkin_date)
        )
        ''')
        
        # 管理员表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            admin_id INTEGER PRIMARY KEY,
            permission_level INTEGER DEFAULT 1,  # 1: 小管理员, 2: 超级管理员
            added_date TEXT
        )
        ''')
        
        self.conn.commit()
    
    def add_application(self, user_id, video_url, photo_url):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute('''
        INSERT OR REPLACE INTO applications (user_id, video_url, photo_url, status, apply_date)
        VALUES (?, ?, ?, 'pending', ?)
        ''', (user_id, video_url, photo_url, date))
        self.conn.commit()
    
    def get_pending_applications(self):
        self.cursor.execute('SELECT user_id, video_url, photo_url FROM applications WHERE status = "pending"')
        return self.cursor.fetchall()
    
    def update_application_status(self, user_id, status):
        self.cursor.execute('UPDATE applications SET status = ? WHERE user_id = ?', (status, user_id))
        self.conn.commit()
    
    def add_registration(self, user_id, username, streamer_id, nickname):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute('''
        INSERT OR REPLACE INTO registrations (user_id, username, streamer_id, nickname, status, register_date)
        VALUES (?, ?, ?, ?, 'pending', ?)
        ''', (user_id, username, streamer_id, nickname, date))
        self.conn.commit()
    
    def get_pending_registrations(self):
        self.cursor.execute('SELECT user_id, username, streamer_id, nickname FROM registrations WHERE status = "pending"')
        return self.cursor.fetchall()
    
    def update_registration_status(self, user_id, status):
        self.cursor.execute('UPDATE registrations SET status = ? WHERE user_id = ?', (status, user_id))
        self.conn.commit()
    
    def record_checkin(self, user_id, start_time):
        date = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute('''
        INSERT INTO checkins (user_id, checkin_date, start_time, duration)
        VALUES (?, ?, ?, 0)
        ON CONFLICT(user_id, checkin_date) DO UPDATE SET start_time = excluded.start_time
        ''', (user_id, date, start_time))
        self.conn.commit()
    
    def record_checkout(self, user_id, end_time):
        date = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute('''
        UPDATE checkins 
        SET end_time = ?, duration = strftime('%s', ?) - strftime('%s', start_time)
        WHERE user_id = ? AND checkin_date = ?
        ''', (end_time, end_time, user_id, date))
        self.conn.commit()
    
    def get_monthly_stats(self, user_id):
        month = datetime.now().strftime("%Y-%m")
        self.cursor.execute('''
        SELECT SUM(duration) FROM checkins 
        WHERE user_id = ? AND checkin_date LIKE ?
        ''', (user_id, f"{month}%"))
        return self.cursor.fetchone()[0] or 0
    
    def add_admin(self, admin_id, permission_level=1):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute('''
        INSERT INTO admins (admin_id, permission_level, added_date)
        VALUES (?, ?, ?)
        ''', (admin_id, permission_level, date))
        self.conn.commit()
    
    def get_admin_level(self, admin_id):
        self.cursor.execute('SELECT permission_level FROM admins WHERE admin_id = ?', (admin_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0
    
    def close(self):
        self.conn.close()
