#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import time
import tkinter
import traceback
from tkinter import *
from tkinter import ttk
from classqk import User
from threading import Thread
from datetime import datetime
from tkinter import messagebox


# noinspection PyAttributeOutsideInit,PyTypeChecker,PyBroadException
class Tkinter:
    red = "#FFC2C2"
    orange = "#FFE2A6"
    yellow = "#FFFBBB"
    green = "#C4FFC2"
    blue = "#C0E3FF"
    purple = "#D4DAFF"
    pink = "#FFE1F4"
    User = None
    monitor_status = False
    course_status = False

    def __init__(self):
        """
        这里为了可以重启程序而不影响数据丢失，采用了函数重启的办法
        """
        self.create()

    def create(self, tip=True):
        """
        创建tk窗口
        """
        self.root = Tk()
        self.root.title('科师抢课程序')  # 标题
        # 获取窗口宽度
        window_height = self.root.winfo_screenheight()
        window_width = self.root.winfo_screenwidth()

        # 最小宽度
        width, height = list([720, 650])
        self.root.minsize(width, height)

        # 设置窗口大小
        self.root.geometry('%dx%d+%d+%d' % (width, height, (window_width - width) / 2, (window_height - height) / 2))
        self.root.attributes("-alpha", 1)  # 窗口透明度

        self.create_place(tip)  # 创建窗口
        self.root.mainloop()  # 使窗口等待

    def create_place(self, tip):
        """
        创建各种空间
        """
        # 登录框
        self.left_place_func()
        # 创建信息空间
        self.info_place_func()
        # 日志配置
        self.log_place_func()

        if tip:
            # 首次打开软件时的说明
            message = f"首次使用时，请您务必阅读以下条款：\n\n" \
                      f"①本软件为免费维护，请不要以任何付费形式出售本软件！\n" \
                      f"②本软件作者@simple，作品已在GitHub开源，地址为：https://github.com/icyou66/hevttc。如果你有任何建议或bug，请提交issue，欢迎大家水贴\n\n" \
                      f"使用说明：\n" \
                      f"①监控功能说明：监控功能指通过不断刷新课程列表，搜索预先设定好的课程，如果搜索成功会自动选入。属于捡漏课程\n" \
                      f"②功能相关：抢课和退课的操作步骤一样：选中课程后按下鼠标右键可以进行选/退课\n" \
                      f"③请严格按照日志提示进行操作！日志提示任何错误时，你可以点击按钮重试\n" \
                      f"④如果想切换账号请先退出登录后再进行登录！\n" \
                      f"⑤所有按钮请勿频繁点击！"
            messagebox.showinfo("说明", message)

    def pprint(self, msg, color=False):
        """
        向日志框中输出日志
        :param self:
        :param msg: 日志内容
        :param color: 文本颜色（当前仅支持red|blue）
        """
        if not color:
            color = "blue"
        self.log_data.insert(END, f"[{datetime.now().strftime('%H:%M:%S')}]——" + msg + "\n", color)
        self.log_data.update()
        # if self.log_value == 1:
        self.log_data.see(END)

    def left_place_func(self):
        """
        窗口左侧空间
        包含登录框、课程详情框、课程信息框、已选课程框
        """
        # 创建最左边的空间
        self.left_place = Frame(self.root)
        self.left_place.pack(side="left", fill="y", expand=False, pady=5, ipadx=5, ipady=5)

        # 读取登录空间配置
        self.login_place_func()
        self.details_place_func()
        self.course_place_func()
        self.selected_place_func()

    def login_place_func(self):
        """
        登录拟态框
        """
        login_place = LabelFrame(self.left_place, text="用户登录")
        login_place.pack(ipady=5, ipadx=25)
        Label(login_place, text="信息：").grid(row=0, column=0, padx=(5, 0), pady=5)
        Label(login_place, text="账号：").grid(row=1, column=0, padx=(5, 0), pady=5)
        Label(login_place, text="密码：").grid(row=2, column=0, padx=(5, 0), pady=5)

        # 判断用户信息是否保存
        open(f"./info.json", "a+", encoding="utf-8-sig").close()
        with open(f"./info.json", "r+", encoding="utf-8-sig") as file:
            user_info = file.read()
        if user_info:
            user_info = json.loads(user_info)
            self.account_value = tkinter.StringVar(value=user_info['account'])
            self.password_value = tkinter.StringVar(value=user_info['password'])
        else:
            self.account_value = tkinter.StringVar()
            self.password_value = tkinter.StringVar()
        self.userinfo = tkinter.StringVar(value="登录后显示")
        Label(login_place, textvariable=self.userinfo, fg="blue").grid(row=0, column=1, columnspan=2)
        Entry(login_place, textvariable=self.account_value).grid(row=1, column=1, columnspan=2)
        Entry(login_place, textvariable=self.password_value).grid(row=2, column=1, columnspan=2)
        Button(login_place, text="退出登录", command=lambda: self.logout(), relief="groove",
               background=self.yellow).grid(row=0, column=3, ipadx=5, padx=10, pady=5)
        Button(login_place, text="点击登录", command=lambda: self.login_thread(), relief="groove",
               background=self.blue).grid(row=1, column=3, rowspan=2, ipadx=5, ipady=10, padx=10, pady=5)

    def details_place_func(self):
        """
        详细课程信息
        当点击课程列表，选中一个课程后，会触发该函数，从而获取该课程的详细信息并推送
        """
        details_place = LabelFrame(self.left_place, text="课程详细信息")
        details_place.pack(fill="x", ipadx=10, ipady=5, padx=5)

        self.details = tkinter.StringVar(value="点击课程后这里显示课程详细信息\n鼠标右键课程可以提交选课")
        Label(details_place, textvariable=self.details, fg="green").pack()

    def course_place_func(self):
        """
        课程列表配置
        这里加了右键菜单的绑定。用来选课
        竖向滚动条的添加是因为选的课程太多了
        """
        self.course_data_List = Listbox(self.left_place, selectmode="browse", bg="#F9F0FF", fg="blue")
        self.course_data_List.pack(expand=tkinter.YES, fill=tkinter.BOTH, side="top", padx=5, pady=5, ipadx=20, ipady=5)
        self.course_data_List.insert(0, f"Tips①：登录后这里显示课程列表")
        self.course_data_List.insert(1, f"Tips②：列表只读取部分课程")

        self.course_menu = Menu(self.root, tearoff=0)
        self.course_menu.add_command(label="就选它了！", command=lambda: self.run_thread(1))
        self.course_data_List.bind("<Button-3>", self.course_menu_func)
        self.course_data_List.bind("<<ListboxSelect>>", self.course_onclick_func)

        # 设置滚动条(y)
        roll_y = tkinter.Scrollbar(self.course_data_List)
        roll_y.pack(side="right", fill="y")
        self.course_data_List.config(yscrollcommand=roll_y.set)
        roll_y.config(command=self.course_data_List.yview)

    def course_menu_func(self, event):
        """
        选课窗口右键菜单传入事件
        :param event: 默认事件
        """
        selection = event.widget.curselection()
        if selection:
            item = event.widget.get(selection[0])
            if "Tips" not in item:
                self.course_menu.post(event.x_root, event.y_root)

    def course_onclick_func(self, event):
        """
        课程点击事件
        点击课程后将会获取到该课程的详细内容
        """
        selection = event.widget.curselection()
        if selection:
            item = event.widget.get(selection[0])
            if "Tips" not in item:
                msg = self.User.details(self.course_wx[selection[0]])
                self.details.set(msg)

    def selected_place_func(self):
        """
        已选课程列表配置
        数据是直接从课程列表中拿到的
        通过简单的判断得到课程是已选还是未选
        """
        self.selected_course_List = Listbox(self.left_place, selectmode="browse", bg="#F9F0FF", fg="blue", height=4)
        self.selected_course_List.pack(fill="x", side="top", padx=5, pady=5, ipadx=20, ipady=5)
        self.selected_course_List.insert(0, f"Tips①：这里显示已选课程")

        self.select_menu = Menu(self.root, tearoff=0)
        self.select_menu.add_command(label="退课", command=lambda: self.run_thread(2))
        self.selected_course_List.bind("<Button-3>", self.select_menu_func)
        self.selected_course_List.bind("<<ListboxSelect>>", self.select_onclick_func)

    def select_menu_func(self, event):
        """
        退课窗口右键菜单传入事件
        :param event: 默认事件
        """
        selection = event.widget.curselection()
        if selection:
            item = event.widget.get(selection[0])
            if "Tips" not in item:
                self.select_menu.post(event.x_root, event.y_root)

    def select_onclick_func(self, event):
        """
        课程点击事件
        点击课程后将会获取到该课程的详细内容
        """
        selection = event.widget.curselection()
        if selection:
            item = event.widget.get(selection[0])
            if "Tips" not in item:
                msg = self.User.details(self.course_yx[selection[0]])
                self.details.set(msg)

    def log_place_func(self):
        """
        日志文本框的配置
        这里配置了文本颜色：red|blue
        """
        self.log_place = Frame(self.root)
        self.log_place.pack(side="left", expand=tkinter.YES, fill=tkinter.BOTH,
                            ipadx=5, ipady=5, pady=5, padx=5)

        self.log_data = Text(self.log_place, font="微软雅黑 9", height=16, fg="blue", bg="#F4F3FF")
        self.log_data.pack(side="left", expand=tkinter.YES, fill=tkinter.BOTH,
                           ipadx=5, ipady=5, pady=5, padx=5)
        self.log_data.tag_config("blue", foreground="blue")
        self.log_data.tag_config("red", foreground="red")

        self.pprint("Tips:操作后这里显示日志内容")

    def info_place_func(self):
        """
        信息窗口的配置
        不过多赘述了
        """
        self.info_place = LabelFrame(self.root, text="信息配置")
        self.info_place.pack(side="top", padx=5, ipadx=5)

        # 左边
        info1 = Frame(self.info_place)
        info1.pack(side="left", pady=5, padx=(10, 0))

        # 左上
        info1_top = Frame(info1)
        info1_top.pack(side="top")

        self.select = tkinter.StringVar(value="公选课")
        self.select_label = Label(info1_top, text="课程获取方式：")
        self.select_label.grid(row=0, column=0, padx=(5, 0), pady=5, sticky="w")
        self.select_value = ttk.Combobox(info1_top, width=12, textvariable=self.select, state="readonly")
        self.select_value['values'] = ["公选课", "美育课"]
        self.select_value.grid(row=0, column=1, sticky="w")

        self.monitor_time = tkinter.DoubleVar(value=1)
        self.monitor_str = tkinter.StringVar()
        Label(info1_top, text="监控间隔时长：").grid(row=1, column=0, padx=(5, 0), pady=5)
        Entry(info1_top, textvariable=self.monitor_time, width=14).grid(row=1, column=1)
        Label(info1_top, text="待监控课程名：").grid(row=2, column=0, padx=(5, 0), pady=5)
        Entry(info1_top, textvariable=self.monitor_str, width=14).grid(row=2, column=1)

        # 左下
        info1_bot = Frame(info1)
        info1_bot.pack(side="top", ipadx=5, padx=5)
        Button(info1_bot, text="获取课程", command=lambda: self.course_thread(),
               relief="groove", background=self.orange).grid(row=2, column=0, ipadx=20, pady=5)
        self.monitor_button = Button(info1_bot, text="执行监控", command=lambda: self.run_thread(3),
                                     relief="groove", background=self.pink)
        self.monitor_button.grid(row=2, column=1, ipadx=20, pady=5, padx=(5, 0))

        # 右边
        info2 = Frame(self.info_place)
        info2.pack(side="left", anchor="n", padx=(0, 10))

        Button(info2, text="清空日志", command=lambda: self.empty(),
               relief="groove", background=self.purple).grid(row=0, column=0, ipadx=20, pady=5)
        Button(info2, text="修改密码", command=lambda: self.modify_window(),
               relief="groove", background=self.blue).grid(row=2, column=0, ipadx=20, pady=5)
        Button(info2, text="监控说明", command=lambda: self.monitor_explain(),
               relief="groove", background=self.green).grid(row=3, column=0, ipadx=20, pady=5)

    def save_info(self):
        """
        保存账号密码，将账号密码以json的格式存入到info.json文件中
        """
        self.account = self.account_value.get()
        self.password = self.password_value.get()
        if self.account and self.password:
            data = dict(account=self.account, password=self.password)
            data = json.dumps(data)
            open(f"./info.json", "a+", encoding="utf-8-sig").close()
            with open(f"./info.json", "r+", encoding="utf-8-sig") as file:
                file.write(data)

    def login_thread(self):
        """
        登录线程
        因为不开启线程会导致tk窗口阻塞
        这里为了方便便多开一个函数单独使用线程
        :return:
        """
        Thread(target=self.login_ajax).start()

    def login_ajax(self):
        """
        登录请求
        拿到登录后的session
        """
        self.pprint("登录中...")
        self.User = User(self.account_value.get().strip(), self.password_value.get().strip())
        result = self.User.login()
        if not result[0]:
            messagebox.showwarning("错误", result[1])
        else:
            self.save_info()
            self.pprint("登录成功！")
            self.pprint("已经将你的账号密码存入到info.json文件中，下次打开软件可直接读取到你的信息\n", "red")
            try:
                info = self.User.initial()  # 信息初始化
                self.userinfo.set(f"{info[0]}[{info[1]}]")
                self.course_list_func()  # 更新课程列表
            except Exception as e:
                self.pprint("出错了！\n", "red")
                self.pprint(str(e), "red")


    def logout(self):
        if not self.User:
            messagebox.showwarning("警告", "你还未登录！")
        else:
            self.User.logout()
            messagebox.showinfo("提示", "注销登录成功！点击确定重启程序！")
            self.root.destroy()
            self.create(False)

    def course_thread(self):
        """
        单独开一个获取课程的线程，这里是为了点击获取课程按钮不阻塞tk线程
        """
        Thread(target=self.course_list_func).start()

    def course_list_func(self):
        """
        更新课程列表，包括获取、分类、更新
        """
        if self.course_status:
            messagebox.showwarning("警告", "请勿重复点击！")
        else:
            try:
                self.pprint("正在获取课程列表...")
                self.course_status = True
                self.User.course(self.select.get())
                self.course_wx, self.course_yx = self.User.classify()
                self.update_course()
                self.course_status = False
                self.pprint("课程列表获取成功！\n")
            except Exception as e:
                self.end(str(e), color="red")

    def update_course(self):
        """
        更新课程列表
        未选课程和已选课程一起更新
        """
        self.course_data_List.delete(0, END)
        self.selected_course_List.delete(0, END)
        for course in self.course_wx:
            self.course_data_List.insert(END, f"{course['kcmc']}【{course['yxrl']}】")
        if self.course_yx:
            for course in self.course_yx:
                self.selected_course_List.insert(END, course['jxbmc'])
        else:
            self.selected_course_List.insert(END, "一门课程都没有选上！")

    def run_thread(self, types=1):
        """
        开启运行线程
        :param types: 1：提交选课 | 2：退课 | 3：监控课程
        """
        if types == 1:
            Thread(target=self.submit_course).start()
        elif types == 2:
            Thread(target=self.drop_course).start()
        elif types == 3:
            if self.monitor_status:
                self.pprint("\n监控任务即将关闭！", "red")
                self.monitor_button['text'] = "打开监控"
            else:
                self.pprint("\n监控课程任务开始执行！\n")
                self.monitor_button['text'] = "关闭监控"
            self.monitor_status = not self.monitor_status
            if self.monitor_status:
                Thread(target=self.monitor_course).start()

    def submit_course(self, course=False):
        """
        提交课程的操作，如果传入course，则不判断选中状态
        :param course: 课程信息
        :return:
        """
        if not course:
            if self.course_data_List.size() < 3:
                self.end("请先获取课程！", "red")
            item = self.course_data_List.curselection()
            if not item:
                self.end("你还未选择课程！", "red")
            course = self.course_wx[item[0]]
        self.pprint("正在提交选课请求，请稍等...")
        result = self.User.submit(course)
        if result['ret'] == 0:
            messagebox.showinfo("提示", "选课成功！")
            self.course_list_func()
        else:
            messagebox.showwarning("警告", result['msg'])

    def drop_course(self):
        """
        退课操作
        """
        item = self.selected_course_List.curselection()
        if not item:
            self.end("你还未选择课程！", "red")
        self.pprint("正在提交退课请求，请稍等...")
        course = self.course_yx[item[0]]
        result = self.User.drop(course)
        if result['ret'] == 0:
            messagebox.showinfo("提示", "退课成功！")
            self.course_list_func()
        else:
            messagebox.showwarning("警告", result['msg'])

    def monitor_course(self):
        """
        监控课程，从课程列表中判断是否含有要监控的课程
        """
        self.monitor_name = self.monitor_str.get().strip()
        if not self.monitor_name:
            self.end("请先填写要监控的课程！不要有错字！", "red")
        n = 0
        while self.monitor_status:
            n += 1
            self.monitor_name = self.monitor_str.get().strip()
            self.course_list_func()
            course = None
            for item in self.course_wx:
                if self.monitor_name in item['kcmc']:
                    capacity = item['yxrl']
                    cap = capacity.split("/")
                    if cap[0] != cap[1]:
                        course = item
                    break
            if course:
                self.pprint(f"已监控到课程：{course['kcmc']}", "red")
                self.submit_course(course)
                self.monitor_status = False
            else:
                self.pprint(f"第{n}次监控结果：未发现符合课程")
                try:
                    sleep = self.monitor_time.get()
                except:
                    sleep = 1
                    self.pprint("未设置延迟时间！已默认为你设置：1秒！", "red")
                time.sleep(sleep)
        self.pprint(f"监控线程已结束，本次一共监控了{n}次！")

    def end(self, msg, color=False):
        self.monitor_status = False
        self.course_status = False
        self.pprint(msg, color)
        raise SystemExit

    def empty(self):
        self.log_data.delete("1.0", END)

    @staticmethod
    def monitor_explain():
        message = f"监控功能指通过不断刷新课程列表，搜索预先设定好的课程，如果搜索成功会自动选入，属于捡漏课程。\n\n" \
                  f"关于间隔时间：间隔时间可以随意设置，但是不允许空着。开发测试时频繁请求未见异常情况，但是保险期间低延迟监控时请保持不离电脑\n\n" \
                  f"关于监控课程：监控课程可以是关键字，例如你想搜索毛泽东诗词与革命，你可以填：毛泽东 即可。如果课程中包含多个含有毛泽东的课程，默认选择第一个。\n\n" \
                  f"关于课程列表：如果你的课程获取方式为公选课，监控任务则为公选课的监控，如果你想监控美育课，需要你将课程获取方式改为美育课，一般情况下美育课很少需要监控。\n\n" \
                  f"希望你能通过本软件选到自己心仪的课程~"
        messagebox.showinfo("说明", message)


if __name__ == "__main__":
    Tkinter()
