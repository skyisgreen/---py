import re
import threading
import time

import requests


class GrabClass:
    def __init__(self, data):
        self.number = 0
        self.html = ""
        self.url = "http://10.10.240." + \
            data[0] + "/xsxjs.aspx?xkkh=" + data[2] + "&xh=" + data[1]
        self.data = {
            "__EVENTTARGET": "Button1",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": data[3],
            "xkkh": data[4],
            "RadioButtonList1": "0"
        }
        self.head = {"Cookie": data[5]}

    @property
    def post(self):
        try:
            session = requests.session()
            response = session.post(
                self.url, data=self.data, headers=self.head, timeout=5)
        except WindowsError:
            return "服务器超时！"
        else:
            try:
                self.html = response.text
                decide = re.search(r"alert\S+！", self.html).group()
            except AttributeError:
                return response.text
            else:
                decide = decide.replace("alert('", "")
                return decide

    @property
    def get_name(self):
        name = re.search(
            r'<span id="Label1">课程名称：\S+学分\S{2,5}\d', self.html).group()
        name = name.replace('<span id="Label1">', '\n')
        name = name.replace('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;', ' ')
        return name

    @property
    def over(self):
        self.number += 1
        alert = self.post
        if alert == "现在不是选课时间！":
            print(self.get_name + "            现在不是选课时间！ Ps：第" + str(
                self.number) + "次尝试")
            return False
        if alert == "保存成功！":
            print(self.get_name + "            保存成功！ Ps：第" + str(
                self.number) + "次尝试")
            return True
        if alert == "您的教材改选成功！":
            print(self.get_name + "            您的教材改选成功！ Ps：第" + str(
                self.number) + "次尝试")
            return True
        if alert == "上课时间冲突！":
            print(self.get_name + "            上课时间冲突！ Ps：第" + str(
                self.number) + "次尝试")
            return True
        print(self.get_name + "            重试中！ Ps：第" + str(
            self.number) + "次尝试" + "\n错误: " + alert)
        return False

    def start(self):
        while True:
            if self.over:
                return
            time.sleep(0.1)


class MyThread(threading.Thread):
    def __init__(self, data):
        threading.Thread.__init__(self)
        self.data = data

    def run(self):
        take_lessons = GrabClass(self.data)
        take_lessons.start()


def get_name(input_data, server, student_id):
    while True:
        data = [server,
                student_id,
                input("请输入url_xkkh："),
                input("请输入__VIEWSTATE："),
                input("请输入xkkh："),
                input("请输入cookie：")]
        text = GrabClass(data)
        alert = text.post
        if alert == "现在不是选课时间！":
            print(text.get_name)
            input_data.append(data)
        else:
            print(alert)
        button = input("是否继续添加课程：（y/n）\n")
        while True:
            if button == "y":
                break
            if button == "n":
                return
            button = input("输入错误，重新输入（y/n）：\n")


if __name__ == "__main__":
    set_data = []
    for i in range(int(input("请输入本次抢课对应服务器数量："))):
        get_name(set_data, input("请输入服务器号: "), input("请输入学号: "))

    thread = list(range(len(set_data)))

    for i in range(len(set_data)):
        thread[i] = MyThread(set_data[i])
        thread[i].start()

    for i in range(len(set_data)):
        thread[i].join()

    print('\n\n----------------------------------------------')
    print('以上，全部课程请求完毕')