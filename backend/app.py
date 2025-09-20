from flask import Flask, jsonify, request
from flask_cors import CORS  # 已导入，无需新增
import mysql.connector
import random
import os
import hashlib
import uuid
from mysql.connector import Error

app = Flask(__name__)

# -------------------------- 关键修改：修复 CORS 配置 --------------------------
# 1. 允许前端域名（http://localhost:8080）跨域
# 2. 开启 credentials=True，允许前端携带凭证（对应前端的 credentials: 'include'）
CORS(
    app,
    supports_credentials=True,  # 必须开启，否则前端凭证请求被拦截
    origins="http://localhost:8080"  # 明确指定前端地址（你的前端运行在 8080 端口）
)
# -----------------------------------------------------------------------------

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '123456'),
    'database': os.getenv('MYSQL_DB', 'mysql_life')  # 确保与 docker-compose 中的数据库名一致
}


def create_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None


# 密码加密函数
def encrypt_password(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    return sha256.hexdigest()


# 用户注册接口（无需修改）
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'code': 400, 'msg': '用户名和密码不能为空'})

    conn = create_db_connection()
    if not conn:
        return jsonify({'code': 500, 'msg': '数据库连接失败'})

    try:
        cursor = conn.cursor()

        # 检查用户名是否已存在
        cursor.execute("SELECT id FROM user WHERE username = %s", (username,))
        if cursor.fetchone():
            return jsonify({'code': 400, 'msg': '用户名已存在'})

        # 插入新用户
        encrypted_pwd = encrypt_password(password)
        cursor.execute(
            "INSERT INTO user (username, password) VALUES (%s, %s)",
            (username, encrypted_pwd)
        )
        conn.commit()
        return jsonify({'code': 200, 'msg': '注册成功'})
    except Exception as e:
        conn.rollback()
        return jsonify({'code': 500, 'msg': f'注册失败: {str(e)}'})
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


# 用户登录接口（无需修改，已正确返回 token）
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'code': 400, 'msg': '用户名和密码不能为空'})

    conn = create_db_connection()
    if not conn:
        return jsonify({'code': 500, 'msg': '数据库连接失败'})

    try:
        cursor = conn.cursor(dictionary=True)
        encrypted_pwd = encrypt_password(password)

        cursor.execute(
            "SELECT id, username FROM user WHERE username = %s AND password = %s",
            (username, encrypted_pwd)
        )
        user = cursor.fetchone()

        if user:
            # 生成登录令牌（UUID 随机唯一，无需额外存储，前端存 localStorage 即可）
            token = str(uuid.uuid4())
            return jsonify({
                'code': 200,
                'msg': '登录成功',
                'token': token,
                'user': {'id': user['id'], 'username': user['username']}
            })
        else:
            return jsonify({'code': 401, 'msg': '用户名或密码错误'})
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'登录失败: {str(e)}'})
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


# 以下原有接口（应用、随机事项、游戏筛选）均无需修改
@app.route('/api/apps/types', methods=['GET'])
def get_app_types():
    conn = create_db_connection()
    if not conn:
        return jsonify({'code': 500, 'msg': '数据库连接失败', 'data': []})
    try:
        cursor = conn.cursor()
        query = "SELECT DISTINCT Type FROM apps WHERE Type IS NOT NULL AND Type != ''"
        cursor.execute(query)
        types = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify({'code': 200, 'msg': 'success', 'data': types})
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'获取App类型错误: {str(e)}', 'data': []})


@app.route('/api/apps/by-type/<type_name>', methods=['GET'])
def get_apps_by_type(type_name):
    conn = create_db_connection()
    if not conn:
        return jsonify({'code': 500, 'msg': '数据库连接失败', 'data': []})
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT App_name, App_use, Related_app FROM apps WHERE Type = %s AND App_name IS NOT NULL"
        cursor.execute(query, (type_name,))
        apps = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'code': 200, 'msg': 'success', 'data': apps})
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'获取App列表错误: {str(e)}', 'data': []})


@app.route('/api/things/random', methods=['GET'])
def get_random_thing():
    used_ranks = request.args.get('usedRanks', '')
    try:
        used_rank_list = list(map(int, filter(None, used_ranks.split(',')))) if used_ranks else []
    except ValueError:
        used_rank_list = []

    conn = create_db_connection()
    if not conn:
        return jsonify({'code': 500, 'msg': '数据库连接失败'})

    try:
        cursor = conn.cursor(dictionary=True)
        if not used_rank_list:
            query = "SELECT * FROM things"
        else:
            used_str = ", ".join(map(str, used_rank_list))
            query = f"SELECT * FROM things WHERE `Rank` NOT IN ({used_str})"

        print(f"执行的 SQL: {query}")
        cursor.execute(query)
        all_things = cursor.fetchall()

        if not all_things:
            return jsonify({'code': 404, 'msg': '所有事项已展示完毕'})

        random_thing = random.choice(all_things)
        cursor.close()
        conn.close()
        return jsonify({'code': 200, 'msg': 'success', 'data': random_thing})
    except Exception as e:
        print(f"SQL 错误: {str(e)}")
        return jsonify({'code': 500, 'msg': f'获取随机事项错误: {str(e)}'})


@app.route('/api/filters/meta', methods=['GET'])
def get_filter_meta():
    connection = create_db_connection()
    if not connection:
        return jsonify({'code': 500, 'msg': '数据库连接失败', 'data': {}})

    try:
        cursor = connection.cursor()
        meta_data = {'genres': [], 'platforms': [], 'publishers': []}

        cursor.execute("SELECT DISTINCT Genre FROM game_sales WHERE Genre IS NOT NULL AND Genre != '' ORDER BY Genre")
        meta_data['genres'] = [row[0] for row in cursor.fetchall()] or []
        cursor.execute(
            "SELECT DISTINCT Platform FROM game_sales WHERE Platform IS NOT NULL AND Platform != '' ORDER BY Platform")
        meta_data['platforms'] = [row[0] for row in cursor.fetchall()] or []
        cursor.execute(
            "SELECT DISTINCT Publisher FROM game_sales WHERE Publisher IS NOT NULL AND Publisher != '' ORDER BY Publisher")
        meta_data['publishers'] = [row[0] for row in cursor.fetchall()] or []

        print(
            f"筛选器元数据：类型{len(meta_data['genres'])}个，平台{len(meta_data['platforms'])}个，发行商{len(meta_data['publishers'])}个")
        return jsonify({'code': 200, 'msg': 'success', **meta_data})

    except Error as e:
        error_msg = f"筛选器元数据查询错误: {str(e)}"
        print(error_msg)
        return jsonify({'code': 500, 'msg': error_msg, 'data': {}})
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.route('/api/games/filtered', methods=['GET'])
def get_filtered_games():
    genre = request.args.get('genre', '').strip()
    platform = request.args.get('platform', '').strip()
    publisher = request.args.get('publisher', '').strip()

    print(f"\n【筛选参数】genre='{genre}', platform='{platform}', publisher='{publisher}'")

    if not all([genre, platform, publisher]):
        return jsonify({'code': 400, 'msg': '请选择完整的筛选条件（类型/平台/发行商）', 'data': []})

    connection = create_db_connection()
    if not connection:
        return jsonify({'code': 500, 'msg': '数据库连接失败', 'data': []})

    try:
        cursor = connection.cursor(dictionary=True)
        query = (
            "SELECT `Rank`, Name, Platform, Publisher, Genre, Global_Sales "
            "FROM game_sales "
            "WHERE LOWER(TRIM(Genre)) = LOWER(%s) "
            "AND LOWER(TRIM(Platform)) = LOWER(%s) "
            "AND LOWER(TRIM(Publisher)) = LOWER(%s) "
            "ORDER BY Global_Sales DESC"
        )

        cursor.execute(query, (genre, platform, publisher))
        games = cursor.fetchall()
        print(f"【执行SQL】{cursor.statement}")
        print(f"【筛选结果】查询到 {len(games)} 条数据")

        result = []
        for game in games:
            result.append({
                'Rank': game.get('Rank', game.get('rank', 0)),
                'Name': game.get('Name', game.get('name', '未知游戏')),
                'Platform': game.get('Platform', game.get('platform', '未知平台')),
                'Publisher': game.get('Publisher', game.get('publisher', '未知发行商')),
                'Genre': game.get('Genre', game.get('genre', '未知类型')),
                'Global_Sales': float(game.get('Global_Sales', game.get('global_sales', 0)))
                if (game.get('Global_Sales') or game.get('global_sales')) else 0.0
            })

        return jsonify({'code': 200, 'msg': 'success', 'data': result})

    except Error as e:
        error_msg = f"筛选查询错误: SQL={cursor.statement if 'cursor' in locals() else '未生成'}, 错误={str(e)}"
        print(f"【筛选错误】{error_msg}")
        return jsonify({'code': 500, 'msg': error_msg, 'data': []})
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == '__main__':
    print("后端服务启动中...")
    print(f"数据库配置：{DB_CONFIG}")
    app.run(host='0.0.0.0', port=5000, debug=True)