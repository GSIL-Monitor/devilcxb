# -*- coding: utf-8 -*-
import MySQLdb
import MySQLdb.cursors
import logging
logging.basicConfig(level=logging.INFO)

class HandleSQL(object):
    def __init__(self, host, username, password, database, port=3306, dict_result = False, charset='utf8'):
        """
        初始化sql数据库连接
        :param host: IP地址
        :param username: 用户名
        :param password: 密码
        :param database: 数据库
        :param port: 端口，默认为3306
        :return: None
        """
        logging.info("init connection")
        if dict_result:
            self.db_con = MySQLdb.connect(host, username, password, database, port=port, cursorclass=MySQLdb.cursors.DictCursor, charset=charset)
        else:
            self.db_con = MySQLdb.connect(host, username, password, database, port=port, charset=charset)
        self.db_cursor = self.db_con.cursor()

    def query_sql(self, sql, return_result=False):
        """
        执行sql语句
        :param sql: sql语句
        :return: 返回result或者None
        """
        logging.info(sql)
        self.db_cursor.execute(sql)
        result = self.db_cursor.fetchall()
        if return_result:
            return result

    def commit_change(self):
        """
        保存修改
        :return:
        """
        self.db_con.commit()

    def close(self):
        """
        关闭sql连接
        :return:
        """
        self.db_cursor.close()
        self.db_con.close()

if __name__ == "__main__":
    HandleSQL = HandleSQL("10.115.101.231", "cmp_test", "Aa123456", "compatibility_test", 3306, dict_result=True)
    # print HandleSQL.query_sql("select id from devices", return_result=True)
    # print max(map(lambda x: x["id"], HandleSQL.query_sql("select id from devices", return_result=True)))
    print list(map(lambda x: x["model"], HandleSQL.query_sql('SELECT model FROM devices WHERE model LIKE "POP4-10_4G%"', return_result=True)))
    HandleSQL.close()