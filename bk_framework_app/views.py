# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.shortcuts import render
from django.http import JsonResponse
from blueking.component.shortcuts import get_client_by_request


# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt
def home(request):
    """
    首页
    """
    return render(request, "index.html")


def dev_guide(request):
    """
    开发指引
    """
    return render(request, "bk_framework_app/dev_guide.html")


def contact(request):
    """
    联系页
    """
    return render(request, "bk_framework_app/contact.html")


def hello(request):
    return JsonResponse({"hello": "world"})


def get_obj_ins_count(request):
    data = {
        "bk_app_code": "bk_sops",
        "bk_app_secret": "0CR79bvYKkZ651T01tyZuz4nc9QF7e6ykWir",
        "bk_username": "admin",
        "bk_obj_id": "IDC_Deliver"
    }
    client = get_client_by_request(request)
    resp = client.cc.count_object_instances(data)

    return JsonResponse(resp)