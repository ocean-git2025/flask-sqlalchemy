from flask import Blueprint, request, jsonify
from app.models.user import User

user_bp = Blueprint('user', __name__)

def get_flask_sqlalchemy_version():
    """获取已安装的 Flask-SQLAlchemy 版本"""
    try:
        import pkg_resources
        version = pkg_resources.get_distribution('Flask-SQLAlchemy').version
        return version
    except ImportError:
        # 缺失 pkg_resources 模块，默认使用 2.5.1 版本
        return '2.5.1'
    except Exception:
        # 其他异常，默认使用 2.5.1 版本
        return '2.5.1'

def is_version_3_or_higher(version):
    """判断是否为 3.x 版本"""
    try:
        # 处理非标准版本号，只取第一个数字
        version_part = version.split('.')[0]
        # 提取数字部分
        major_str = ''.join(filter(str.isdigit, version_part))
        if not major_str:
            return False
        major = int(major_str)
        return major >= 3
    except Exception:
        # 任何异常都返回 False，默认使用 2.5.1 的参数
        return False

@user_bp.route('/users', methods=['GET'])
def get_users():
    # 参数校验
    try:
        # 获取参数，设置默认值
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 10, type=int)
        
        # 严格校验参数
        if not isinstance(page, int) or page < 1:
            return jsonify({"code": 400, "detail": "参数错误：page 必须≥1"}), 400
        if page > 1000:
            return jsonify({"code": 400, "detail": "参数错误：page 不能超过 1000"}), 400
        if not isinstance(size, int) or size < 1:
            return jsonify({"code": 400, "detail": "参数错误：size 必须≥1"}), 400
        if size > 50:
            return jsonify({"code": 400, "detail": "参数错误：size 不能超过 50"}), 400
    except (ValueError, TypeError):
        return jsonify({"code": 400, "detail": "参数错误：page 和 size 必须为整数"}), 400
    
    # 版本适配逻辑
    fsa_version = get_flask_sqlalchemy_version()
    is_v3 = is_version_3_or_higher(fsa_version)
    
    # 根据版本选择正确的参数名
    if is_v3:
        # 3.x 版本使用 per_page
        users = User.query.paginate(page=page, per_page=size)
    else:
        # 2.5.1 版本也使用 per_page
        users = User.query.paginate(page=page, per_page=size)
    
    user_list = []
    for user in users.items:
        user_list.append({
            'id': user.id,
            'username': user.username,
            'email': user.email
        })
    
    # 完善返回格式
    return jsonify({
        "code": 200,
        "data": {
            "users": user_list,
            "total": users.total,
            "current_page": page,
            "page_size": size,
            "pages": users.pages
        },
        "msg": "success"
    })