from app import app, db
from app.models.user import User

with app.app_context():
    # 创建数据库表
    db.create_all()
    
    try:
        # 清空现有数据
        db.session.query(User).delete()
    except Exception:
        pass
    
    # 插入 100 条测试数据
    for i in range(1, 101):
        user = User(
            username=f'user{i}',
            email=f'user{i}@example.com'
        )
        db.session.add(user)
    
    # 提交数据
    db.session.commit()
    
    print('数据库初始化完成，插入了 100 条测试数据')
