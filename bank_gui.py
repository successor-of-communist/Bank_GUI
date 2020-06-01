import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
import time
import tkinter.messagebox as messagebox
import pymysql
import datetime


class app:
    def __init__(self):
        self.main_win = tk.Tk()
        self.main_win.title("用户界面")
        self.main_win.geometry('500x300')
        self.main_win.minsize(400, 200)
        self.user_login_flag = False
        self.admin_login_flag = False
        self.button_font = tkfont.Font(family='Fixdsys', size=20)
        self.create_main_window()
        self.card_id=''
    
    def gettran_id(self,ty):
        dic={'贷款':0,'转账':1,'存款':2,'取款':3,'收入':4,'转账手续费':5,'还贷':6,'透支':7,'归还透支':8}
        return dic[ty]
    
    def gettime(self):
        t = time.localtime()
        ti = str(t.tm_year)+str(t.tm_mon).zfill(2)+str(
            t.tm_mday).zfill(2)+str(t.tm_hour).zfill(2)+str(t.tm_min).zfill(2)+str(t.tm_sec).zfill(2)
        return ti

    def init(self):
        self.user_login_flag = False
        self.admin_login_flag = False

    def son_win_closing(self, main_w, son_w):
        son_w.destroy()
        main_w.deiconify()
        self.init()

    def admin_son_win_closing(self, main_w, son_w):
        son_w.destroy()
        main_w.deiconify()

    def check_admin(self, son_win, password):
        if str(password.get()) == '':
            tk.messagebox.showinfo('提示', '口令正确！')
            self.admin_login_flag = True
            son_win.destroy()
        else:
            tk.messagebox.showerror('提示', '口令错误')

    def admin_login(self, event):
        self.main_win.withdraw()
        son_win = tk.Toplevel()
        son_win.title('管理员登陆')
        son_win.geometry('300x200')
        son_win.resizable(False, False)
        son_win.protocol("WM_DELETE_WINDOW",
                         lambda: self.son_win_closing(self.main_win, son_win))
        password = tk.StringVar()
        tk.Label(son_win,text='请输入管理员口令').pack()
        psw = tk.Entry(son_win, textvariable=password, show='*')
        psw.pack()
        login = tk.Button(son_win, text='确定', font=self.button_font,
                          command=lambda: self.check_admin(son_win, password))
        login.pack()
        son_win.wait_window()
        if self.admin_login_flag:
            self.admin_window()

    def check_user(self, son_win, id, psw, card_type):
        print(card_type)
        db,cursor=self.connect_db()
        sql="select password from card where card_id='%s'"%(str(id))
        cursor.execute(sql)
        data=cursor.fetchall()
        if len(data)==0 or data[0][0]!=psw:
            tk.messagebox.showerror('提示', '卡号或密码错误')
            return
        else:
            tk.messagebox.showinfo('提示', '登陆成功')
            self.user_login_flag = True
            son_win.destroy()

    def adopter_handler(self, fun, **kwds):
        return lambda event, fun=fun, kwds=kwds: fun(event, **kwds)

    def user_login(self):
        son_win = tk.Toplevel()
        son_win.title('用户登陆')
        son_win.geometry('350x200')
        son_win.resizable(False, False)
        son_font = tkfont.Font(family='Fixdsys', size=12)
        self.main_win.withdraw()
        frame = tk.Frame(son_win)
        tk.Label(frame, text='选择卡类别', font=son_font).grid(row=0)
        tk.Label(frame, text='卡号：', font=son_font).grid(row=1)
        tk.Label(frame, text='密码：', font=son_font).grid(row=2)
        son_win.protocol("WM_DELETE_WINDOW",
                         lambda: self.son_win_closing(self.main_win, son_win))
        combobox = ttk.Combobox(frame, state='readonly', font=son_font)
        combobox["values"] = ('湖北长城卡', '北京长城卡', '上海长城卡',
                              '湖北龙卡', '北京龙卡', '上海龙卡')
        combobox.grid(row=0, column=1)
        id = tk.StringVar()
        password = tk.StringVar()
        tk.Entry(frame, textvariable=id, font=son_font).grid(row=1, column=1)
        tk.Entry(frame, textvariable=password, show='*',
                 font=son_font).grid(row=2, column=1)
        tk.Button(frame, text='确定', font=son_font, command=lambda: self.check_user(
            son_win, id.get(), password.get(), combobox.get())).grid(row=3, rowspan=3, column=0, columnspan=2, pady=15)
        frame.pack(expand=tk.YES)
        son_win.wait_window()
        self.card_id = id.get()
        return self.user_login_flag

    def save_money_to_db(self, input_m):
        try:
            input_money = float(input_m.get())
        except:
            tk.messagebox.showerror('错误', '请输入正确的金额！')
        else:
            if input_money <= 0:
                tk.messagebox.showerror('错误', '请输入正确的金额！')
            else:
                db, cursor = self.connect_db()
                sql="select amount_credit from card where card_id='%s'"%(self.card_id)
                cursor.execute(sql)
                data=cursor.fetchall()
                ti=self.gettime()
                if float(data[0][0])>0:
                    if float(input_money)>float(data[0][0]):
                        sql = "update card set amount_credit='%f' where card_id='%s'" % (
                            float(0), str(self.card_id))
                        cursor.execute(sql)
                        sql = "insert into transaction values('%s','%s','%s','%f','%s')" % (
                            str(ti)+str(self.gettran_id('归还透支')), str(self.card_id), str('归还透支'), float(data[0][0]), str(ti[:-6]))
                        cursor.execute(sql)
                        sql = "update card set money=money+'%f' where card_id='%s'" % (
                            float(input_money)-float(data[0][0]), str(self.card_id))
                        cursor.execute(sql)
                        sql = "insert into transaction values('%s','%s','%s','%f','%s')" % (
                            str(ti)+str(self.gettran_id('存款')), str(self.card_id), str('存款'), float(input_money)-float(data[0][0]), str(ti[:-6]))
                        cursor.execute(sql)
                        tk.messagebox.showinfo(
                            '提示', '您已经成功归还透支的'+str(data[0][0])+'元\n'+'您存入'+str(float(input_money)-float(data[0][0]))+'元')
                    else:
                        sql = "update card set amount_credit='%f' where card_id='%s'" % (
                            float(data[0][0])-float(input_money), str(self.card_id))
                        cursor.execute(sql)
                        sql = "insert into transaction values('%s','%s','%s','%f','%s')" % (
                            str(ti)+str(self.gettran_id('归还透支')), str(self.card_id), str('归还透支'), float(input_money), str(ti[:-6]))
                        cursor.execute(sql)
                        tk.messagebox.showinfo(
                            '提示', '您已经成功归还透支的'+str(input_money)+'元')
                    db.commit()
                    input_m.set("")
                    return

                sql = "update card set money=money+'%f' where card_id='%s'" % (
                    float(input_money), str(self.card_id))
                cursor.execute(sql)
                sql = "insert into transaction values('%s','%s','%s','%f','%s')" % (
                    str(ti)+str(self.gettran_id('存款')), str(self.card_id), str('存款'), float(input_money), str(ti[:-6]))
                cursor.execute(sql)
                db.commit()
                sql = "select money from card where card_id='%s'" % (
                    str(self.card_id))
                cursor.execute(sql)
                data = cursor.fetchall()
                tk.messagebox.showinfo(
                    '提示', '您已经成功存入'+str(input_money)+'元\n'+'当前您账上余额为'+str(data[0][0])+'元')
                input_m.set("")

    def hit_save_money(self):
        if self.user_login() == False:
            return False
        son_win = tk.Toplevel()
        son_win.geometry('300x200')
        son_win.title('存款')
        son_win.resizable(False, False)
        son_win.protocol("WM_DELETE_WINDOW",
                         lambda: self.son_win_closing(self.main_win, son_win))
        tk.Label(son_win, text='请输入存款金额（输入金额需大于0元）：').pack()
        input_money = tk.StringVar()
        tk.Entry(son_win, textvariable=input_money).pack()
        tk.Button(son_win, text='确定',
                  command=lambda: self.save_money_to_db(input_money)).pack()

    def take_money_to_db(self, input_m):
        try:
            input_money = float(input_m.get())
        except:
            tk.messagebox.showerror('错误', '请输入正确的金额！')
        else:
            if input_money <= 0:
                tk.messagebox.showerror('错误', '请输入正确的金额！')
            else:
                db, cursor = self.connect_db()
                sql = "select money,credit_limit,amount_credit from card where card_id='%s'" % (
                    self.card_id)
                cursor.execute(sql)
                data = cursor.fetchall()
                print(data)
                ti=self.gettime()
                if float(data[0][0]) >= input_money:
                    sql = "update card set money=money-'%f' where card_id='%s'" % (
                        input_money, self.card_id)
                    cursor.execute(sql)
                    sql = "insert into transaction values('%s','%s','%s','%f','%s')" % (
                        str(ti)+str(self.gettran_id('取款')), str(self.card_id), str('取款'), float(input_money), str(ti[:-6]))
                    cursor.execute(sql)
                    db.commit()
                    tk.messagebox.showinfo(
                        '提示', '您已经成功取出'+str(input_money)+'元\n您现在的余额为'+str(float(data[0][0])-input_money)+'元！')
                elif float(data[0][1])-float(data[0][2])+float(data[0][0]) >= input_money:
                    sql = "update card set money='%f',amount_credit='%f' where card_id='%s'" % (
                        0, input_money-float(data[0][0]), self.card_id)
                    cursor.execute(sql)
                    if float(data[0][0]) > 0:
                        sql = "insert into transaction values('%s','%s','%s','%f','%s')" % (
                            str(ti)+str(self.gettran_id('取款')), str(self.card_id), str('取款'), float(input_money), str(ti[:-6]))
                        cursor.execute(sql)
                    sql = "insert into transaction values('%s','%s','%s','%f','%s')" % (
                        str(ti)+str(self.gettran_id('透支')), str(self.card_id), str('透支'), float(input_money), str(ti[:-6]))
                    cursor.execute(sql)
                    db.commit()
                    tk.messagebox.showinfo(
                        '提示', '您已经成功取出'+str(input_money)+'元\n您现在的余额为0元！现在已透支'+str(input_money-float(data[0][0]))+'元！')
                else:
                    tk.messagebox.showinfo('提示', '您账上的余额不足！')
                    return
        input_m.set("")

    def hit_take_money(self):
        if self.user_login() == False:
            return False
        son_win = tk.Toplevel()
        son_win.geometry('300x200')
        son_win.title('取款')
        son_win.resizable(False, False)
        son_win.protocol("WM_DELETE_WINDOW",
                         lambda: self.son_win_closing(self.main_win, son_win))
        tk.Label(son_win, text='请输入取款金额（输入金额需大于0元）：').pack()
        input_money = tk.StringVar()
        tk.Entry(son_win, textvariable=input_money).pack()
        tk.Button(son_win, text='确定', command=lambda: self.take_money_to_db(
            input_money)).pack()

    def loan_to_db(self,input_m,duration):
        dic_interest={'1年':4.35,'2年':4.55,'3年':4.75,'4年':4.90,'5年':5.05}
        try:
            input_money = float(input_m.get())
        except:
            tk.messagebox.showerror('错误', '请输入正确的金额！')
        else:
            if input_money <= 0:
                tk.messagebox.showerror('错误', '请输入正确的金额！')
            else:
                db, cursor = self.connect_db()
                sql="select * from loan where card_id='%s'"%(self.card_id)
                cursor.execute(sql)
                data = cursor.fetchall()
                if len(data)!=0:
                    tk.messagebox.showerror('提示', '您已经有贷款记录，请还款之后在进行贷款！')
                    return
                sql = "select loan_limit from post where post_id=(select position_id from person where person_id=(select person_id from card where card_id='%s'))" % (
                    self.card_id)
                cursor.execute(sql)
                data = cursor.fetchall()
                print(data)
                ti=self.gettime()
                if float(data[0][0]) >= input_money:
                    sql = "insert into loan values('%s','%s','%f','%s','%s','%f')" % (
                        str(ti), str(self.card_id),float(input_money),str(ti[:-6]),str(duration[0]),float(dic_interest[duration]))
                    cursor.execute(sql)
                    sql = "insert into transaction values('%s','%s','%s','%f','%s')" % (
                        str(ti), str(self.card_id), str('贷款'), float(input_money), str(ti[:-6]))
                    cursor.execute(sql)
                    db.commit()
                    tk.messagebox.showinfo(
                        '提示', '您已经成功贷款'+str(input_money)+'元')
                else:
                    tk.messagebox.showinfo('提示', '您的最大贷款额度为'+str(data[0][0])+'！')
                    return
        input_m.set("")

    def hit_loan(self):
        if self.user_login() == False:
            return False
        son_win = tk.Toplevel()
        son_win.title('贷款')
        son_win.geometry('300x200')
        son_win.resizable(False, False)
        son_win.protocol("WM_DELETE_WINDOW",
                         lambda: self.son_win_closing(self.main_win, son_win))
        tk.Label(son_win, text='请输入贷款金额（输入金额需大于0元）：').pack()
        input_money = tk.StringVar()
        tk.Entry(son_win, textvariable=input_money).pack()
        tk.Label(son_win, text='请选择贷款时长：').pack()
        duration=tk.StringVar()
        ttk.Combobox(son_win,values=('1年','2年','3年','4年','5年'),state='readonly',textvariable=duration).pack()
        tk.Button(son_win, text='确定', command=lambda: self.loan_to_db(
            input_money,duration.get())).pack()

    def transfer_money_to_db(self,input_id,input_m):
        print(len(input_id))
        print(input_id)
        try:
            float(input_id)
        except:
            tk.messagebox.showerror('错误', '请输入正确的卡号！')
            return
        else:
            if len(input_id)!=19:
                tk.messagebox.showerror('错误', '请输入正确的卡号！')
                return
        try:
            input_money = float(input_m)
        except:
            tk.messagebox.showerror('错误', '请输入正确的金额！')
        else:
            if input_money <= 0:
                tk.messagebox.showerror('错误', '请输入正确的金额！')
            else:
                db, cursor = self.connect_db()
                sql="select * from card where card_id='%s'"%(str(input_id))
                cursor.execute(sql)
                data1 = cursor.fetchall()
                if len(data1)==0:
                    tk.messagebox.showerror('提示', '您输入的卡号不存在!')
                    return
                sql = "select money,branch_id from card where card_id='%s'" % (
                    self.card_id)
                cursor.execute(sql)
                data = cursor.fetchall()
                print(data)
                ti=self.gettime()
                fee=0.001*input_money
                if fee<1:
                    fee=1
                if fee>50:
                    fee=50
                print(fee)
                if data[0][1]==data1[0][1]:
                    fee=0
                if float(data[0][0]) >= input_money+fee:
                    sql = "insert into transaction values('%s','%s','%s','%f','%s')" % (
                        str(ti)+str(self.gettran_id('转账')), str(self.card_id), str('转账'), float(input_money), str(ti[:-6]))
                    cursor.execute(sql)
                    if fee!=0:
                        sql = "insert into transaction values('%s','%s','%s','%f','%s')" % (
                            str(ti)+str(self.gettran_id('转账手续费')), str(self.card_id), str('转账手续费'), float(fee), str(ti[:-6]))
                        cursor.execute(sql)
                    sql = "insert into transaction values('%s','%s','%s','%f','%s')" % (
                        str(ti)+str(self.gettran_id('收入')), str(input_id), str('收入'), float(input_money), str(ti[:-6]))
                    cursor.execute(sql)
                    sql="update card set money=money-'%f' where card_id='%s'"%(input_money+fee,self.card_id)
                    cursor.execute(sql)
                    sql="update card set money=money+'%f' where card_id='%s'"%(input_money,input_id)
                    cursor.execute(sql)
                    db.commit()
                    tk.messagebox.showinfo(
                        '提示', '您已经成功向'+str(input_id)+'转账'+str(input_money)+'元')
                else:
                    tk.messagebox.showinfo('提示', '您的余额不足！')
                    return

    def hit_transfer_money(self):
        if self.user_login() == False:
            return False
        son_win = tk.Toplevel()
        son_win.title('转账')
        son_win.resizable(False, False)
        son_win.geometry('300x200')
        son_win.protocol("WM_DELETE_WINDOW",
                         lambda: self.son_win_closing(self.main_win, son_win))
        tk.Label(son_win,text='提示：跨行或异地转账需要收取 %1 的手续费').pack()
        tk.Label(son_win,text='请输入转入的银行卡：').pack()
        input_card_id=tk.StringVar()
        tk.Entry(son_win, textvariable=input_card_id).pack()
        tk.Label(son_win, text='请输入转入的金额（输入金额需大于0元）：').pack()
        input_money = tk.StringVar()
        tk.Entry(son_win, textvariable=input_money).pack()
        tk.Button(son_win, text='确定', command=lambda: self.transfer_money_to_db(input_card_id.get(),input_money.get())).pack()

    def repay_to_db(self,repay):
        db,cursor=self.connect_db()
        sql="delete from loan where card_id='%s'"%(self.card_id)
        cursor.execute(sql)
        ti=self.gettime()
        sql = "insert into transaction values('%s','%s','%s','%f','%s')" % (
            str(ti)+str(self.gettran_id('还贷')), str(self.card_id), str('还贷'), float(repay), str(ti[:-6]))
        cursor.execute(sql)
        db.commit()
        tk.messagebox.showinfo('提示','还款成功！')

    def hit_repayment(self):
        if self.user_login() == False:
            return False
        son_win = tk.Toplevel()
        son_win.title('还贷')
        son_win.resizable(False, False)
        son_win.geometry('300x200')
        son_win.protocol("WM_DELETE_WINDOW",
                         lambda: self.son_win_closing(self.main_win, son_win))
        text_repay=tk.StringVar()
        tk.Label(son_win,textvariable=text_repay).pack()
        db,cursor=self.connect_db()
        sql="select money,duration,interest from loan where card_id='%s'"%(self.card_id)
        cursor.execute(sql)
        cursor.close()
        db.close()
        data=cursor.fetchall()
        repay=0.0
        if len(data)==0:
            text_repay.set('您没有贷款记录！')
        else:
            d=str(data[0][1][0])
            print(d)
            repay=float(data[0][0])+float(d)*float(data[0][2])*float(data[0][0])/100.0
            text_repay.set('您贷款'+str(data[0][0])+'元\n需还款'+str(repay)+'元')
        tk.Button(son_win, text='确定', command=lambda:{self.repay_to_db(repay),son_win.destroy()}).pack()
        son_win.wait_window()

    def hit_query_deposit(self):
        if self.user_login() == False:
            return False
        son_win = tk.Toplevel()
        son_win.title('查询余额/贷款')
        son_win.geometry('300x200')
        son_win.resizable(False, False)
        son_win.protocol("WM_DELETE_WINDOW",
                         lambda: self.son_win_closing(self.main_win, son_win))
        db,cursor=self.connect_db()
        sql="select money from card where card_id='%s'"%(self.card_id)
        cursor.execute(sql)
        data1=cursor.fetchall()
        sql="select money from loan where card_id='%s'"%(self.card_id)
        cursor.execute(sql)
        data2=cursor.fetchall()
        dic={'贷款':'0','余额':'0'}
        dic['余额']='您的余额为：'+str(data1[0][0])
        if len(data2)==0:
            dic['贷款']='目前没有贷款'
        else:
            dic['贷款']='您贷款的金额为：'+str(data2[0][0])
        text_var=tk.StringVar()
        text_var.set("")
        tk.Label(son_win,text='请选择:').pack()
        com_var=tk.StringVar()
        ttk.Combobox(son_win,values=('余额','贷款'),textvariable=com_var,state='readonly').pack()
        tk.Button(son_win,text='确定',command=lambda:{text_var.set(dic[com_var.get()])}).pack()
        tk.Label(son_win,textvariable=text_var).pack()
        son_win.wait_window()

    def create_main_window(self):
        frame_top = tk.Frame(self.main_win)
        tk.Button(frame_top, text='存款',
                  font=self.button_font, command=self.hit_save_money).grid(row=0, padx=20, pady=10)
        tk.Button(frame_top, text='取款', font=self.button_font,
                  command=self.hit_take_money).grid(row=1, padx=20, pady=10)
        tk.Button(frame_top, text='转账', font=self.button_font,
                  command=self.hit_transfer_money).grid(row=2, padx=20, pady=10)
        tk.Button(frame_top, text='贷款', font=self.button_font,
                  command=self.hit_loan).grid(row=0, column=1)
        tk.Button(frame_top, text='还贷', font=self.button_font,
                  command=self.hit_repayment).grid(row=1, column=1)
        tk.Button(frame_top, text='查询存/贷款', font=self.button_font,
                  command=self.hit_query_deposit).grid(row=2, column=1)
        self.main_win.update()
        frame_top.pack(expand=tk.YES)
        admin = tk.Label(self.main_win, text='管理员入口', fg='blue',
                         font=tkfont.Font(size=10, underline=1))
        admin.bind("<Button-1>", self.admin_login)
        admin.pack(expand=tk.YES)
        #self.main_win.bind("<Configure>",self.adopter_handler(self.resize,frame=frame_top))
        self.main_win.mainloop()

    def resize(self, event, frame):
        w_width = self.main_win.winfo_width()
        w_height = self.main_win.winfo_height()
        print(w_width, w_height)

    def save_account_to_db(self, fa_win, vo, vn, vi, vp, cc, cp, vpsw1, vpsw2):
        try:
            if len(str(vpsw1.get())) == 6 and int(vpsw1.get()) >= 0:
                if vpsw1.get() != vpsw2.get():
                    tk.messagebox.showerror('提示', '两次密码不匹配，请重新输入！')
                    return
                try:
                    db,cursor=self.connect_db()
                    dic = {'湖北长城卡': 65531, '北京长城卡': 65532, '上海长城卡': 65533,
                           '湖北龙卡': 65534, '北京龙卡': 65535, '上海龙卡': 65536}
                    dicp = {'游民': 0, '职工': 1, '项目经理': 2, '总经理': 3, '董事长': 4}
                    card_id=self.gettime()
                    credit=1000
                    if int(vo.get())==0:
                        credit=0
                    sql = "insert into card values('%s','%s','%s','%s','%s','%s','%s','%s')" %\
                        (str(card_id), str(dic[cc.get()]), str(vi.get()), str(
                            vo.get()), str(0), str(vpsw1.get()), str(credit), str(0))
                    cursor.execute(sql)
                    print(str(card_id), str(dic[cc.get()]), str(vi.get()), str(
                        vo.get()), str(0), str(vpsw1.get()), str(credit), str(0))
                    sql = "select * from person where person_id='%s'" % (
                        str(vi.get()))
                    cursor.execute(sql)
                    data = cursor.fetchall()
                    if len(data) == 0:
                        sql = "insert into person values('%s','%s','%s','%s')" %\
                            (str(vi.get()), str(vn.get()), str(
                                vp.get()), str(dicp[cp.get()]))
                        cursor.execute(sql)
                    print(str(vi.get()), str(vn.get()), str(
                        vp.get()), str(dicp[cp.get()]))
                    db.commit()
                except:
                    tk.messagebox.showerror('提示', '数据库写入失败！')
                else:
                    tk.messagebox.showinfo(
                        '提示', '开户成功，卡号位'+str(card_id)+'！\n请向账户中充值至少10元')
                    fa_win.destroy()
            else:
                tk.messagebox.showerror('提示', '请输入6位的数字密码！')
        except:
            tk.messagebox.showerror('提示', '请输入6位的数字密码！')

    def input_password(self, vo, vn, vi, vp, cc, cp):
        if cc.get() == "":
            tk.messagebox.showinfo('提示', '请选择卡的类型！')
            return
        if vn.get() == "":
            tk.messagebox.showinfo('提示', '请输入名字！')
            return
        if vi.get() == "":
            tk.messagebox.showinfo('提示', '请输入身份证号！')
            return
        elif len(vi.get()) == 18:
            try:
                int(vi.get()[:17])
                if vi.get()[17] != 'X':
                    int(vi.get()[17])
            except:
                tk.messagebox.showinfo('提示', '请确保身份证格式正确！')
                return
        else:
            tk.messagebox.showinfo('提示', '请确保身份证号是18位！')
            return
        if vp.get() == "":
            tk.messagebox.showinfo('提示', '请输入手机号！')
            return
        elif len(vp.get()) == 11:
            try:
                int(vp.get())
            except:
                tk.messagebox.showinfo('提示', '请确保手机号码格式正确！')
                return
        else:
            tk.messagebox.showinfo('提示', '请确保手机号码是11位！')
            return
        if cp.get() == "":
            tk.messagebox.showinfo('提示', '请选择职业！')
            return
        win = tk.Toplevel()
        var_password1 = tk.StringVar()
        var_password2 = tk.StringVar()
        tk.Label(win, text='输入密码：').pack()
        tk.Entry(win, textvariable=var_password1, show='*').pack()
        tk.Label(win, text='再次输入密码：').pack()
        tk.Entry(win, textvariable=var_password2, show='*').pack()
        tk.Button(win, text='确定', command=lambda: self.save_account_to_db(fa_win=win, vpsw1=var_password1,
                                                                          vpsw2=var_password2, vo=vo, vn=vn, vi=vi, vp=vp, cc=cc, cp=cp)).pack()
        win.wait_window()

    def open_account(self, fa_win):
        fa_win.withdraw()
        son_win = tk.Toplevel()
        son_win.title('开户')
        son_win.protocol("WM_DELETE_WINDOW",
                         lambda: self.admin_son_win_closing(fa_win, son_win))
        son_win.geometry('250x350')
        son_win.resizable(False, False)
        var_overdraft = tk.IntVar()
        var_name = tk.StringVar()
        var_id = tk.StringVar()
        var_phone = tk.StringVar()
        var_post = tk.StringVar()
        tk.Label(son_win, text='选卡:').pack()
        com_card = ttk.Combobox(son_win)
        com_card['values'] = ['湖北长城卡', '北京长城卡', '上海长城卡',
                              '湖北龙卡', '北京龙卡', '上海龙卡']
        com_card.pack()
        tk.Label(son_win, text='是否需要透支功能:').pack()
        tk.Radiobutton(son_win, text='否', variable=var_overdraft,
                       value=0, command=lambda: var_overdraft.set(0)).pack()
        tk.Radiobutton(son_win, text='是', variable=var_overdraft,
                       value=1, command=lambda: var_overdraft.set(1)).pack()
        var_overdraft.set(0)
        tk.Label(son_win, text='姓名:').pack()
        tk.Entry(son_win, textvariable=var_name).pack()
        tk.Label(son_win, text='身份证号:').pack()
        tk.Entry(son_win, textvariable=var_id).pack()
        tk.Label(son_win, text='电话:').pack()
        tk.Entry(son_win, textvariable=var_phone).pack()
        tk.Label(son_win, text='职业:').pack()
        com_post = ttk.Combobox(son_win)
        com_post['values'] = ['游民', '职工', '项目经理', '总经理', '董事长']
        com_post.pack()
        tk.Button(son_win, text='确定', command=lambda: self.input_password(vo=var_overdraft,
                                                                          vn=var_name, vi=var_id, vp=var_phone, cc=com_card, cp=com_post)).pack()
        son_win.wait_window()
        #fa_win.deiconify()

    def close_accout_to_db(self, fa_win, var_card_id, var_id, var_card_password):
        if True:
            #if len(str(var_card_id)) == 19 and len(str(var_id)) == 18 and len(str(var_card_password)) == 6:
            try:
                db,cursor=self.connect_db()
                sql = "select person_id,password from card where card_id='%s'" % (
                    str(var_card_id))
                cursor.execute(sql)
                ret_data = cursor.fetchall()
                if len(ret_data) == 0:
                    tk.messagebox.showinfo('提示', '卡号不存在')
                    return
                else:
                    if str(ret_data[0][0]) != str(var_id):
                        tk.messagebox.showerror('提示', '身份证号错误！')
                        return
                    if str(ret_data[0][1]) != str(var_card_password):
                        tk.messagebox.showerror('提示', '密码错误！')
                        return
                    print(var_card_id, var_id, var_card_password)
                    sql = "select money from card where card_id='%s'" % (
                        str(var_card_id))
                    cursor.execute(sql)
                    data=cursor.fetchall()
                    tk.messagebox.showerror('提示', '账户还有余额'+str(data[0][0])+'元，已取出')
                    sql = "delete from card where card_id='%s'" % (
                        str(var_card_id))
                    cursor.execute(sql)
                    db.commit()
            except:
                tk.messagebox.showinfo('提示', '操作失败！')
            else:
                tk.messagebox.showinfo('提示', str(var_card_id)+'已注销！')
                fa_win.destroy()
        else:
            tk.messagebox.showerror('提示', '卡号、身份证号或者密码输入错误！')
    def close_account(self, fa_win):
        fa_win.withdraw()
        son_win = tk.Toplevel()
        son_win.title('销户')
        son_win.resizable(False, False)
        son_win.protocol("WM_DELETE_WINDOW",
                         lambda: self.admin_son_win_closing(fa_win, son_win))
        var_card_id = tk.StringVar()
        var_id = tk.StringVar()
        var_card_password = tk.StringVar()
        tk.Label(son_win, text='卡号:').pack()
        tk.Entry(son_win, textvariable=var_card_id).pack()
        tk.Label(son_win, text='身份证号:').pack()
        tk.Entry(son_win, textvariable=var_id).pack()
        tk.Label(son_win, text='密码:').pack()
        tk.Entry(son_win, textvariable=var_card_password).pack()
        tk.Button(son_win, text='确定', command=lambda: self.close_accout_to_db(fa_win=son_win, var_card_id=var_card_id.get().replace('\n', '').replace('\r', '').replace(
            ' ', ''), var_id=var_id.get().replace('\n', '').replace('\r', '').replace(' ', ''), var_card_password=var_card_password.get().replace('\n', '').replace('\r', '').replace(' ', ''))).pack()
        son_win.wait_window()
        fa_win.deiconify()

    def admin_search_time_from_db(self, date, card_id, search_type,ml):
        if len(date) == 8 and len(card_id) == 19:
            try:
                float(date)
                float(card_id)
            except:
                tk.messagebox.showerror('提示', '日期或者卡号格式错误！')
                return
            else:
                x=ml.get_children()
                for i in x:
                    ml.delete(i)
                if search_type=="":
                    sql = "select * from transaction where card_id='%s' and date='%s'" % (
                        str(card_id), str(date), str(search_type))
                else:
                    sql="select * from transaction where card_id='%s' and trans_date='%s' and type='%s'"%(str(card_id),str(date),str(search_type))
                db,cursor=self.connect_db()
                cursor.execute(sql)
                data=cursor.fetchall()
                sql="select person_name from person where person_id=(select person_id from card where card_id='%s')"%(str(card_id))
                cursor.execute(sql)
                pname=cursor.fetchall()
                s=""
                for i in range(len(data)):
                    ml.insert("",tk.END,values=(str(i),str(pname[0][0]),str(data[i][2]),str(data[i][3])))
                    #ml.insert(tk.END,str(i),str(data[i][2]),str(data[i][3]))
                    s=str(i)+'\t   \t'+str(data[i][2])+'\t   \t'+str(data[i][3])+'\t\n'
        else:
            tk.messagebox.showerror('提示', '日期或者卡号格式错误！')

    def admin_search_name_from_db(self, name, search_type,ml):
        x=ml.get_children()
        for i in x:
            ml.delete(i)
        if search_type=="":
            sql = "select * from transaction where card_id in (select card_id from card where person_id in (select person_id from person where person_name like '%s'))" % (
                str('%'+name+'%'))
            sql="select * from person natural join card natural join transaction where person_name like '%s'"%(str('%'+name+'%'))
        else:
            sql = "select * from transaction where type='%s' and card_id in (select card_id from card where person_id in (select person_id from person where person_name like '%s'))" % (str(search_type),str('%'+name+'%'))
        db,cursor=self.connect_db()
        cursor.execute(sql)
        data=cursor.fetchall()
        print(data)
        cursor.execute(sql)
        pname=cursor.fetchall()
        s=""
        for i in range(len(data)):
            ml.insert("",tk.END,values=(str(i),str(pname[0][0]),str(data[i][2]),str(data[i][3])))
            #ml.insert(tk.END,str(i),str(data[i][2]),str(data[i][3]))
            s=str(i)+'\t   \t'+str(data[i][2])+'\t   \t'+str(data[i][3])+'\t\n'

    def admin_search(self, fa_win):
        fa_win.withdraw()
        son_win = tk.Toplevel()
        son_win.title('查询')
        son_win.resizable(False, False)
        var_com = tk.StringVar()
        var_date = tk.StringVar()
        var_entry1 = tk.StringVar()
        var_entry2 = tk.StringVar()
        var_entry3 = tk.StringVar()
        type_com = tk.StringVar()
        radio = tk.IntVar()
        text_var=tk.StringVar()
        frame = tk.Frame(son_win)
        frame1 = tk.Frame(frame)
        frame2 = tk.Frame(frame)
        tree=ttk.Treeview(son_win,columns=['1','2','3','4'],show='headings')
        tree.column('1',width=100)
        tree.column('2',width=100)
        tree.column('3',width=100)
        tree.column('4',width=100)
        tree.heading('1',text='序号')
        tree.heading('2',text='姓名')
        tree.heading('3',text='类型')
        tree.heading('4',text='金额')
        tk.Label(frame1, text='输入时间：').pack()
        tk.Entry(frame1, textvariable=var_entry1).pack()
        tk.Label(frame1, text='输入卡号：').pack()
        tk.Entry(frame1, textvariable=var_entry2).pack()
        tk.Label(frame2, text='输入名字：').pack()
        tk.Entry(frame2, textvariable=var_entry3).pack()
        tk.Button(frame1, text='确定', command=lambda:self.admin_search_time_from_db(
            search_type=type_com.get().replace('\r', '').replace('\n', '').replace(' ', ''),
            date=var_entry1.get().replace('\r', '').replace('\n', '').replace(' ', ''),
            card_id=var_entry2.get().replace('\r', '').replace('\n', '').replace(' ', ''),
            ml=tree)).pack()
        tk.Button(frame2, text='确定', command=lambda:self.admin_search_name_from_db(
            search_type=type_com.get().replace('\r', '').replace('\n', '').replace(' ', ''),
            name=var_entry3.get().replace('\r', '').replace('\n', '').replace(' ', ''),
            ml=tree)).pack()
        tk.Radiobutton(son_win, variable=radio, value=0, text='按时间查询', command=lambda: {
            frame2.pack_forget(), frame1.pack(), type_com.set(''),text_var.set('')}).pack()
        tk.Radiobutton(son_win, variable=radio, value=1, text='按名字查询', command=lambda: {
            frame1.pack_forget(), frame2.pack(), type_com.set(''),text_var.set('')}).pack()
        radio.set(0)
        tk.Label(son_win, text='选择查询类型：').pack()
        ttk.Combobox(son_win, value=('存款', '取款', '贷款', '转账'),
                     textvariable=type_com).pack()
        frame1.pack()
        frame.pack()
        tk.Label(son_win,text='查询结果：').pack()
        tree.pack()
        son_win.wait_window()
        fa_win.deiconify()

    def admin_window(self):
        admin_win = tk.Toplevel()
        admin_win.title('管理员界面')
        admin_win.geometry('400x300')
        admin_win.protocol("WM_DELETE_WINDOW",
                           lambda: self.son_win_closing(self.main_win, admin_win))
        tk.Button(admin_win, text='开户', font=self.button_font,
                  command=lambda: self.open_account(admin_win)).pack()
        tk.Button(admin_win, text='销户', font=self.button_font,
                  command=lambda: self.close_account(admin_win)).pack()
        tk.Button(admin_win, text='查询', font=self.button_font,
                  command=lambda: self.admin_search(admin_win)).pack()

    def connect_db(self):
        db = pymysql.connect(
            host='localhost', user='xue', password='123456', database='bank')
        cursor = db.cursor()
        return db, cursor


if __name__ == "__main__":
    mywindow = app()