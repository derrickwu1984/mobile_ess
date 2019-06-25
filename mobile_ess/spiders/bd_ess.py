# -*- coding: utf-8 -*-
import scrapy,logging,requests,time,json
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from scrapy.http import Request
from urllib import parse
from lxml import etree
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC #期望的条件
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from scrapy.loader import  ItemLoader
import time,re
import json
import datetime
import pickle
import sys
from io import BytesIO
from scrapy.http.cookies import CookieJar

class BdEssSpider(scrapy.Spider):
    name = 'bd_ess'
    allowed_domains = ['https://ess.10010.com/essframe']
    start_urls = ['http://https://ess.10010.com/essframe/']
    login_url = "https://ess.10010.com/essframe"
    # 登陆后的链接
    initmy_url = "https://123.125.98.209/essframe"
    driver_path = "D:/tools/IEDriverServer.exe"
    userName = "bjsc-zhaomx6"
    passWd = "wang1985@"
    province_code = "bj"
    depart_id = "11b2kv5"
    province_id = "11"
    driver = webdriver.Ie(driver_path)
    js_exec = "var but_click=document.getElementsByClassName('submit')[0].children[0].onclick"


    def __init__(self, broadbandNo, startNo, endNo):
        self.broadbandNo = broadbandNo
        self.startNo = startNo
        self.endNo = endNo
        self.cur_month = self.date_Formate(datetime.datetime.now().month)
        self.cur_day = self.date_Formate(datetime.datetime.now().day)
        self.crawldate = str(datetime.datetime.now().year) + str(self.cur_month) + str(self.cur_day)
        self.params = ''
        pass

    # 将月份、日期小于10的前面补充0
    def date_Formate(self, object):
        if (object < 10):
            object = "0" + str(object)
        return object

    def start_requests(self):
        logging.warning("=========start_requests===========")
        yield scrapy.Request(self.login_url, callback=self.login)
    def login(self, response):
        self.driver.get(self.login_url)
        time.sleep(3)
        self.driver.find_element_by_id("STAFF_ID").send_keys(self.userName)
        self.driver.find_element_by_id("LOGIN_PASSWORD").send_keys(self.passWd)
        Select(self.driver.find_element_by_name("LOGIN_PROVINCE_CODE")).select_by_value(self.province_id)
        WebDriverWait(self.driver, 1000).until(EC.url_to_be(self.initmy_url))
        logging.warning("恭喜您，您已登录成功了！")
        WebDriverWait(self.driver, 600).until(EC.presence_of_element_located((By.ID, 'navframe')))
        self.driver.switch_to.frame("navframe")
        # time.sleep(30)
        WebDriverWait(self.driver, 600).until(EC.presence_of_element_located((By.ID, 'SECOND_MENU_LINK_BIL6500')))
        # in order to find CSM1001
        js_query_acct = "var query_acct=document.getElementById('SECOND_MENU_LINK_BIL6500').onclick()"
        self.driver.execute_script(js_query_acct)
        time.sleep(3)
        WebDriverWait(self.driver, 600).until(EC.presence_of_element_located((By.ID, 'BIL6531')))
        openmenu = self.driver.find_element_by_id("BIL6531").get_attribute("onclick")
        r = re.findall(r"'([\S\s]+?)'", openmenu)
        request_url = "https://" + self.province_code + ".cbss.10010.com" + r[
            0] + "&staffId=" + self.userName + "&departId=" + self.depart_id + "&subSysCode=CBS&eparchyCode=0010"
        requests.adapters.DEFAULT_RETRIES = 5
        s = requests.session()
        cookies_dict = {}
        cookies = self.driver.get_cookies()
        for cookie in cookies:
            cookies_dict[cookie['name']] = cookie['value']
        with open('cookies.txt', 'w+') as f:
            json.dump(cookies_dict, f)
        with open('cookies.txt', 'r') as f:
            cookie_out = json.load(f)
        headers = {
            'Referer': 'https://bj.cbss.10010.com/essframe?service=page/Sidebar',
            'Host': 'bj.cbss.10010.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }
        yield scrapy.Request(request_url, headers=headers, cookies=cookie_out, callback=self.parse_broadbandNo,
                             meta={'request_url': request_url})

    def query_user_info(self,response):
        Cookie = response.request.headers.getlist('Cookie')
        response_str=response.body.decode("gbk")
        refer_url=response.meta['userinfo_request_url']
        # time.sleep(3)
        html = etree.HTML(response_str)
        DateField=""
        _BoInfo=html.xpath('//input[@name="_BoInfo"]/@value')[0]
        ACCPROVICE_ID=html.xpath('//input[@name="ACCPROVICE_ID"]/@value')[0]
        allInfo=html.xpath('//input[@name="allInfo"]/@value')[0]
        broadbandNo = response.meta['broadbandNo']
        currentRightCode=html.xpath('//input[@name="currentRightCode"]/@value')[0]
        Form0 = html.xpath('//input[@name="Form0"]/@value')[0]
        PROVICE_ID= html.xpath('//input[@name="PROVICE_ID"]/@value')[0]
        queryTradehide=html.xpath('//input[@name="queryTradehide"]/@value')[0]
        service=html.xpath('//input[@name="service"]/@value')[0]
        tabSetList=html.xpath('//input[@name="tabSetList"]/@value')[0]
        headers={
            # "Referer": "https://bj.cbss.10010.com/essframe?service=page/Sidebar,
            # "Referer": "https://bj.cbss.10010.com/custserv",
            "Referer":refer_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Host': 'bj.cbss.10010.com'
        }
        cookies = self.get_cookie()
        # del cookies["BSS_CUSTSERV_JSESSIONID"]
        # del cookies["BSS_ACCTMANM_JSESSIONID"]
        # json.dumps(cookies)
        dataForm=self.custserv_dataForm(DateField,_BoInfo,ACCPROVICE_ID,allInfo,broadbandNo,ACCPROVICE_ID,currentRightCode,Form0,PROVICE_ID,queryTradehide,service,tabSetList)
        post_intetrated_url="https://bj.cbss.10010.com/custserv"
        yield scrapy.FormRequest(url=post_intetrated_url, formdata=dataForm, method="POST", headers=headers,cookies=cookies,
                                 callback=self.get_user_property__info,meta={'broadbandNo': broadbandNo},dont_filter=True)