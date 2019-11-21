#!/usr/bin/env
# coding=utf-8
import importlib
import redis
import json
import os
import sys
importlib.reload(sys)
sys.setdefaultencoding("utf-8")

"""
核心入口文件
我们订阅redis的topic
调用{@link uiauto.py}去处理
"""

host = "******"
port = 6379
password = "******"
task_queue_name = "somp_crawl_list"
process_queue_name = "process_somp_crawl_list"
system_command = "python uiauto.py %1s %2s "


def process_task(task_str):
    task_json = json.loads(task_str)
    openid = task_json["openid"]
    name = task_json["name"]
    wxid = task_json["wxid"]
    print("receive a task [%1s][%2s] " % (name, wxid))
    code = os.system(system_command % (wxid, name))
    if int(code) == 0:
        task.remove_task(task_str)

    print("finish task [%1s] " % name)


class Task(object):
    def __init__(self):
        self.__pool__ = redis.ConnectionPool(host=host, port=port, password=password)
        self.__conn__ = redis.Redis(connection_pool=self.__pool__)
        print("connect redis success")

    def list_task(self):
        while True:
            task_str = self.__conn__.brpoplpush(task_queue_name, process_queue_name, timeout=0)
            process_task(task_str)

    def put_test_task(self, i):
        self.__conn__.lpush(task_queue_name, i)

    def remove_task(self, task_str):
        self.__conn__.lrem(process_queue_name, task_str)

    def close(self):
        self.__pool__.disconnect()


if __name__ == "__main__":
    task = Task()
    task.list_task()
    task.close()
