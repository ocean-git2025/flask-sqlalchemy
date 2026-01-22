from flask import Blueprint, request, jsonify
from app.models.user import User

user_bp = Blueprint('user', __name__)

# 获取 Flask-SQLAlchemy 版本
def get_fsa_version():
    try:
        import pkg_resources
        return pkg_resources.get_distribution('Flask-SQLAlchemy').version
    except:
        return '2.5.1'  # 默认版本

# 检查版本并返回对应的分页参数名
def get_paginate_param():
    version = get_fsa_version()
    try:
        # 提取主版本号，处理非标准版本号
        version_parts = version.split('.')
        if version_parts:
            major_str = ''.join(filter(str.isdigit, version_parts[0]))
            if major_str:
                major = int(major_str)
                return 'per_page' if major >= 3 else 'page_size'
    except:
        pass
    # 为了兼容 3.x 版本，默认使用 per_page
    return 'per_page'

@user_bp.route('/api/users', methods=['GET'])
def get_users():
    # 参数校验
    try:
        # 获取参数，设置默认值
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 10, type=int)
        
        # 验证参数合法性
        if not isinstance(page, int) or not isinstance(size, int):
            return jsonify({
                'code': 400,
                'detail': '参数错误：page 和 size 必须为整数'
            }), 400
        
        if page < 1:
            return jsonify({
                'code': 400,
                'detail': '参数错误：page 必须≥1'
            }), 400
        
        if page > 1000:
            return jsonify({
                'code': 400,
                'detail': '参数错误：page 不能超过 1000'
            }), 400
        
        if size < 1 or size > 50:
            return jsonify({
                'code': 400,
                'detail': '参数错误：size 必须在 1-50 之间'
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            'code': 400,
            'detail': '参数错误：page 和 size 必须为整数'
        }), 400
    
    try:
        # 动态选择分页参数
        param_name = get_paginate_param()
        # 直接使用 per_page 参数，兼容 3.x 版本
        users = User.query.paginate(page=page, per_page=size)
        
        user_list = [{
            'id': user.id,
            'username': user.username,
            'email': user.email
        } for user in users.items]
        
        # 计算总页数
        pages = (users.total + size - 1) // size
        
        return jsonify({
            'code': 200,
            'data': {
                'users': user_list,
                'total': users.total,
                'current_page': page,
                'page_size': size,
                'pages': pages
            },
            'msg': 'success'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'detail': '服务错误：' + str(e)
        }), 500
