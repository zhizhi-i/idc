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

from django.urls import re_path
from . import views
from .cmdb import SearchCmdbIns
from .cabinet import SearchCabinet


urlpatterns = (
    re_path(r"^$", views.home),
    re_path(r"^dev-guide/$", views.dev_guide),
    re_path(r"^contact/$", views.contact),
    re_path(r'^hello/$', views.hello),
    re_path(r'^home', views.home),
    re_path(r'^api/cmdb/get_ins_by_condition$', SearchCmdbIns().get_ins_by_condition),
    re_path(r'^api/cmdb/get_machine_room$', SearchCabinet().get_machine_room),
    re_path(r'^api/cmdb/get_cabinet_state$', SearchCabinet().get_cabinet_state),
    re_path(r'^api/cmdb/get_life_cycle$', SearchCabinet().get_life_cycle),
    re_path(r'^api/cmdb/get_power_date$', SearchCabinet().get_power_date),
    re_path(r'^api/cmdb/get_power_date_z$', SearchCabinet().get_power_date_z)
)
