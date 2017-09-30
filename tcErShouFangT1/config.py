import pymysql.cursors

class chuzufang(object):
    # 二级id
    category_second_id = "1010"

class ershoufang(object):
    #二级id
    category_second_id = "1013"

class duanzufang(object):
    # 二级id
    category_second_id = '1011'

class qiuzufang(object):
    # 二级id
    category_second_id = "1012"

class changfang(object):
    changfang_second_id = "1017"
    cangku_second_id = "1018"
    cheku_second_id = "1020"
    tudi_second_id = "1019"
    qita_second_id = "1021"

class xiezilou(object):
    category_second_id = "1014"

class shangpu(object):
    shangpu_second_id = "1016"
    shengyi_second_id = "1015"


class config(object):
    # house 服务器IP
    mongo_server_house_ip = "119.29.35.21"
    # house 服务器端口号
    mongo_server_house_port = 27017
    # 用户名
    mongo_user = "root"
    # 用户名密码
    mongo_password = "Ktz.com123"
    @classmethod
    def get_mysql_connection_db_fangchan(cls):
        connection = pymysql.connect(host="5992da28ec8f4.sh.cdb.myqcloud.com",
                                     user="root",
                                     password="Ktzcom@123",
                                     db="db_fangchan", charset="utf8mb4",
                                     port= 5532
                                     )
        return connection

    @classmethod
    def get_mysql_connection_db_task(cls):
        connection = pymysql.connect(host="localhost",
                                     user="root",
                                     password="123456",
                                     db="db_fangchan", charset="utf8mb4"
                                     )
        return connection

    @classmethod
    def get_mysql_connection_db_sys_global(cls):
        connection = pymysql.connect(host="5992da28ec8f4.sh.cdb.myqcloud.com",
                                     user="root",
                                     password="Ktz.com123",
                                     db="sys_global", charset="utf8mb4"
                                     )
        return connection
