class Config:
    # 数据库连接配置
    import os
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'users.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SQLite 专属配置
    # 注意：SQLite 不支持连接池，以下配置为 SQLite 专属优化
    SQLALCHEMY_ECHO = False  # 是否打印 SQL 语句，调试时可设为 True
    SQLALCHEMY_RECORD_QUERIES = False  # 是否记录查询
    
    # 数据备份配置
    DATA_BACKUP_PATH = './backups'
