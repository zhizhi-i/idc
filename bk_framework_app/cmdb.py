# -*- coding: utf-8 -*-
import traceback
import requests
import json
from blueapps.utils.logger import logger
from blueapps.account.decorators import login_exempt
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http.response import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator


# 根据前端参数信息生成对应的查询请求体
def generate_query_conditions(data):

    query_conditions = {
        "condition": "AND",
        "rules": []
    }
    
    for field, value in data.items():
        if str(value).strip():
            rule = {
                "field": field,
                "operator": "equal",
                "value": value
            }
            query_conditions["rules"].append(rule)
    
    return query_conditions


class SearchCmdbIns(object):
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
            logger.error("CMDB接口调用失败：{}".format(traceback.format_exc()))
            return {'result':False, 'error':'请求错误','message': str(e)}  # 返回带有异常信息的字典
        except Exception as e:
            logger.error("CMDB接口调用失败：{}".format(traceback.format_exc()))
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



    @method_decorator(require_http_methods(["POST"]))
    @login_exempt
    @csrf_exempt
    def get_ins_by_condition(self,request):
        front_body = json.loads(request.body)
        logger.info(f"front_end_request_body:{front_body}")
        obj_id = front_body["obj_id"]
        all_data = []
        obj_count = self.get_obj_ins_count(obj_id)
        logger.info(f"本次查询:{obj_id}:{obj_count}")
        start = 0
        limit = 100
        conditions = generate_query_conditions(front_body["conditions"])
        logger.info(f"格式转化后的条件结构:{conditions}")

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
                **({"conditions": conditions} if conditions.get('rules', []) else {}) # 当前格式化之后的conditions为空时，则删除请求体中的conditions
            }

            logger.info(f"完整接口请求体:{data}")

            res = self._request(url="/api/c/compapi/v2/cc/search_object_instances/",method="post",data=data)

            logger.info(f"本次请求接口返回结果:{res}")
            
            info = res.get("data", {}).get("info", [])

            info = info if info is not None else []

            all_data.extend(info)

            start += limit
            if start > obj_count:
                break

        return JsonResponse({"info": all_data}) # 返回根据条件查询出来的全部数据
