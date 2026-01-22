from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # 创建数据库表
    db.create_all()
    
    # 插入测试数据
    for i in range(1, 101):
        user = User(
            username=f'user{i}',
            email=f'user{i}@example.com'
        )
        db.session.add(user)
    
    db.session.commit()
    print('数据库初始化完成，已插入 100 条测试数据')