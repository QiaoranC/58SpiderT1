# -*- coding: utf-8 -*-
import scrapy
import re
# from redis import Redis
import redis
from scrapy_redis.spiders import RedisSpider

# error系列
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

# from scrapy.loader import ItemLoader
from scrapy.http import Request
from urllib import parse
import logging

import json
import time

from tcErShouFangT1.items import Tcershoufangt1Item
from tcErShouFangT1.config import *

#log文件==========================================================================
import logging
from scrapy.utils.log import configure_logging

configure_logging(install_root_handler=False)
logging.basicConfig(
    filename='logItem.txt',
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO
)
#===============================================================================

logger = logging.getLogger()
r = redis.StrictRedis(host='106.75.166.130', port=6379, db=0, password='v5e7r8o4n4i9c0a9')
stimeR = time.strftime("%Y/%m/%d")
syear = time.strftime("%Y") 
CurrentDate = re.sub('[/]', '-', stimeR) #从2017/09/28 换成 2017-09-28
        
class Tcershoufangx1Spider(RedisSpider):
    name = 'tcErShouFangT1'
    redis_key = "58House:All"

    def parse(self, response):
        info_item = Tcershoufangt1Item()
        room  = ''
        list = []
        acerage = ''
        rent_type_content =''
        price = ''
        price_unit = ''
        rent_mode = ""
        list_pack = {}
        house_type = ''
        list_pack_floor = ""
        rooms = ''
        category= ''
        
        Rurl = response.url
        C1 = re.search(r'58.com/zufang/', Rurl) #出租
        C2 = re.search(r'58.com/hezu/', Rurl)
        Q1 = re.search(r'58.com/qiuzu/', Rurl)  #求租
        D1 = re.search(r'58.com/duanzu/', Rurl) #短租
        E1 = re.search(r'58.com/ershoufang/', Rurl) #二手房
        X1 = re.search(r'58.com/zhaozu/', Rurl) #写字楼    
        S1 = re.search(r'58.com/shangpu/', Rurl) #商铺
        FKHT1 = re.search(r'58.com/fangchan/', Rurl) #厂房 仓库 土地 车位
    #出租 ================================================================================================================
        if C1 or C2:
            info_item["category_second_id"] = chuzufang.category_second_id
            name = response.xpath('//div[@class="house-title"]/h1/text()')
            title = response.xpath('/html/head/title/text()')
            description = response.xpath('/html/head/meta[@name="description"]/@content')
            refresh_at = response.xpath('//p[contains(@class,"house-update-info")]//text()')
            imgs = response.xpath('//ul[@id="housePicList"]//@lazy_src').extract()
            details = response.xpath('//ul[@class="introduce-item"]/li[2]/span[2]//text()').extract()

            if name: 
                name = name.extract_first().strip()
            if title:
                title = title.extract_first().strip()
            if description:
                description =description.extract_first().strip()    
            if refresh_at:
                refresh_at =refresh_at.extract_first().strip()            
                if re.search(r'分钟前', refresh_at) or re.search(r'小时前', refresh_at) or re.search(r'天前', refresh_at):
                    refresh_at = CurrentDate           
                else:
                    refresh_at = syear + '-' + refresh_at      
            phoneO = response.xpath('//span[@class="house-chat-txt"]//text()').extract()
            if phoneO:
                a = phoneO[0]
                if a != '扫码看电话':
                    phone = a
            
            contactInfoR = response.xpath('//a[@class="c_000"]//text()').extract()
            if contactInfoR: 
                contactInfo =contactInfoR[0]
                contact_name = re.findall(r'(^.*)\(', contactInfo)[0]
                owner_type = re.findall(r'\((.*?)\)', contactInfo)[0]
            else:
                logger.info("V's Cannot get Conact in %s" % Rurl)
                contact_name = '王先生'
                owner_type = '个人'
                
            #配置------------------------------
            allocation = response.xpath('//ul[@class="house-disposal"]/li/text()').extract()
            
            #位置 市域圈------------------------------------------------------------------------
            NavBar = response.xpath('//div[contains(@class,"nav-top-bar")]//text()').extract()
            
            if len(NavBar) >= 5:
                city3 = NavBar[3]
                keywords = city3    #关键词为 武威租房
                if re.search(r'合租房', city3):
                    city3 = re.findall(r'(^.*)合租房', city3)[0]
                else:
                    city3 = re.findall(r'(^.*)租房', city3)[0]
                position_city = city3  
                if len(NavBar) >= 7:
                    city5 = NavBar[5]
                    if re.search(r'合租房', city5):
                        city5 = re.findall(r'(^.*)合租房', city5)[0]
                    else:
                        city5 = re.findall(r'(^.*)租房', city5)[0]
                    position_district = city5
                    if len(NavBar) == 9:
                        city7 = NavBar[7]
                        if re.search(r'合租房', city7):
                            city7 = re.findall(r'(^.*)合租房', city7)[0]
                        else:
                            city7 = re.findall(r'(^.*)租房', city7)[0]                
                        position_commercial_area = city7
            else:
                logger.info("V's NavBar Size not perdicted in %s" % Rurl)
            #----------------------------------------------------------------------------                        
            price = response.xpath('//b[@class="f36"]/text()')          
            if price:
                price = price.extract_first().strip()  
                if price = "面议":
                    price = -1
                else:
                    price_unit = response.xpath('//span[@class="c_ff552e"]/text()')
                    if price_unit:
                        price_unit = price_unit.extract_first().strip()
            else:
                logger.info("V's Cannot get Price in %s" % Rurl)
                price = -1
                        
            #pack and list---------------------
            FList = {}
            packs = response.xpath('//ul[@class="f14"]/li')
            for i in range(0, len(packs)):
                name = packs[i].xpath("./span[1]/text()").extract_first()
                if re.search(r'租赁方式：', name): #'整租'
                    a1 = packs[i].xpath("./span[2]/text()").extract_first().strip()
                    YaYiFuYi = response.xpath('//span[@class="c_333"]/text()')
                    if re.search(r'整租', a1):
                        rent_mode = "整套出租"
                    elif re.search(r'合租', a1):
                        rent_mode = "单间出租"
                    FList['租赁方式：'] = a1
                    if YaYiFuYi:
                        YaYiFuYi = YaYiFuYi.extract_first().strip()
                        FList['租赁方式：'] = a1 + '  ' + YaYiFuYi
                if re.search(r'房屋类型：', name): #
                    a2 = packs[i].xpath("./span[2]/text()").extract_first().strip()
                    AreaR = re.findall(r'\d+', a2)[3]  #32
                    RoomR = re.findall(r'(^.*卫)', a2)[0]  #1室1厅1卫     
                    FList['房屋类型：'] = RoomR + '  ' + AreaR + '㎡'  #RoomR + '  ' + AreaR + '㎡'
                    list_pack['厅室'] = RoomR                   
                    list_pack['面积'] = AreaR
                    acerage = AreaR    
                    if RoomR:
                        if re.search(r'1室', RoomR):
                            room = "一室"
                        elif re.search(r'2室', RoomR):
                            room = "二室"
                        elif re.search(r'3室', RoomR):
                            room = "三室"
                        elif re.search(r'4室', RoomR):
                            room = "四室"
                        else:
                            room = "四室以上"                    
                if re.search(r'朝向楼层：', name): # 
                    a3 = packs[i].xpath("./span[2]/text()").extract_first().strip()
                    FList['朝向楼层'] = re.sub('[\xa0\xa0]', ' ', a3)  #南\xa0\xa0共2层 ->南  共2层
                if re.search(r'所在小区：', name): #'锦博苑'
                    a4 = packs[i].xpath("./span[2]/a/text()").extract_first().strip()
                    FList['所在小区：'] = a4
                if re.search(r'所属区域：', name): #'浦东    北蔡'
                    a5 = packs[i].xpath("./span[2]//text()").extract()       
                    a5 = ' '.join([str(x) for x in a5])    #list换str
                    a5 = re.sub('[\r\n]', ' ', a5)        #str 去\r\n
                    a5 = a5.replace(" ", "")               #去空格
                    a5 = re.sub('[\xa0\xa0]', ' ', a5)                    
                    FList['所属区域：'] = a5     
                if re.search(r'详细地址：', name): # '高科西路2111弄159号三楼桂和公寓'
                    b1 = packs[i].xpath("./span[2]//text()").extract_first().strip()
                    FList['详细地址：'] = b1
                    position_detail = b1
            if FList:
                list.append(FList)                
    
    #求租 短租 ===========================================================================================================
        if Q1 or D1:
            name = response.xpath('//div[@class="w headline"]/h1/text()')
            title = response.xpath('/html/head/title/text()')
            description = response.xpath('/html/head/meta[@name="description"]/@content')
            keywords = response.xpath('//span[@id="keyword"]/text()')
            views = response.xpath('//em[@id="totalcount"]//text()')
            contact_nameR = response.xpath('//ul[@class="userinfo"]/li[2]/a/text()')            
            if name: 
                name = name.extract_first().strip()
            if title:
                title = title.extract_first().strip()
            if description:
                description =description.extract_first().strip()    
            if keywords:
                keywords = keywords.extract_first().strip()
            if views:
                views = views.extract_first().strip()
            if contact_nameR:
                contact_name = contact_nameR.extract_first().strip()
            owner_typeR = response.xpath('//em[@class="medium"]//text()')
            if owner_typeR:
                owner_type = owner_typeR.extract_first().strip()            
            
            #refresh_at
            create_dataOrginal = response.xpath('//div[contains(@class, "other")]/text()[1]').extract_first().strip() #发表时间: 2017-09-11
            create_data = re.findall("：(.+?)$", create_dataOrginal) #匹配:到最后一位之间的
            refresh_at = create_data[0]
            
            # imgs = response.xpath('//ul[@id="housePicList"]//@lazy_src').extract()
            details = response.xpath('//div[@class="maincon"]/text()').extract_first().strip()
            
            #phone 
            phoneURLOrginalCheck = response.xpath("//span[@id='t_phone']/script/text()").extract_first()
            PhoneNumberCheck = response.xpath("//span[@id='t_phone']//text()").extract_first()
            if phoneURLOrginalCheck:
                phoneURLOrginal = phoneURLOrginalCheck.strip()
                phone = re.findall('\'(.*?)\'',phoneURLOrginal)[0]
            else:
                phone = PhoneNumberCheck.strip()    
    
        #求租---------------------------------------------
        if Q1:
            info_item["category_second_id"] = qiuzufang.category_second_id
            #pack and list---------------------
            FList = {}
            roomR = response.xpath('//ul[@class="info"]/li[2]/text()')
            RentO = response.xpath('//ul[@class="info"]/li[3]//text()').extract()
            AvailableTiming = response.xpath('//ul[@class="info"]/li[4]/text()')
            if roomR:
                room = roomR.extract_first().strip() 
                FList['居室'] = room
                list_pack['所期望居室'] = room
            if Rent0:
                price = RentO[1]
                price_unit = RentO[2].strip()
                FList['租金'] = price + ' ' + price_unit
                list_pack['期望租金'] = price + ' ' + price_unit
            if AvailableTiming:
                Atime = AvailableTiming.extract_first().strip() 
                FList['入住'] = Atime
            list.append(FList)                            
            
            #位置图--------------------
            NavBar = response.xpath('//span[@id="crumbs"]/a/text()').extract()
            if len(NavBar) >= 3:
                city3 = NavBar[2]
                position_city = re.findall(r'(^.*)求租房', city3)[0]
                position_detail = position_city
                if len(NavBar) >= 4:
                    city4 = NavBar[3]
                    position_district = re.findall(r'(^.*)求租房', city4)[0]
                    position_detail = position_district
                    if len(NavBar) >= 5:
                        city5 = NavBar[4]
                        position_commercial_area = re.findall(r'(^.*)求租房', city5)[0]
                        position_detail = position_commercial_area
            else:
                logger.info("V's NavBar issue in  %s" % Rurl)
                
            if room:
                if re.search(r'1室', room):
                    room = "整租一室"
                elif re.search(r'2室', room):
                    room = "整租二室"
                elif re.search(r'3室', room) or re.search(r'合租', room):
                    room = "整租三室"
                elif re.search(r'4室', room):
                    room = "整租四室"
                else:
                    room = "整租四室以上"    
            
        #短租---------------------------------------------
        if D1:
            info_item["category_second_id"] = duanzufang.category_second_id
            imgs = response.xpath('//div[@class="bigimg"]//@src').extract()
            alt = response.xpath('//div[@class="bigimg"]//@alt').extract()
            
            #位置图-----------------------
            NavBar = response.xpath('//span[@id="crumbs"]/a/text()').extract()
            if len(NavBar) >= 3:
                city3 = NavBar[2]
                position_city = re.findall(r'(^.*)短租房/日租房', city3)[0]
                if len(NavBar) >= 4:
                    city4 = NavBar[3]
                    position_district = re.findall(r'(^.*)短租房/日租房', city4)[0]
                    if len(NavBar) >= 5:
                        city5 = NavBar[4]
                        position_commercial_area = re.findall(r'(^.*)短租房/日租房', city5)[0]
            else:
                logger.info("V's NavBar issue in  %s" % Rurl)                
            
            #pack and list---------------------
            packs = response.xpath('//ul[@class="info"]/li')
            for i in range(0, len(packs)):
                FList = {}
                name = packs[i].xpath("./i/text()").extract_first()
                if re.search(r'区域：', name): 
                    a = packs[i].xpath("./a/text()").extract_first().strip()
                if re.search(r'类型：', name): 
                    b = packs[i].xpath("./text()").extract_first().strip()
                    FList['类型'] = b
                    list_pack['类型'] = b
                    house_type = b                       
                if re.search(r'地段：', name): 
                    c = packs[i].xpath("./text()").extract_first().strip()
                    FList['地段'] = c
                if re.search(r'租金：', name): 
                    price = packs[i].xpath("./em/text()").extract()[0]
                    price_unitR = packs[i].xpath("./text()").extract_first().strip()      
                    if re.search(r'最短租期', name): 
                        price_unit = re.findall(r'(.*?)\(', price_unitR)[0].strip()
                        MinStay = re.findall(r'\((.*?)\)', price_unitR)[0].strip()
                        FList['租金'] = price + ' ' + price_unit + '(' + MinStay + ')' # '租金': '20 元/天(最短租期 1 天)'
                    else:
                        price_unit = price_unitR                     
                        FList['租金'] = price + ' ' + price_unit +  # '租金': '20 元/天'
                    list_pack['租金'] = price + ' ' + price_unit
            if FList:
                list.append(FList)
        
    #二手房 ==============================================================================================================
        if E1:
            info_item["category_second_id"] = ershoufang.category_second_id
            name = response.xpath('//div[@class="house-title"]/h1/text()')
            title = response.xpath('/html/head/title/text()')
            description = response.xpath('/html/head/meta[@name="description"]/@content')
            refresh_at = response.xpath('//span[@class="up"][@id]//text()')
            
            if name: 
                name = name.extract_first().strip()
            if title:
                title = title.extract_first().strip()
            if description:
                description =description.extract_first().strip()    
            if refresh_at:
                refresh_at = refresh_at.extract_first().strip() 
                if re.search(r'分钟前', refresh_at) or re.search(r'小时前', refresh_at) or re.search(r'天前', refresh_at):
                    refresh_at = CurrentDate
                else:
                    refresh_at = syear + '-' + refresh_at 
                        
            imgs = response.xpath('//ul[@class="general-pic-list"]/li//img/@data-src').extract()
            
            #details
            details = str(response.xpath('//div[@id="generalDesc"]').extract())
            details = re.sub('[[\']', '', details)
            details = re.sub('[]]', '', details)
            # detailsR = response.xpath('//div[@class="genaral-pic-desc"]/p/text()').extract()
            # if detailsR:            
            #     detailsRR = ' '.join([str(x) for x in detailsR])    #list换str
            #     detailsRRR = re.sub('[\r\n]', ' ', detailsRR)       #str 去\r\n
            #     details = detailsRRR.replace(" ", "")               #去空格
            
            phoneO = response.xpath('//p[@class="phone-num"]//text()').extract()
            if phoneO:
                phone = phoneO[0]
            
            contactInfoR = response.xpath('//span[@class="f14 c_333 jjrsay"]//text()').extract()
            if contactInfoR: 
                contactInfo =contactInfoR[0]
                contact_name = re.sub('[说]', '', contactInfo)
                contact_name = contact_name.replace(" ", "")
                if re.search(r'-', contact_name)
                    owner_type = "经纪人"
                else:
                    owner_type = "个人"            
            else:
                logger.info("V's Cannot get Conact in %s" % Rurl)
                contact_name = '王先生'
                owner_type = '个人'
                
            # allocation = response.xpath('//ul[@class="house-disposal"]/li/text()').extract()

            #位置图-----------------------
            NavBar = response.xpath('//span[@id="crumbs"]/a/text()').extract()
            if len(NavBar) >= 3:
                city3 = NavBar[1]
                position_city = re.findall(r'(^.*)58同城', city3)[0]
                if len(NavBar) >= 5:
                    city4 = NavBar[3]
                    position_district = re.findall(r'(^.*)二手房', city4)[0]
                    if len(NavBar) >= 7:
                        city5 = NavBar[5]
                        position_commercial_area = re.findall(r'(^.*)二手房', city5)[0]
            else:
                logger.info("V's NavBar issue in  %s" % Rurl)       
            
            #小区---------------------
            FList = {}
            position_detailrr = response.xpath('//ul[@class="house-basic-item3"]/li[1]//text()').extract()
            locationRR = response.xpath('//ul[@class="house-basic-item3"]/li[2]//text()').extract()
            if position_detailrr:            
                detailsRR = ' '.join([str(x) for x in position_detailrr])    
                detailsRRR = re.sub('[\r\n]', ' ', detailsRR)       
                XiaoquRR = detailsRRR.replace(" ", "")       
                XiaoquRRR = re.findall(r"：(.+?)$", XiaoquRR)[0]
                FList['小区'] = XiaoquRRR
            if locationRR:            
                detailsRR = ' '.join([str(x) for x in locationRR])    
                detailsRRR = re.sub('[\r\n]', ' ', detailsRR)       
                position_detail = detailsRRR.replace(" ", "")       
                position_detail = re.findall(r"－(.+?)$", position_detail)[0]
            #pack and list---------------------
            packs = response.xpath('//div[@class="general-item-wrap"]/ul//li')
            for i in range(0, len(packs)-11):
                name = packs[i].xpath("./span[1]/text()").extract_first()
                if re.search(r'房屋总价', name): #400万（单价105263元/㎡）
                    a1 = packs[i].xpath("./span[@class='c_000']/text()").extract_first().strip()
                    a11 = a1.replace(" ", "")
                    FList['房屋总价'] = a11
                    price = re.findall(r'(^.*)万',a11)    
                    price_unit = '万'
                if re.search(r'房屋户型', name): #1室1厅1卫
                    a2 = packs[i].xpath("./span[@class='c_000']/text()").extract_first().strip()                   
                    if a2:
                        FList['房屋户型'] = a2
                        list_pack['房屋户型'] = a2
                        if re.search(r'1室', room):
                            room = "整租一室"
                        elif re.search(r'2室', room):
                            room = "整租二室"
                        elif re.search(r'3室', room) or re.search(r'合租', room):
                            room = "整租三室"
                        elif re.search(r'4室', room):
                            room = "整租四室"
                        else:
                            room = "整租四室以上"      
                if re.search(r'房本面积', name): #'38㎡
                    a3 = packs[i].xpath("./span[@class='c_000']/text()").extract_first().strip()
                    FList['房屋户型'] = a3
                    list_pack['房屋户型'] = a3
                    acerage = a3
                if re.search(r'房屋朝向', name): #'南'
                    a4 = packs[i].xpath("./span[@class='c_000']/text()").extract_first().strip()
                    FList['房屋朝向'] = a4
                    list_pack['房屋朝向'] = a4
                if re.search(r'所在楼层', name): #'低层/共6层'
                    a5 = packs[i].xpath("./span[@class='c_000']/text()").extract_first().strip()
                    FList['房屋朝向'] = a5
                    list_pack['房屋朝向'] = a5
                if re.search(r'装修情况', name): #'精装修'
                    a6 = packs[i].xpath("./span[@class='c_000']/text()").extract_first().strip()   
                    FList['装修情况'] = a6
                if re.search(r'产权年限', name): #'70年'
                    a7 = packs[i].xpath("./span[@class='c_000']/text()").extract_first().strip()
                    FList['装修情况'] = a7
                if re.search(r'建筑年代', name): #'1986年'
                    a8 = packs[i].xpath("./span[@class='c_000']/text()").extract_first().strip()
                    FList['建筑年代'] = a8
                if re.search(r'房屋类型', name): #'普通住宅'
                    a9 = packs[i].xpath("./span[@class='c_000']/text()").extract_first().strip()   
                    FList['建筑年代'] = a9
                if re.search(r'交易权属', name): #'商品房'
                    b1 = packs[i].xpath("./span[@class='c_000']/text()").extract_first().strip()
                    FList['交易权属'] = b1
                if re.search(r'参考首付', name): #'120万（月供11481元/月）'
                    b2 = packs[i].xpath("./span[@class='c_000']/text()").extract_first().strip() 
                    b22 = b2.replace(" ", "")
                    FList['交易权属'] = b22                           
            if FList:
                list.append(FList)
        
    #写字楼 商铺 厂仓土车==================================================================================================
        if X1 or S1 or FKHT1:
            name = response.xpath('//div[@class="w headline"]/h1/text()')
            title = response.xpath('/html/head/title/text()')
            description = response.xpath('/html/head/meta[@name="description"]/@content')
            keywords = response.xpath('//span[@id="keyword"]/text()')            
            views = response.xpath('//em[@id="totalcount"]//text()')
            contact_name = response.xpath('//ul[@class="userinfo"]/li[2]/a/text()')
            owner_typeR = response.xpath('//em[@class="medium"]//text()')
            
            if name: 
                name = name.extract_first().strip()
            if title:
                title = title.extract_first().strip()
            if description:
                description =description.extract_first().strip()    
            if keywords:
                keywords = keywords.extract_first().strip()
            if views:
                views = views.extract_first().strip()
            if contact_name:
                contact_name = contact_name.extract_first().strip()
            if owner_typeR:
                owner_type = owner_typeR.extract_first().strip()            
            else:
                owner_type = '个人'
            
            #img alt
            imgsR = response.xpath('//div[@class="conleft"]/script[3]/text()')
            if imgsR:
                imgsR = imgsR.extract_first().strip()
                imgsRR = re.findall(r'\"(.*?)\"', imgsR)
            if imgsRR:
                imgs = imgsRR
            
            #refresh_at
            create_dataOrginalR = response.xpath('//div[contains(@class, "other")]/text()[1]')
            if create_dataOrginalR:
                    create_dataOrginalRR = create_dataOrginalR.extract_first().strip()
                if re.search(r'房源编号：', create_dataOrginalRR):
                    create_dataOrginalR = response.xpath('//div[contains(@class, "other")]/text()[2]')
                    create_dataOrginal = create_dataOrginalR.extract_first().strip() #发表时间: 2017-09-11
                    create_data = re.findall("：(.+?)$", create_dataOrginal) #匹配:到最后一位之间的
                    refresh_at = create_data[0]
                else:
                    create_data = re.findall("：(.+?)$", create_dataOrginalRR) #匹配:到最后一位之间的
                    refresh_at = create_data[0]
                    
            details = str(response.xpath('//div[@class="maincon"]').extract())
            details = re.sub('[[\']', '', details)
            details = re.sub('[]]', '', details)

            #phone 
            phoneURLOrginalCheck = response.xpath("//span[@id='t_phone']/script/text()").extract_first()
            PhoneNumberCheck = response.xpath("//span[@id='t_phone']//text()").extract_first()
            if phoneURLOrginalCheck:
                phoneURLOrginal = phoneURLOrginalCheck.strip()
                phone = re.findall('\'(.*?)\'',phoneURLOrginal)[0]
            elif PhoneNumberCheck:
                phone = PhoneNumberCheck.strip()    
            
        #写字楼---------------------------------------------
        if X1:
            info_item["category_second_id"] = xiezilou.category_second_id
            name = response.xpath('//div[@class="w headline"]/h1/text()')
            if name:
                name = name.extract_first().strip()
                category = re.findall(r'\((.*?)\)',name)[0] #出租
                # if category:
                #     category = category[0]
            #位置图--------------------
            NavBar = response.xpath('//span[@id="crumbs"]/a/text()').extract()
            if len(NavBar) >= 3:
                city3 = NavBar[2]
                position_city = re.findall(r'(^.*)写字楼', city3)[0]
                if len(NavBar) >= 4:
                    city4 = NavBar[3]
                    position_district = re.findall(r'(^.*)写字楼', city4)[0]
                    if len(NavBar) >= 5:
                        city5 = NavBar[4]
                        position_commercial_area = re.findall(r'(^.*)写字楼', city5)[0]
            else:
                logger.info("V's NavBar issue in  %s" % Rurl)
            
            #pack and list---------------------
            FList = {}
            packs = response.xpath('//ul[@class="info"]/li')
            for i in range(0, len(packs)):
                name = packs[i].xpath("./i/text()").extract_first()
                if re.search(r'区域：', name): #'长宁'
                    a1 = packs[i].xpath("./a/text()").extract_first().strip()
                    FList['区域'] = a1
                if re.search(r'楼盘：', name): #'凌空soho'
                    a2 = packs[i].xpath("./text()").extract_first().strip()
                    FList['楼盘'] = a2
                    list_pack['楼盘'] = a2                   
                if re.search(r'地段：', name): # '淞虹路地铁口附近 或 金钟路968号'
                    a3 = packs[i].xpath("./text()").extract_first().strip()
                    FList['地段'] = a3
                    position_detail = a3
                if re.search(r'类别：', name): #'写字楼（可注册公司）'
                    a4 = packs[i].xpath("./text()").extract()[1].strip()
                    if re.search(r'可注册公司', a4):
                        a4 = re.findall(r'(.*?)\（', a4)[0]
                    FList['类别'] = a4
                    list_pack['类别'] = a4 
                    rent_type_content = a4
                if re.search(r'面积：', name): #'620㎡'
                    a5 = packs[i].xpath("./text()").extract_first().strip()       
                    FList['面积'] = a5     
                    list_pack['面积'] = a5       
                    acerage = a5
                if re.search(r'价格：', name): # '4.8' '元/㎡/天'
                    price = packs[i].xpath("./em/text()").extract_first().strip()
                    FList['价格'] = price 
                    if price != '面议':                        
                        price_unitR = packs[i].xpath("./text()").extract()[2]
                        price_unit = re.sub('[\xa0\xa0\n]', ' ', price_unitR).replace(" ", "")
                        FList['价格'] = price + ' ' + price_unit
                    elif price == '面议':
                        price = -1
            if FList:
                list.append(FList)
    
        #商铺 ----------------------------------------------
        if S1:
            info_item["category_second_id"] = shangpu.shangpu_second_id
            name = response.xpath('//div[@class="w headline"]/h1/text()')
            if name:
                name = name.extract_first().strip()
                category = re.findall(r'\((.*?)\)',name)[0] #出租
                if re.search(r'转让', category):
                    info_item["category_second_id"] = shangpu.shengyi_second_id                
                
            #位置图--------------------
            NavBar = response.xpath('//span[@id="crumbs"]/a/text()').extract()
            if len(NavBar) >= 3:
                city3 = NavBar[2]
                position_city = re.findall(r'(^.*)商铺租售/生意转让', city3)[0]
                if len(NavBar) >= 4:
                    city4 = NavBar[3]
                    position_district = re.findall(r'(^.*)商铺租售/生意转让', city4)[0]
                    if len(NavBar) >= 5:
                        city5 = NavBar[4]
                        position_commercial_area = re.findall(r'(^.*)商铺租售/生意转让', city5)[0]
            else:
                logger.info("V's NavBar issue in  %s" % Rurl)

            #pack and list---------------------
            FList = {}
            packs = response.xpath('//ul[@class="info"]/li')
            for i in range(0, len(packs)):
                name = packs[i].xpath('.//text()').extract_first().strip()
                if re.search(r'区域：', name): #'长宁'
                    a1 = packs[i].xpath("./a/text()").extract_first().strip()
                    FList['区域'] = a1
                if re.search(r'临近：', name): #'商城路良友大厦'
                    a2 = re.findall(r"：(.+?)$",name)[0]
                    FList['临近'] = a2
                if re.search(r'地址', name): #'临近：地铁口 水产路'
                    a2b = re.findall(r"：(.+?)$",name)[0]
                    FList['地址'] = a2b
                    position_detail = a2b
                if re.search(r'历史经营', name): #'餐饮'
                    a2c = re.findall(r"：(.+?)$",name)[0]
                    FList['历史经营'] = a2c
                if re.search(r'行业：', name): #'家具店'
                    a2a = re.findall(r"：(.+?)$",name)[0]
                    FList['行业'] = a2a                
                if re.search(r'类型：', name): # '类型：商业街卖场'
                    a3 = re.findall(r"：(.+?)$",name)[0]
                    FList['类型'] = a3
                    list_pack['类型'] = a2                   
                if re.search(r'面积：', name): #'面积：25㎡'
                    a4 = re.findall(r'\d+',name)[0]       #25
                    a41 = re.findall(r"：(.+?)$",name)[0] #25㎡
                    FList['面积'] = a41 
                    list_pack['面积'] = a41                   
                    acerage = a4
                if re.search(r'租金：', name): #'5000' 出租有租金 生意转让有租金和转让费, 以转让费为price
                    a5 = packs[i].xpath("./em/text()").extract_first().strip()                     
                    if category != '转让':
                        price = a5  
                        if price != '面议':                        
                            price_unitR = packs[i].xpath("./text()").extract()[1]
                            price_unit = re.sub('[\xa0\xa0\n]', ' ', price_unitR).replace(" ", "")
                            FList['租金：'] = price + ' ' + price_unit
                        elif price == '面议':
                            price = -1  
                    elif category == '转让':
                        if a5 == '面议':
                            FList['租金：'] = '面议'
                        elif a5 != '转让':
                             price_unitR = packs[6].xpath("./text()").extract()[1]
                             price_unit = re.sub('[\xa0\xa0\n]', ' ', price_unitR).replace(" ", "")
                             FList['租金：'] = a5 + ' ' + price_unit
                if re.search(r'售价：', name): # '3' '万元'
                    a6 = packs[i].xpath("./em/text()").extract_first().strip() 
                    price = a6  
                    if price != '面议':                        
                        price_unitR = packs[i].xpath("./text()").extract()[1]
                        price_unit = re.sub('[\xa0\xa0\n]', ' ', price_unitR).replace(" ", "")
                        FList['售价'] = price + ' ' + price_unit
                    elif price == '面议':
                        price = -1           
                if re.search(r'转让费：', name): # '3' '万元'
                    a7 = packs[i].xpath("./em/text()").extract_first().strip() 
                    price = a7  
                    if price != '面议':                        
                        price_unitR = packs[i].xpath("./text()").extract()[1]
                        price_unit = re.sub('[\xa0\xa0\n]', ' ', price_unitR).replace(" ", "")
                        FList['转让费'] = price + ' ' + price_unit
                    elif price == '面议':
                        price = -1                                                
            if FList:
                list.append(FList)
        
        if FKHT1:
            # info_item["category_second_id"] = shangpu.shangpu_second_id
            name = response.xpath('//div[@class="w headline"]/h1/text()')
            if name:
                name = name.extract_first().strip()
                category = re.findall(r'\((.*?)\)',name)[0] #出租       
                
            #位置图--------------------
            NavBar = response.xpath('//span[@id="crumbs"]/a/text()').extract()
            if len(NavBar) >= 3:
                city3 = NavBar[2]
                position_city = re.findall(r'(^.*)厂房/仓库/土地/车位', city3)[0]
                if len(NavBar) >= 4:
                    city4 = NavBar[3]
                    position_district = re.findall(r'(^.*)厂房/仓库/土地/车位', city4)[0]
                    if len(NavBar) >= 5:
                        city5 = NavBar[4]
                        position_commercial_area = re.findall(r'(^.*)厂房/仓库/土地/车位', city5)[0]
            else:
                logger.info("V's NavBar issue in  %s" % Rurl)        
            
            #pack and list---------------------
            FList = {}
            packs = response.xpath('//ul[@class="info"]/li')
            for i in range(0, len(packs)):
                name = packs[i].xpath("./i/text()").extract_first()
                if re.search(r'区域：', name): #'长宁'
                    a1 = packs[i].xpath("./a/text()").extract_first().strip()
                    FList['区域'] = a1             
                if re.search(r'地段：', name): # '淞虹路地铁口附近 或 金钟路968号'
                    a3 = packs[i].xpath("./text()").extract_first().strip()
                    FList['地段'] = a3
                    position_detail = a3
                if re.search(r'类别：', name): #'仓库'
                    a4 = packs[i].xpath("./text()").extract()[1].strip()
                    FList['类别'] = a4
                    list_pack['类别'] = a4 
                    rent_type_content = a4
                    if re.search(r'仓库', a4):
                        info_item["category_second_id"] = changfang.cangku_second_id
                    elif re.search(r'土地', a4):    
                        info_item["category_second_id"] = changfang.tudi_second_id
                    elif re.search(r'车位', a4):    
                        info_item["category_second_id"] = changfang.cheku_second_id
                    elif re.search(r'厂房', a4):    
                        info_item["category_second_id"] = changfang.changfang_second_id
                    else:
                        info_item["category_second_id"] = changfang.qita_second_id                            
                if re.search(r'面积：', name): #'620㎡'
                    a5 = packs[i].xpath("./text()").extract_first().strip()       
                    FList['面积'] = a5     
                    list_pack['面积'] = a5       
                    acerage = a5
                if re.search(r'租金', name): # '4.8' '元/㎡/天'
                    price = packs[i].xpath("./em/text()").extract_first().strip()
                    FList['租金'] = price 
                    if price != '面议':                        
                        price_unitR = packs[i].xpath("./text()").extract()[2]
                        price_unit = re.sub('[\xa0\xa0\n]', ' ', price_unitR).replace(" ", "")
                        FList['租金'] = price + ' ' + price_unit
                    elif price == '面议':
                        price = -1
            if FList:
                list.append(FList)
            
    #TOGETHER=================================================================================================================           
        if category:
            info_item["category"] = category
        #查询条件：
        if list_pack:
            info_item["list_item_pack"] = list_pack
        #供求
        if house_type:
            info_item["house_type"] = house_type
        if rent_mode:
            info_item["rent_mode"] = rent_mode
        #面积
        if acerage:
            info_item["acerage"] = acerage
        #类型
        if rent_type_content:
            info_item["type"] = rent_type_content
        #几室
        if room:
            info_item["room"] = room
        #价格
        if price:
            info_item["price"] = price
        #pack
        if list:
            info_item["pack"] = list
        #价格单位：
        if price_unit:
            info_item["price_unit"] = price_unit
        #封面名
        info_item["name"] = name
        #标题
        info_item["title"]  = title
        #关键字
        if keywords:
            info_item["keywords"] = keywords
        #简介
        info_item["description"] = description
        # 详情图片地址
        if imgs:
            info_item["imgs"] = img_urls
        #url
        info_item["url"] = Rurl
        #详情
        if details:
            info_item["details"] = details
        #创建日期
        info_item["refresh_at"] = refresh_at
        #浏览次数
        if view:
            info_item["views"] = views
        #城市
        info_item["position_city"] = position_city
        #区
        if position_district:
            info_item["position_district"] = position_district
        #商圈
        if position_commercial_area:
            info_item["position_commercial_area"] = position_commercial_area
        #具体位置
        if position_detail:
            info_item["position_detail"] = position_detail
        #电话号码
        if phone:
            info_item["phone"] = phone
        #联系人
        info_item["contact_name"] = contact_name
        #持有人类型
        info_item["owner_type"] = owner_type
        # types = response.xpath(common.owner_xpath).extract_first("")
        # if types:
        #     if re.match(".*\((.*)\)", types):
        #         info_item["owner_type"] = re.match(".*\((.*)\)", types).group(1)
        
        #配置
        # allocation = response.xpath(common.allocation_xpath).extract()
        # if allocation:
        if allocation:
            info_item["allocation"] = allocation
        # try:
        oitem = {}
        oitem["categorySecondId"] = info_item["category_second_id"]
        oitem["url"] = Rurl
        r_data = requests.get("http://123.207.237.172/common/build/dataId", params=oitem)
        r = r_data.text
        print(r)
        r = json.loads(r)
        print(r)
        for i in r.keys():
            if i == "resCode" and r[i] == "0":
                print("success")
            elif i == "data":
                info_item["data_id"] = r[i]
        # except Exception as e:
        #     print(e)
        yield info_item    
            


        
    #Error===================================================================================================================

    def errback_httpbin(self, failure):
        self.logger.error(repr(failure))
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("V's Occur HttpError on %s", response.url)
        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error("V's Occur DNSLookupError on %s", request.url)
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error("V's Occur TimeoutError on %s", request.url)
#========================================================================================================================
