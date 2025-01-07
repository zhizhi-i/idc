# -*- coding: utf-8 -*-
import traceback
import requests
import json
from blueapps.utils.logger import logger
from blueapps.account.decorators import login_exempt
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
import re
from collections import Counter

class SearchCabinet(object):
    #生产环境从环境变量中获取，开发环境写死
    host = "http://bkapi.blueking.megaspeed-tech.ai"
    app_code = "bk_sops"
    app_search = "0CR79bvYKkZ651T01tyZuz4nc9QF7e6ykWir"

    def __init__(self):
        pass

    def _request(self, url, method='GET', data=None, params=None):
        try:
            response = requests.request(method, self.host + url, json=data, params=params, verify=False)
            response.raise_for_status()  # 如果响应状态码不是200，将抛出HTTPError异常
            return response.json() # 返回响应体的json格式化后的字典
        except requests.RequestException as e:
            return {'result':False, 'error':'请求错误','message': str(e)}  # 返回带有异常信息的字典
        except Exception as e:
            return {'result':False, 'error':'未知错误','message': str(e)}  # 返回带有异常信息的字典


    def get_obj_ins_count(self,obj_id):
        data = {
            "bk_app_code": "bk_sops",
            "bk_app_secret": "0CR79bvYKkZ651T01tyZuz4nc9QF7e6ykWir",
            "bk_username": "admin",
            "bk_obj_id": obj_id
        }
        res = self._request(url="/api/c/compapi/v2/cc/count_object_instances/",method="post",data=data)
        return res["data"].get("count",0) # 返回查询到的实例总数


    def penrcentage_of_data(self,obj_id,field):
        all_data = []
        obj_count = self.get_obj_ins_count(obj_id)
        start = 0
        limit = 500
        while True:
            data = {
                "bk_app_code": self.app_code,
                "bk_app_secret": self.app_search,
                "bk_username": "admin",
                "bk_obj_id": obj_id,
                "page": {
                    "start": start,
                    "limit": limit
                },
                "fields": [field]
            }
            res = self._request(url="/api/c/compapi/v2/cc/search_object_instances/",method="post",data=data)
            info = res.get("data", {}).get("info", [])
            info = info if info is not None else []
            all_data.extend(info)

            start += limit
            if start > obj_count:
                break

        field_data = [item[field] for item in all_data]
        field_list = list(set(field_data)) # 返回不同的字段列表['马来BDC-B7', '马来BDC-B1', '马来BDC-B2', '马来GDS']
        field_count = dict(Counter(field_data)) # 返回相同字段对应的数量{'马来GDS': 1219, '马来BDC-B1': 780, '马来BDC-B2': 1480, '马来BDC-B7': 550}
        series = []
        for item in field_list:
            state_data = {
                "name": item,
                "value": field_count.get(item,0) 
            }
            series.append(state_data)

        return series

    @method_decorator(require_http_methods(["GET"]))
    @login_exempt
    def get_machine_room(self, request): # 机柜分布
        return JsonResponse({
            "code":0,
            "result": True,
            "messge":"success",
            "data": {
                "title": "机房机柜分布",
                "series": self.penrcentage_of_data("cabinet","machine_room")
            }   
        })

    @method_decorator(require_http_methods(["GET"]))
    @login_exempt
    def get_cabinet_state(self, request): # 加电情况
        data = self.penrcentage_of_data("cabinet","power_state")
        for item in data:
            if item['name'] == '2':
                item['name'] = 'ON'
            elif item['name'] == '1':
                item['name'] = 'OFF'
        
        return JsonResponse({
            "code":0,
            "result": True,
            "messge":"success",
            "data": {
                "title": "机柜加电情况",
                "series": data
            }   
        })

    @method_decorator(require_http_methods(["GET"]))
    @login_exempt
    def get_life_cycle(self, request): # 投产情况
        data = self.penrcentage_of_data("cabinet","life_cycle")
        for item in data:
            if item['name'] == '6':
                item['name'] = '待使用'
            elif item['name'] == '5':
                item['name'] = '已投产'

        return JsonResponse({
            "code":0,
            "result": True,
            "messge":"success",
            "data": {
                "title": "机柜投产情况",
                "series": data
            }   
        })
    
    @method_decorator(require_http_methods(["GET"]))
    @login_exempt
    def get_power_date(self, request): # 柱状图数据源
        data = self.penrcentage_of_data("cabinet","power_date")
        years = [0] * 12  # 创建一个包含12个0的列表，表示12个月份

        for item in data:
            if item.get("name"):
                match = re.search(r"-([0-9]{2})-", item["name"])  # 匹配类似"-01-"这样的月份部分
                if match:
                    month = int(match.group(1))  # 提取月份数字
                    if 1 <= month <= 12:
                        years[month - 1] += item["value"]
            
        return JsonResponse({
            "code": 0,
            "result": True,
            "messge": "success",
            "data":{
                "series":[{
                    "name": "2024年机柜投产数量",            
                    "data": years
                }],
                "categories": ["1月","2月","3月","4月","5月","6月","7月","8月","9月","10月","11月","12月"]
            }
        })
    
    @method_decorator(require_http_methods(["GET"]))
    @login_exempt
    def get_power_date_z(self, request): # 折线图数据源
        data = self.penrcentage_of_data("cabinet","power_date")
        years = [0] * 12  # 创建一个包含12个0的列表，表示12个月份

        for item in data:
            if item.get("name"):
                match = re.search(r"-([0-9]{2})-", item["name"])  # 匹配类似"-01-"这样的月份部分
                if match:
                    month = int(match.group(1))  # 提取月份数字
                    if 1 <= month <= 12:
                        years[month - 1] += item["value"]
            
        return JsonResponse({
            "code":0,
            "result": True,
            "messge":"success",
            "data":{
                "xAxis":["1月","2月","3月","4月","5月","6月","7月","8月","9月","10月","11月","12月"],
                "series" : [
                    {
                        "name": "机柜投产",
                        "type": "line",
                        "data": years
                    }
                ]
            }
        })