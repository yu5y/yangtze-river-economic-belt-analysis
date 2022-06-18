# -*- coding: utf-8 -*-
from typing import Dict
import requests #导入请求模块
import json #导入json模块
import time #导入时间模块
import xlrd
import xlwt
import pandas as pd
from ChineseAdminiDivisionsDict import YangtzeRiverCode,YangtzeRiverCodeTest



def date2str(date,date_formate = "%Y%m%d"):
    str = date.strftime(date_formate)
    return str

def migration_index(FileTittle,classname,direction,CodeDict): #CodeDict字典里所有城市的迁徙规模指数，以全国列表形式列出
  
   #################写入行头各城市代码及其城市名###############
    if direction == 'in' :
        nameofdire = '迁入'
    if direction == 'out':
        nameofdire = '迁出'
   ########################开始抓取数据##############################
 
    df_value = pd.DataFrame(index=[])
    city = []


    for Area , Code in CodeDict.items():
        
        url=f'http://huiyan.baidu.com/migration/historycurve.jsonp?dt={classname}&id={Code}&type=move_{direction}'
        print(f'{Area}:{url}')
        response=requests.get(url, timeout=10) # #发出请求并json化处理
        time.sleep(5)  #挂起五秒
        r=response.text[4:-1] #去头去尾
        data_dict=json.loads(r) #字典化
        if data_dict['errmsg']=='SUCCESS':
           
            city.append(Area)
            data_list=data_dict['data']['list']         
            size = df_value.index.size

            if size == 0:#如果df为空则新建列
                df_value = pd.DataFrame([data_list])
            else:
                
                add_data = pd.Series(data_list)
                # ignore_index=True不能少
                df_value = df_value.append(add_data, ignore_index=True)                              
        else:
            print('错误')

    df_value.insert(0,"city",pd.Series(city))
    df_value.to_csv(f'{FileTittle} {nameofdire}规模指数.csv')



if __name__=="__main__":
     # migration_index('全国','country','in',ProvinceCode)
    migration_index('全国','city','out',YangtzeRiverCode)
    print('全部完成')


