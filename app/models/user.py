from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 用户名，唯一索引，用于快速查询
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    # 邮箱，唯一索引，用于快速查询
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    # 创建时间，索引用于时间范围查询
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    # 更新时间，索引用于时间范围查询
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    def __repr__(self):
        return '<User %r>' % self.username
    
    def __str__(self):
        return f'User(id={self.id}, username={self.username}, email={self.email})'
