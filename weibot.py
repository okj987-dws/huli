import os
import pandas as pd
import asyncio
import aiohttp
import re
import time
import base64
import json
from execjs import compile
from datetime import date


class denglu():
    def __init__(self):
        self.url = [
            'https://huli.weibot.cn/auth/weibo?redirect=https://huli.weibot.cn/login-redirect',
            'https://login.sina.com.cn/sso/prelogin.php',
            "https://api.weibo.com/oauth2/authorize",
            'https://login.sina.com.cn/cgi/pin.php?'
        ]

    def header(self, a=None):
        if a == 0:
            header = {
                'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
                'accept':
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'upgrade-insecure-requests': '1'
            }
            return header
        elif a == 1:
            header = {
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Dest': 'script',
                'Accept-Encoding': 'gzip, deflate, br'
            }
            return header


# 获取时间戳
    def get_time(self):
        now_time = str(int(time.time() * 1000))
        # print('当前的时间戳：', now_time)
        return now_time

# 用户名加密
    def uese_64(self, log_name):
        b_user = log_name.encode('utf-8')
        user_64 = str(base64.b64encode(b_user), encoding="utf-8")  # 64加密
        return user_64

# 获取加密密码
    def get_sp(self, password, me):
        with open("wb.js", "r") as f:
            js_code = f.read()
        re = compile(js_code)
        res = re.call("getsp", password, me)
        return res

# 第一次登录获取URL
    async def first_log(self, session):
        print("开始第一次登录")
        async with session.get(self.url[0]) as response:
            first_url = str(response.url)
            return first_url

# 预登录获取密钥
    async def denglu_yu(self, session, username):
        print("预登录开始")
        parmas = {
            'entry': 'openapi',
            'callback': 'sinaSSOController.preloginCallBack',
            'su': self.uese_64(username),
            'rsakt': 'mod',
            'checkpin': '1',
            'client': 'ssologin.js(v1.4.18)',
            '_': self.get_time()
        }
        async with  session.get(self.url[1], headers=self.header(1), params=parmas) as response:
            miyao = await response.text()
            print('以获取到公钥等信息，正在提取数据')
            p1 = re.compile(r'[(](.*?)[)]', re.S)  # 正则表达式
            p2 = re.findall(p1, miyao)  # 正则提取后字符转列表
            p3 = ''.join(p2)  # 列表转字符
            me = json.loads(p3)  # me是公钥字典
            print('公钥等信息已转为字典形式')
            return me

# 正式登录
    async def fist_denglu(self, session, username, password, me):
        print("开始带密码登录")
        deng_url = "https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)&_=" + self.get_time(
        ) + "&openapilogin=qrcode"
        data = {
            #'door': '',  #self.yz_code(session),
            'appkey': '3Lskcm',
            'su': self.uese_64(username),
            'service': 'miniblog',
            'servertime':me['servertime'],
            'nonce': me['nonce'],
            'pwencode': 'rsa2',
            'rsakv': '1330428213',
            'sp': self.get_sp(password, me),
            'encoding': 'UTF-8',
            'prelt': me['exectime'],
            'returntype': 'TEXT'
        }
        async with session.post(deng_url, data=data) as response:
            res = json.loads(await response.text())
            # print(pd_data.loc[:,"uid"])
            pd_data.loc[username, "uid"]=res["uid"]
            print("取得字典形式的Ticket及uid等信息，并按照字典形式返回")
            return res

    async def second_UU(self, session, url, token):
        print("开始登陆后第二次跳转")
        header = {
            'Referer':
            url,
            'User-Agent':
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        }
        data = {
            'ticket':
            token['ticket'],
            'redirect_uri':
            'https://huli.weibot.cn/auth/weibo/callback',
            'appkey62':
            '3Lskcm',
            'action':
            'login',
            'client_id':
            url.split('&', -1)[0].split('=', -1)[1],
            'state':
            url.split('&', -1)[4].split('=', -1)[1],
        }
        async with session.post(self.url[2],
                                headers=header,
                                data=data,
                                allow_redirects=False) as response:
            return response.headers["location"]

    async def zuihou(self,session,url, code_url):
        header = {
            'Referer':
            url,
            'User-Agent':
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        }
        params = {
            'state': url.split('&', -1)[4].split('=', -1)[1],
            'code': code_url.split('&', -1)[1].split('=', -1)[1]
        }
        async with session.get(code_url,
                                headers=header,
                                params=params,
                                allow_redirects=False) as response:
            if response.status==302:
                print("登录成功")
                return response.headers["location"]
            else:
                print("登录失败")




# 主调度函数
    async def main(self, username, pwd):
        # print(pd_data.head())
        cookie = {}
        async with aiohttp.ClientSession() as session:
            url = await self.first_log(session)
            me = await self.denglu_yu(session, username)
            token = await self.fist_denglu(session, username, pwd, me)
            code_url =await self.second_UU(session, url, token)
            zuihou_url = await self.zuihou(session, url, code_url)
            Bearer = zuihou_url.split('&', -1)[0].split('=', -1)[1]
            pd_data.loc[username, "Bearer"]=Bearer
            for cook in session.cookie_jar:
                cookie["SUB"] = cook.value
            pd_data.loc[username, "cookie"] = cookie["SUB"]
            day1 = date.today()
            day2 = day1.isoformat()
            pd_data.loc[username, "time"] = day2
            pd_data.to_csv(log_data)

# 长连接抢单
class long_list():


    def time_time(self):
        now_time = str(int(time.time() * 1000))
        # print('当前的时间戳：', now_time)
        return now_time

# 转发任务
    async def zhuanfa(self, session, xinxi, pl_url):
        url = 'https://weibo.com/aj/v6/mblog/forward?ajwvr=6&domain={}&__rnd={}' .format(xinxi["pid"][0:6], self.time_time())
        data1 = {
            'pic_src': '',
            'pic_id': '',
            'appkey': '',
            'mid': xinxi["mid"],
            'style_type': '2',
            'mark': '',
            'reason': '转发微博',
            'location': 'page_' + xinxi["pid"][0:6] + '_single_weibo',
            'pdetail': xinxi["pid"],
            'module': '',
            'page_module_id': '',
            'refer_sort': '',
            'rank': '0',
            'rankid': '',
            'isReEdit': '',
            '_t': '0'
        }
        header = {
            'Content-Type':
                'application/x-www-form-urlencoded',
            'Host':
                'weibo.com',
            'Origin':
                'https://weibo.com',
            'Pragma':
                'no-cache',
            'Referer':
                pl_url,
            'Sec-Fetch-Dest':
                'empty',
            'Sec-Fetch-Mode':
                'cors',
            'Sec-Fetch-Site':
                'same-origin',
            'X-Requested-With':
                'XMLHttpRequest',
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        }
        async with session.post(url, headers=header, data = data1, allow_redirects=False) as response:
            if response.status == 200:
                print("网站以响应")
                text = await response.text()
                if json.loads(text)["code"] == "100000":
                    print("转发成功")
                    return 1
                else:
                    print("转发未成功")
                    return 2
            else:
                print("网站未响应")
                return 3
# 点赞任务
    async def like(self, session, xinxi, pl_url):
        like_url = "https://weibo.com/aj/v6/like/add?ajwvr=6&__rnd=" + self.time_time()
        data1 = {
            'location': 'page_' + xinxi["pid"][0:6] + '_single_weibo',
            'version': 'mini',
            'qid': 'heart',
            'mid': xinxi["mid"],
            'loc': 'profile',
            'cuslike': '1',
            '_t': '0',
        }
        header = {
            'Content-Type':
                'application/x-www-form-urlencoded',
            'Host':
                'weibo.com',
            'Origin':
                'https://weibo.com',
            'Pragma':
                'no-cache',
            'Referer':
                pl_url,
            'Sec-Fetch-Dest':
                'empty',
            'Sec-Fetch-Mode':
                'cors',
            'Sec-Fetch-Site':
                'same-origin',
            'X-Requested-With':
                'XMLHttpRequest',
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        }
        async with session.post(like_url, headers=header, data=data1, allow_redirects=False) as response:
            if response.status == 200:
                print("网站以响应")
                text = await response.text()
                if json.loads(text)["code"] == "100000":
                    print("点赞成功")
                    return 1
                else:
                    print("点赞未成功")
                    return 2
            else:
                print("网站未响应")
                return 3
# 评论任务
    async def weibo_pinglun(self, session, pl_url, xinxi):
        url = 'https://weibo.com/aj/v6/comment/add?ajwvr=6&__rnd=' + self.time_time()
        data1 = {
            'act': 'post',
            'mid': xinxi["mid"],
            'uid': xinxi["uid"],  # 我的微博用户ID
            'forward': '0',
            'isroot': '0',
            'content': xinxi["content"],  # 评论内容
            'ref': 'home',
            'location': 'page_' + xinxi["pid"][0:6] + '_single_weibo',  # 在需要发表评论的微博页中
            'module': 'bcommlist',
            # page_id  在发表评论的微博页中
            'pdetail': xinxi["pid"],
            '_t': ''
        }
        header = {
            'Content-Type':
                'application/x-www-form-urlencoded',
            'Host':
                'weibo.com',
            'Origin':
                'https://weibo.com',
            'Pragma':
                'no-cache',
            'Referer':
                pl_url,
            'Sec-Fetch-Dest':
                'empty',
            'Sec-Fetch-Mode':
                'cors',
            'Sec-Fetch-Site':
                'same-origin',
            'X-Requested-With':
                'XMLHttpRequest',
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        }
        async with session.post(url, headers= header, data = data1, allow_redirects=False) as response:
            if response.status  == 200:
                print("网站以响应")
                text = await response.text()
                if json.loads(text)["code"]== "100000":
                    print("评论发表成功")
                    return 1
                else:
                    print("评论发表未成功")
                    return 2
            else:
                print("网站未响应")
                return 3


# 取得PID
    async def qu_pid(self, session, url):
        header = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
        }
        async with session.get(url, headers=header) as response:
            res = await response.text()
            results = re.findall(r"\WCONFIG\W\Wpage_id\W\W\W\W(.*?)\W\W", res)[0]
            print("以取得PID：" + results)
            return results
# 任务推送
    async def jianting(self, session, url):
        a = "https:/"
        c = '42["task-receive",'
        async with session.ws_connect(url, timeout=3.0, heartbeat=10.0) as websocket:
            async for msg in websocket:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    print(msg.data)
                    if msg.data.split("[", 1)[0] == "42":
                        if json.loads(msg.data[3:-1].split(",", 1)[0]) == "task-dispatch":
                            print("收到推送订单")
                            b = c + json.dumps(json.loads(msg.data[3:-1].split(",", 1)[1])["data"])+"]"
                            #print(b)
                            await websocket.send_str(b)
                            print("以发送确认订单信息")
                        elif json.loads(msg.data[3:-1].split(",", 1)[0]) == "task-received":
                            print("收到任务信息，以接收到任务")
                            d_data = json.loads(msg.data[3:-1].split(",", 1)[1])["data"]
                            task_xinxi = {
                                "task_id": d_data["task_id"],  # 任务ID
                                "mid": d_data["mid"],  # mid
                                "uid": json.loads(d_data["parameters"])["uid"],  # uid
                                "url": d_data["task_order_info"]["url"],  # 任务链接地址
                                "task_point": d_data["task_order_info"]["task_point"],  # 本次任务金币数
                                "task_type_name": d_data["task_order_info"]["task_type_name"],  # 任务类型
                                "task_type": d_data["task_order_info"]["task_type"],  # 任务编号
                                "point": d_data["user_task_info"]["point"]  # 账户总金币数
                            }
                            pl_url = a + task_xinxi["url"].split("/", 1)[1]
                            pid = await self.qu_pid(session, pl_url)
                            task_xinxi["pid"] = pid
                            # 点赞任务
                            if task_xinxi["task_type"] == "1_1_0":
                                print(task_xinxi)
                                dz_code = await self.like(session, task_xinxi, pl_url)
                                # pl_code 是返回码，1表示成功发表成功，2表示发表未成功，3表示网络未响应
                            # 转发任务
                            elif task_xinxi["task_type"] == "1_2_0":
                                print(task_xinxi)
                                zf_code = await self.zhuanfa(session, task_xinxi, pl_url)
                                # pl_code 是返回码，1表示成功发表成功，2表示发表未成功，3表示网络未响应
                            # 评论任务
                            elif task_xinxi["task_type"] == "1_3_1":
                                task_xinxi["content"] = d_data["task_order_info"]["content"]  # 任务内容
                                print(task_xinxi)
                                xy_code = await self.weibo_pinglun(session, pl_url, task_xinxi)
                                # pl_code 是返回码，1表示成功发表成功，2表示发表未成功，3表示网络未响应
                            # 关注任务
                            elif task_xinxi["task_type"] == "1_4_0":
                                print("关注任务！！！！！！！！！！！！！！！！！！！！")

                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        print("连接出错")
                    elif msg.type == aiohttp.WSMsgType.closed:
                        print("连接关闭")


# 抢单及任务调度函数
    async def main(self, bearer, cookie):
        url = "wss://socket.hulihuzhu.com/socket.io/?user_type=single&user_not=&sku_type=1_1_1-1_1_0-1_2_0-1_2_1-1_3_1-1_3_5-1_4_0&sku_not=&token="+bearer
        cookies = {
            "SUB": cookie
        }
        async with aiohttp.ClientSession(cookies=cookies) as session:
            await self.jianting(session, url)




def main():
    wb_dl = denglu()
    if len(user_log) != 0:
        print("正在登录")
        loop = asyncio.get_event_loop()
        tasks = [wb_dl.main(user_log[i], passwords[i])for i in range(0, len(user_log))]
        loop.run_until_complete(asyncio.gather(*tasks))
    else:
        print("以登录可以向下操作")
        huli_long = long_list()
        cookies = []
        Bearer = []
        for item in list(pd_data.loc[:, "cookie"]):
            cookies.append(item)
        for token in list(pd_data.loc[:, "Bearer"]):
            Bearer.append(token)
        loop = asyncio.get_event_loop()
        task = [huli_long.main(Bearer[i], cookies[i])for i in range(0, len(cookies))]
        loop.run_until_complete(asyncio.gather(*task))

if __name__ == "__main__":
    log_data = "config.csv"
    user_log = []
    passwords = []
    if os.path.isfile(log_data) == True:
        print("文件存在")
        pd_data = pd.read_csv(log_data).set_index("user")
        # print(pd_data.head())
        for user in list(pd_data.index):
            time11 = pd_data.loc[user, "time"]
            day = date.today() - date.fromisoformat(time11)
            if day.days != 0:
                user_log.append(user)
                passwords.append(pd_data.loc[user, "password"])
        main()
    else:
        print("文件不存在")
        with open(log_data, "w+") as f:
            print("文件以创建")
        data = {
            "user": [],
            "password": [],
            "uid": [],
            "cookie": [],
            "Bearer": [],
            "time": [],
        }
        pd_data = pd.DataFrame(data).set_index("user")
        pd_data.to_csv(log_data)
