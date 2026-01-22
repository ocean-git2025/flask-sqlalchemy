from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 用户名：非空 + 唯一，长度限制为 80 字符
    # 索引：加速用户名查询和唯一性检查
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    
    # 邮箱：非空 + 唯一，长度限制为 120 字符
    # 索引：加速邮箱查询和唯一性检查
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    
    # 新增字段：创建时间，默认值为当前时间
    # 索引：加速按创建时间排序和查询
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), index=True)
    
    # 新增字段：更新时间，默认值为当前时间，自动更新
    # 索引：加速按更新时间排序和查询
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), index=True)
    
    def __str__(self):
        """便于日志打印的字符串表示"""
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"
    
    def __repr__(self):
        """详细的字符串表示，用于调试"""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', created_at={self.created_at})>"