# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from pymongo import MongoClient
import requests
import json
from  util_data import util_data
import re

city_table = util_data.get_position_city_id_table()
district_table = util_data.get_position_district_id_table()
commercial_area_table = util_data.get_position_commercial_area_id_table()

sub_table = util_data.get_subclass_table()
map_table = util_data.get_query_map_table()
table = util_data.get_query_item_table()


class PostTerms(object):

    def process_item(self, item, spider):
        ut_data = util_data()
        try:
            index_terms ={}
            if item["data_id"]:
                index_terms["dataId"] = item["data_id"]
                index_terms["status"] = 0
                index_terms["dataSourceId"] = 2

            position_terms = {}
            if item["position_city"]:
                position_terms["dataId"] = item["data_id"]
                city_id = ut_data.from_table_get_city_id(item["position_city"],city_table)
                position_terms["positionCityId"] = city_id
                if item["position_district"]:
                    district_id = ut_data.from_table_get_district_id(city_id,item["position_district"],district_table )
                    position_terms["positionDistrictId"] = district_id
                    if item["position_commercial_area"] :
                        commercial_area_id = ut_data.from_table_get_commercial_area_id(district_id,item["position_commercial_area"],
                                                                                     commercial_area_table)
                        position_terms["positionCommercialAreaId"] = commercial_area_id
            if item["position_detail"]:
                position_terms["positionDetail"] = item["position_detail"]
            if "latitude" in item:
                position_terms["latitude"] = "0"
            if "longitude" in item:
                position_terms["longitude"] = "0"

            allocation_terms = {}
            if "allocation" in item:
                if item["allocation"]:
                    allocation_terms["allocation"] = item["allocation"]
                    allocation_terms["dataId"] = item["data_id"]

            contact_terms  ={}
            if item["phone"]:
                contact_terms["dataId"] = item["data_id"]
                contact_terms["contactPhone"] = item["phone"]

                if item["contact_name"]:
                    contact_terms["contactName"] = item["contact_name"]

                if "owner_type" in item:
                    if item["owner_type"] == "经纪人":
                        contact_terms["contactRole"] = 2
                    elif item["owner_type"] == "个人":
                        contact_terms["contactRole"] = 1
                else:
                    contact_terms["contactRole"] = 1

            category_terms = {}
            if item["category_second_id"]:
                category_terms["dataId"] = item["data_id"]
                category_terms["categoryFirstId"] = "10"
                if "category" in item:
                    if item["category"]:
                        parent_category_id = util_data.get_subclass_id(int(item["category_second_id"]),item["category"],sub_table)
                    else:
                        parent_category_id = item["category_second_id"]
                else:
                    parent_category_id = item["category_second_id"]
                category_terms["parentCategoryId"] = parent_category_id

            general_terms ={}
            if item["name"]:
                general_terms["name"] = item["name"]
                if "data_id" in item:
                    general_terms["dataId"] = item["data_id"]
                if "title" in item:
                    general_terms["title"] = item["title"]
                if "description" in item:
                    general_terms["description"] = item["description"]
                if "keywords" in item:
                    general_terms["keywords"] = item["keywords"]
                if "refresh_at" in item:
                    general_terms["refreshAt"] = item["refresh_at"]
                if "price" in item:
                    general_terms["price"] = item["price"]
                if "price_unit" in item:
                    general_terms["priceUnit"] = item["price_unit"]
                if "list_item_pack" in item:
                    general_terms["listItemPack"] = item["list_item_pack"]

            pack_terms  = {}
            if "pack" in item:
                if item["pack"]:
                    pack_terms["pack"] = json.dumps(item["pack"],ensure_ascii=False)
                    pack_terms["dataId"] = item["data_id"]

            imgs_terms = {}
            if "imgs" in item:
                if item["imgs"]:
                    imgs_terms["url"] = item["imgs"]
                    if "data_id" in item:
                        imgs_terms["dataId"] = item["data_id"]
                    if "alt" in item:
                        imgs_terms["alt"] = item["alt"]

            details_terms ={}
            if "details" in item:
                if item["details"]:
                    details_terms["details"] = item["details"]
                    details_terms["dataId"] = item["data_id"]

            # url_terms= {}
            # url_terms["url"] = item["url"]
            query_terms = {}
            # if item["category_second_id"] = '1010':
            parent_category_id = int(parent_category_id)
            citem = util_data.get_query_items(parent_category_id,map_table)
            for i in citem.keys():
                if citem[i] =="room_id":
                    if "room" in item:
                        if item["room"]:
                            if util_data.get_type_id(i,item["room"],table):
                                query_terms["roomId"] = util_data.get_type_id(i,item["room"],table)
                elif citem[i] =="rent_range_id":
                    if "price" in item:
                        if int(item["price"])>=0:
                            if util_data.get_range_id(i,int(item["price"]),table):
                                query_terms["rentRangeId"] = util_data.get_range_id(i,int(item["price"]),table)
                elif citem[i] =="total_price_id":
                    if "price" in item:
                        if int(item["price"])>=0:
                            if util_data.get_range_id(i,int(item["price"]),table):
                                query_terms["totalPriceId"] = util_data.get_range_id(i,int(item["price"]),table)
                elif citem[i] =="area_id":
                    if "acerage" in item:
                        if item["acerage"]:
                            if re.search(r'\d+',item["acerage"]):
                                acerage = int(re.search(r'\d+',item["acerage"]).group())
                                if util_data.get_range_id(i,acerage,table):
                                    query_terms["areaId"] = util_data.get_range_id(i,acerage,table)
                elif citem[i] =="rent_mode_id":
                    if "rent_mode" in item:
                        if item["rent_mode"]:
                            if util_data.get_type_id(i,item["rent_mode"],table):
                                query_terms["rentModeId"] = util_data.get_type_id(i,item["rent_mode"],table)
                elif citem[i] =="house_type_id":
                    if "house_type" in item:
                        if item["house_type"]:
                            if util_data.get_type_id(i,item["house_type"],table):
                                query_terms["houseTypeId"] = util_data.get_type_id(i,item["house_type"],table)
                elif citem[i] =="type_id":
                    if "type" in item:
                        if item["type"]:
                            if util_data.get_type_id(i,item["type"],table):
                                query_terms["typeId"] = util_data.get_type_id(i,item["type"],table)
                elif citem[i] =="trade_id":
                    if "trade" in item:
                        if item["trade"]:
                            if util_data.get_type_id(i,item["trade"],table):
                                query_terms["tradeId"] = util_data.get_type_id(i,item["trade"],table)


            oitem ={}
            oitem["url"] = item["url"]
            if index_terms:
                oitem["dataIndex"] =json.dumps(index_terms)
            if position_terms:
                oitem["dataPosition"] = json.dumps(position_terms)
            if allocation_terms:
                oitem["dataAllocation"] = json.dumps(allocation_terms)
            if contact_terms:
                oitem["dataContact"] = json.dumps(contact_terms)

            oitem["dataCategory"] = json.dumps(category_terms)
            oitem["dataGeneral"] = json.dumps(general_terms)
            if pack_terms:
                oitem["dataPack"] = json.dumps(pack_terms)
            if imgs_terms:
                oitem["dataPictures"] =json.dumps(imgs_terms)
            if details_terms:
                oitem["dataDetails"] =json.dumps(details_terms)
            if query_terms:
                query_terms["dataId"]  = item["data_id"]
                oitem["dataQueryItems"] =json.dumps(query_terms)
            # oitem = json.dumps(oitem)
            r_data = requests.post("http://123.207.237.172/fangchan/spider/create/cover", data=oitem)
            print(r_data.text)
        except Exception as e:
            print(e)
        return item



#123.207.237.172
#10.2.200.21