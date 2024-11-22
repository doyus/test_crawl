import time
import pymysql
def connect_to_mysql(host, user, password, database, max_retries=5, timeout=5):
    retries = 0
    while retries < max_retries:
        try:
            connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                connect_timeout=timeout,cursorclass=pymysql.cursors.DictCursor  # 设置连接超时
            )
            return connection
        except pymysql.MySQLError as e:
            print(f"连接失败: {e}")
            retries += 1
            print(f"尝试重连...（{retries}/{max_retries}）")
            time.sleep(2)  # 等待一段时间再尝试重连
    print("无法连接到 MySQL 服务器，已达到最大重试次数")
    return None

db_username = ''
db_password = ''
db_host = '..31.145'  # 更改为你的MySQL主机
db_name = 'spider'
db_port = 3306
conn = connect_to_mysql(db_host,db_username, db_password,'spider')
cursor = conn.cursor()
conn.ping(reconnect=True)