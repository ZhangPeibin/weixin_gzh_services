# coding=utf-8
import requests
from lxml import etree
import html
import json

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': 'IPLOC=CN4420; SUV=1506943186112167; ABTEST=7|1506942416|v1; weixinIndexVisited=1; CXID=5D12500D59021E7399D71313F1F3736E; SNUID=FE101C8A55530E4D7C80B78B561D857E; ppinf=5|1507547135|1508756735|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTo2OnF6dXNlcnxjcnQ6MTA6MTUwNzU0NzEzNXxyZWZuaWNrOjY6cXp1c2VyfHVzZXJpZDo0NDoyNzVGNzI2NzhEQTEyMDQ1NkEzNjYyNTc1MEIwNDQwREBxcS5zb2h1LmNvbXw; pprdig=qWa4OUzE1V7jnZWg4yi28BlzbppqmCEVxtugIH_Fggcpg4miTfTinUIVxlSH1hajo0HFOsvjeh1MEK7ZcMOZTkIMJrydWDM7AY4XFBQNqNuctnJkdwXT0DejbkAbY72KyREVSQHkScUzsQoYijJD5k3JTfLYyGe34WOzaBkR6xw; sgid=08-31389655-AVnbVicibgcwK5wiaicVxicoibAYM; pgv_pvi=2191015936; sw_uuid=5806069797; dt_ssuid=197528870; pex=C864C03270DED3DD8A06887A372DA219231FFAC25A9D64AE09E82AED12E416AC; ssuid=3172653254; cd=1507558955&1f77085a987b907d27e166ccf0d64aa6; GOTO=Af22417-3002; ad=MN4tSZllll2BCESBlllllVXbAgYlllllns@mxkllllwllllljylll5@@@@@@@@@@; SUID=554549DF1508990A00000000591EB0DE; ld=Byllllllll2BLcR7QNm9ICXb0CJBLcYrT1OV$llllx6lllljjylll5@@@@@@@@@@; LSTMV=242%2C73; LCLKINT=95504; ppmdig=15075639020000004eb5e8a786550e64db4915a5227e0eeb; sct=60; JSESSIONID=aaa_21YiQD6W_8okinz6v',
    'Host': 'weixin.sogou.com',
    'Pragma': 'no-cache',
    'Referer': 'http://weixin.sogou.com/weixin?type=2&query=python&ie=utf8&s_from=input&_sug_=n&_sug_type_=1&w=01015002&oq=&ri=14&sourceid=sugg&sut=0&sst0=1507564693572&lkt=0%2C0%2C0&p=40040108',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
}
gzh_list_url = "https://weixin.sogou.com/weixin"


class RequestGzhList:

    @staticmethod
    def request_gzh_list(gzh_name, page=0):
        """
         获取公众号列表
        :param gzh_name:公众号名称
        :param page: 当前的公众号列表索引
        """
        kv = {"query": gzh_name, '_sug_type_': '', 's_from': 'input',
              '_sug_': 'n', 'type': '1', 'page': page, 'ie': 'utf-8'}

        response = requests.get(gzh_list_url, kv, headers=headers)
        response.encoding = 'utf-8'

        return RequestGzhList.parse_gzh_list(response.content)

    @staticmethod
    def parse_gzh_list(gzh_list):
        """
        解析文章列表
        :param gzh_list: gzh列表的html数据
        :return: 列表的[]数据源，总共有多少页
        """
        gzh_list_html = etree.HTML(gzh_list)
        gzh_list_items = gzh_list_html.xpath('//ul[@class="news-list2"]/li')
        gzh_list_models = []
        for gzh_list_item in gzh_list_items:
            """
                img,name,wxid,intro
            """
            img_box_value = gzh_list_item.xpath('.//div[@class="img-box"]/a/img/@src')[0]
            wx_name = html.unescape(str(etree.tostring(gzh_list_item.xpath('.//div[@class="txt-box"]/p/a')[0])))
            l_index = str(wx_name).find(">")
            r_index = str(wx_name).find("</a>")
            wx_name = str(wx_name)[l_index + 1:r_index]
            # .replace("<em>", "").replace("</em>", "").replace("<!--red_beg-->", "").replace("<!--red_end-->", "")
            wx_id = gzh_list_item.xpath('.//div[@class="txt-box"]/p[@class="info"]/label/text()')[0]

            dl_list = gzh_list_item.xpath('.//dl')
            intro = ''
            if len(dl_list) > 0:
                intro_html = dl_list[0].xpath('.//dd')[0]
                intro = html.unescape(str(etree.tostring(intro_html)))

            gzh_list_model = GzhListModel(img_box_value, wx_id, wx_name, intro)
            # gzh_list_models.append(json.dumps(gzh_list_model.__dict__))
            gzh_list_models.append(gzh_list_model.__dict__)

        print(json.dumps(gzh_list_models))
        page_fy = gzh_list_html.xpath('//div[@class="p-fy"]/a')
        page_fy_count = len(page_fy)
        return gzh_list_models, page_fy_count


class GzhListModel:
    def __init__(self, img, wx_id, wx_name, wx_intro):
        self.img = img
        self.wx_id = wx_id
        self.wx_name = wx_name
        self.wx_intro = wx_intro


if __name__ == '__main__':
    RequestGzhList.request_gzh_list("唐")
