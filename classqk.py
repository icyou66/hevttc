import re
import requests
import traceback
from bs4 import BeautifulSoup


# noinspection PyAttributeOutsideInit,PyTypeChecker,PyBroadException
class User:
    session = requests.session()
    course_list = []

    def __init__(self, account, password):
        self.account = account
        self.password = password
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "hevttc.jw.chaoxing.com",
            "Origin": "https://hevttc.jw.chaoxing.com",
            "Referer": "https://hevttc.jw.chaoxing.com/admin/login",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }

    def login(self):
        """
        登录线程
        :return (bool, msg): 是否成功，若失败返回失败原因
        """
        if not self.account or not self.password:
            return False, "账号密码不能为空！"

        url = 'https://hevttc.jw.chaoxing.com/admin/login'
        data = dict(username=self.account, password=self.password)
        result = self.session.post(url, data=data, headers=self.headers).text
        if "账号登录" in result:
            error = re.findall('var error = "(.*?)";', result)[0]
            return False, error
        return True, "登录成功"

    def logout(self):
        """
        退出登录
        """
        self.session.post("https://hevttc.jw.chaoxing.com/admin/logout", headers=self.headers)
        return True

    def initial(self):
        """
        取选课主页面的pcid,暂时不确定pcid是否为固定值。
        2023年8月10日的抢课pcid为571958c87a204848b1f95c82160dbc4b
        :return (name, number): 返回姓名和学号
        """
        self.headers['Referer'] = "https://hevttc.jw.chaoxing.com/admin"
        self.headers.pop("Content-Type")
        result = self.session.get("https://hevttc.jw.chaoxing.com/admin/xsd/xk", headers=self.headers)
        if "您的密码是初始密码，请修改密码" in result.text:
            raise Exception("您的密码是初始密码，请登录网站：\nhttps://hevttc.jw.chaoxing.com/ \n修改密码后再来操作！")
        soup = BeautifulSoup(result.text, "html.parser")
        self.pcid = soup.find('a', attrs={"data-toggle": "tab"})['id']
        self.pcid = self.pcid.replace("navItem_", "")
        number = soup.find("span", class_="admin_name").text
        name = soup.find("span", class_="arrowbt").text
        return name, number

    def course(self, select):
        """
        获取课程列表，此列表为全部课程的列表。包括已选和未选，已满课程排在最后面
        格式如下：
        [{
            'id': 'b1696422568a4bd89cbb3baf0d955ecb',
            'kkxxdm': '70426127840b44e18c43bb93650fdb25',
            'jxbmc': '健康教育课(公共选修课)-理论003',
            'kclb': '28',
            'kclx': '--',
            'kcid': 'AL991810',
            'sfyzjxb': '0',
            'fjxb': '-',
            'sfym': '0',
            'bz': '周三9-10节课',
            'kcxz': '公共选修课',
            'kcbh': 'AL991810',
            'kcmc': '健康教育课',
            'kcgs': '自然科学类',
            'xf': '1.0',
            'type': '理论',
            'jxms': '中文教学',
            'yxrl': '51/120',
            'teacher': '齐峻瑶',
            'sksjdd': '第3-5,7-11周 星期三 9-10节【1C108】;',
            'source': '2',
            'status': '0',
            'sfkxk': '1',
            'bjrs': '120',
            'sfct': '0',
            'ksxs': ''
        }]
        """
        data = dict(pcid=self.pcid)
        if select == "美育课":
            data['kcgs'] = "美育教育类"
        self.headers['Referer'] = "https://hevttc.jw.chaoxing.com/admin/xsd/xk"
        self.headers['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
        self.course_list = self.session.post("https://hevttc.jw.chaoxing.com/admin/xsd/xk/listjxb", data=data, headers=self.headers).json()
        if not self.course_list:
            raise Exception("疑似登录失效，请重新登录！")

    def classify(self):
        """
        将课程按已选和未选进行分开
        :return: (未选课程， 已选课程)
        """
        course_wx = []
        course_yx = []
        for course in self.course_list:
            if course.get("status") == "1":
                course_yx.append(course)
            else:
                course_wx.append((course))
        return course_wx, course_yx

    @staticmethod
    def details(course):
        """
        获取课程详细信息
        :param course: 当前课程信息
        :return: 课程详细信息
        """
        if course['teacher'] == "昌黎":
            msg = f"该课程为选修课\n【学分：{course['xf']}】| 【分类：{course['kcgs']}】"
        else:
            msg = f"【教师：{course['teacher']}】【学分：{course['xf']}】【分类：{course['kcgs']}】\n上课信息：{course['sksjdd']}"
        return msg

    def submit(self, course):
        """
        提交选课
        :param course: 要选的课程信息
        :return: 返回结果，如果选课成功，则返回：{ret: 0, msg: "操作成功"}
        """
        data = dict(jxbid=course['id'], pcid=self.pcid)
        self.headers['Referer'] = "https://hevttc.jw.chaoxing.com/admin/xsd/xk"
        self.headers['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
        return self.session.post("https://hevttc.jw.chaoxing.com/admin/xsd/xk/ggxxk/xk", data=data, headers=self.headers).json()

    def drop(self, course):
        """
        提交退课
        :param course: 要退选的课程信息
        :return: 返回结果，如果退课成功，则返回：{ret: 0, msg: "操作成功"}
        """
        data = dict(jxbid=course['id'], pcid=self.pcid)
        self.headers['Referer'] = "https://hevttc.jw.chaoxing.com/admin/xsd/xk"
        self.headers['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
        return self.session.post("https://hevttc.jw.chaoxing.com/admin/xsd/xk/ggxxk/tk", data=data, headers=self.headers).json()
