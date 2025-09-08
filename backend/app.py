from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import random
import os

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'mysql-test'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '123456'),
    'database': os.getenv('MYSQL_DB', 'mysql-life')
}

def create_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

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
        # 严格区分两种情况，确保 used_str 只在 else 中使用
        if not used_rank_list:
            # 无已使用项：不涉及 used_str
            query = "SELECT * FROM things"
        else:
            # 有已使用项：先定义 used_str，再使用
            used_str = ", ".join(map(str, used_rank_list))
            query = f"SELECT * FROM things WHERE `Rank` NOT IN ({used_str})"  # 反引号保留
        
        print(f"执行的 SQL: {query}")  # 调试用
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

if __name__ == '__main__':
    print("后端服务启动中...")
    print(f"数据库配置：{DB_CONFIG}")
    app.run(host='0.0.0.0', port=5000, debug=True)