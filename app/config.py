class Config:
    # 数据库基本配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SQLite 专属配置
    # 注意：SQLite 是文件数据库，不支持连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'timeout': 15,  # SQLite 连接超时（秒）
            'cache_size': -10000,  # SQLite 缓存大小（-10000 表示 10MB）
            'journal_mode': 'WAL',  # 写入前日志模式，提高并发性能
            'synchronous': 'NORMAL',  # 同步级别，平衡性能和安全性
            'foreign_keys': 1,  # 启用外键约束
            'ignore_check_constraints': 0,  # 启用检查约束
            'temp_store': 'MEMORY',  # 临时表存储在内存中，提高性能
            'mmap_size': 30000000000  # 内存映射大小（30GB），提高大数据库性能
        }
    }
    
    # 数据备份路径配置
    DATABASE_BACKUP_PATH = 'backups/'
    DATABASE_BACKUP_INTERVAL = 3600  # 备份间隔（秒）
    
    # 数据库文件路径配置
    DATABASE_FILE = 'app.db'
    DATABASE_PATH = '.'  # 数据库文件存储路径