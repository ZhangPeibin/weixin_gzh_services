#!/usr/bin/env python
# coding=utf-8
from bs4 import BeautifulSoup
import sys
import json
import os
import time
import pycurl
import sql
import importlib


importlib.reload(sys)
sys.setdefaultencoding("utf-8")

tmp = "tmp/"
db = None
pnp_data = "pnp_data/"
biz_name_json_path = pnp_data + "biz_name_json"


def process_list(message_json_tuple, save_path):
    for value in message_json_tuple:

        # 纯文本
        if 'app_msg_ext_info' not in value.keys():
            continue

        app_msg_ext_info = value['app_msg_ext_info']
        comm_msg_info = value['comm_msg_info']
        content_url = str(app_msg_ext_info['content_url']).replace("&amp;amp;", "&").replace("\\", "")
        title = str(app_msg_ext_info['title']).replace('/', '／').replace('\\', '＼')
        datetime = comm_msg_info['datetime']
        wc_id = comm_msg_info['id']
        cover = app_msg_ext_info['cover'].replace("\\", "")
        c_path = os.path.join(save_path, title + ".html")
        db.save_to_db(title, datetime, wc_id, cover, c_path)
        download(c_path, content_url)
        time.sleep(2)


def process_home(content, save_path):
    start = content.index('msgList')
    end = content.index(r'if(!!window.__initCatch)')
    messageList = content[start:end]
    messageList = str(messageList[messageList.index(r'{'):messageList.rindex(r"}") + 1])
    messageList = messageList.replace("&quot;", "\"")
    messageJsonDict = json.loads(messageList, encoding='utf-8')
    messageJsonTuple = messageJsonDict['list']
    process_list(messageJsonTuple, save_path)


def process_more(content, save_path, wc_name):
    json_data = json.loads(content)
    can_msg_continue = int(json_data['can_msg_continue'])
    general_msg_list = json.loads(json_data['general_msg_list'])
    if general_msg_list is None:
        print("error can not find list")
    messageJsonTuple = general_msg_list['list']
    process_list(messageJsonTuple, save_path)

    if can_msg_continue == 0:
        with open(tmp + wc_name + ".task.status", 'wb') as f:
            f.write("0")


def save_biz_name(biz, name):
    with open(biz_name_json_path, "a+") as f:
        biz_exist = False
        for line in f:
            biz_name_json = json.loads(line)
            if biz in biz_name_json.keys():
                biz_exist = True
                break
        if not biz_exist:
            biz_json = {biz: name}
            f.write(json.dumps(biz_json) + "\n")


def read_biz_name(msg_offset, soup, biz):
    # 公众号
    if int(msg_offset) == 0:
        # 从html解析公众号名称
        wechat_public_num_name = str(soup.find('strong', 'profile_nickname').string).lstrip().rstrip()
        save_biz_name(biz, wechat_public_num_name)
        return wechat_public_num_name
    else:
        with open(biz_name_json_path, 'r') as f:
            for line in f:
                biz_name_json = json.loads(line)
                if biz in biz_name_json.keys():
                    wechat_public_num_name = biz_name_json[biz]
                else:
                    wechat_public_num_name = biz
        return wechat_public_num_name


def process(biz, page_cache_path, msg_offset):
    soup = BeautifulSoup(open(page_cache_path))
    if soup is None:
        print("open %s err " % page_cache_path)

    wechat_public_num_name = read_biz_name(msg_offset=msg_offset, soup=soup, biz=biz)

    pnp_save_dir = pnp_data + wechat_public_num_name + "/"

    global db
    db = sql.SqlHelper(str(biz).replace("=", ""))

    pnp_save_dir = pnp_save_dir + msg_offset + "/"
    if not os.path.exists(pnp_save_dir):
        os.mkdir(pnp_save_dir)

    if int(offset) == 0:
        content = soup.prettify()
        process_home(content, pnp_save_dir)
    else:
        with open(page_cache_path, 'r') as f:
            process_more(f.read(), pnp_save_dir, wechat_public_num_name)


class WeChatNumDetails:
    def __init__(self, save_path):
        self.contents = ''
        self.save_path = save_path

    def callback(self, curl):
        self.contents = self.contents + curl
        try:
            with open(self.save_path, "wb") as f:
                f.write(self.contents)
        except Exception as e:
            print(e)


def download(save_path, url):
    t = WeChatNumDetails(save_path)
    c = pycurl.Curl()
    c.setopt(pycurl.WRITEFUNCTION, t.callback)
    c.setopt(pycurl.URL, url)
    c.perform()


if __name__ == "__main__":
    if len(sys.argv) == 0:
        print("错误的参数")
    else:
        _biz = sys.argv[1]
        path = sys.argv[2]
        offset = sys.argv[3]
        process(_biz, path, offset)
