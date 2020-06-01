import pymysql

#db = pymysql.connect(host='192.168.10.158', user='xue', port='3306', password='123456', database='test')
db=pymysql.connect(host='localhost',user='xue',password='123456',database='bank')
cursor = db.cursor()
#sql = "insert into card values('%s','%s','%s','%s','%s','%s','%s','%s')" %\
#    (str(13124111), '111', '12', '111',
#     '33', '11', '111', '111')



sql = '''create table if not exists loan(
loan_id varchar(20) not null PRIMARY KEY,
card_id varchar(20),
money decimal(19,4),
date varchar(10),
duration varchar(10),
interest varchar(10)
)
'''
cursor.execute(sql)


sql = '''create table if not exists person(
person_id varchar(18) not null PRIMARY KEY,
person_name varchar(20),
phone varchar(15),
position_id varchar(10)
)
'''
cursor.execute(sql)


sql = '''create table if not exists transaction(
trans_id varchar(20) not null PRIMARY KEY,
card_id varchar(20),
type varchar(10),
money decimal(19,4),
trans_date varchar(20)
)
'''
cursor.execute(sql)


sql = '''create table if not exists card(
card_id varchar(20) not null PRIMARY KEY,
branch_id varchar(10),
person_id varchar(18),
ctype varchar(10),
money decimal(19,4),
password varchar(6),
credit_limit decimal(19,4),
amount_credit decimal(19,4)
)
'''
cursor.execute(sql)

sql = '''create table if not exists post(
post_id varchar(20) not null PRIMARY KEY,
post_name varchar(10),
loan_limit decimal(19,4)
)
'''
cursor.execute(sql)
'''
sql="insert into post values('%s','%s','%s','%s')"%('0','游民',0)
sql="insert into post values('%s','%s','%s','%s')"%('1','职工',10000)
sql="insert into post values('%s','%s','%s','%s')"%('2','项目经理',100000)
sql="insert into post values('%s','%s','%s','%s')"%('3','总经理',1000000)
sql="insert into post values('%s','%s','%s','%s')"%('4','董事长',10000000)
'''