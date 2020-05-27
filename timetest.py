from datetime import date,timedelta
import time
import pandas as pd
# t = date(2010, 10, 10).isoformat()
# print(type(t))
#
# print(date.today())            # 返回一个当前年月日
# print(date.fromtimestamp(time.time()))     # 传入时间戳，返回年月日
# print(date.fromordinal(date.max.toordinal()))     # 传入天数返回日期，起始日期为1970年1月1日
# print(date.max.toordinal())               # 系统支持的最大天数
# print(type(date.fromisoformat(t)))
# print(date.year)
# print(date.today().max)
#
# day1 = date.today()
# day2 = date(2010, 10, 10)
# day4 = day1.isoformat()
# day3= day1 - day2
# print(day3)
#
# print(timedelta(hours = 23))
# print(day1)
# # print(day4)
# #
# # # today = date.today()
# # # m_today = date.today()
# # # timedelta = m_today - today
# # # print(timedelta.days)
# # # if timedelta.days == 0 :
# # #     print("未过期")
# # # else :
# # #     print("过期")
# ceshi = "ceshi.csv"
# fd = pd.read_csv(ceshi).set_index("user")
# # print(fd.head())
# # print(list(fd.index))
#
# # passwords = []
# # # fd.loc["dingsiwen99", "time"] = ["121234566"]
# # # print(fd.head())
# # for user in list(fd.loc[:,"Bearer"]):
# #     user_log.append(user)
# # # print(user_log)
# # for i in list(fd.loc[:,"Bearer"]):
# #     print(i)
# cookies = {
#     "1":"2",
#     "2":"3"
# }
# # Bearer = []
# # for item in list(fd.loc[:, "cookie"]):
# #     cookies.append(item)
# # for token in list(fd.loc[:,"Bearer"]):
# #     Bearer.append(token)
# # print(cookies)
# # print(Bearer)
# #print(user_log)
# print(cookies)
#
#     else:
#         pass
# print(user_log)

now_time = str(int(time.time() * 1000))
# print('当前的时间戳：', now_time)
print(type(now_time))