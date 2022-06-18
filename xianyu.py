# -*- coding: utf-8 -*-
from turtle import onkey
import requests
import json
import time
import pandas as pd
from ChineseAdminiDivisionsDict import CitiesCode, ProvinceCode

def date2str(date,date_formate = "%Y%m%d"):
    str = date.strftime(date_formate)
    return str


def migration_all_date(areaname,classname,no,direction): #定义生成不同时期，不同城市，不同迁徙方向
    if no == -1 :
        no = CitiesCode[str(areaname)]
   
    #################写入行头各城市代码及其城市名###############
    if direction == 'in' :
        nameofdire = '迁入来源地'
    if direction == 'out':
        nameofdire = '迁出目的地'
   
    ########################设定日期##############################
    datelist = []                                    #日期列表

    #日期计数器
    day = pd.date_range(start='20200101',end='20220531')      # 给定日期
    for d in day:
        datelist.append(date2str(d))
    
    df_value = pd.DataFrame(index=[])

    for date in datelist:                           #遍历所有日期
        time.sleep(1)
        url=f'http://huiyan.baidu.com/migration/cityrank.jsonp?dt={classname}&id={no}&type=move_{direction}&date={date}'  #若是城市级别url则换成cityrank
        print(url)
        response=requests.get(url, timeout=10) #发出请求并json化处理
        time.sleep(3)
        r=response.text[4:-1] #去头去尾
        data_dict=json.loads(r) #字典化

        if data_dict['errmsg']=='SUCCESS':
            data_list=data_dict['data']['list']
            time.sleep(2)
            ################写入###############
            if len(data_list)>0:
                size = df_value.index.size
                #第一次新建dataframe
                if  size == 0:
                    cityratio = {}
                    for i in range (len(data_list)):
                        city_name=data_list[i]['city_name'] #取出城市名
                        value=data_list[i]['value']#取出迁徙比例
                        cityratio[city_name] = value
                    df_value = pd.DataFrame.from_dict(cityratio, orient='index', columns=[date]).reset_index().rename(columns={'index':'city'})
                else:
                #后续采用两个df合并，out方式，查找同名city，放在一行
                    cityratio = {}
                    for i in range (len(data_list)):
                        city_name=data_list[i]['city_name'] #取出城市名
                        value=data_list[i]['value']#取出迁徙比例
                        cityratio[city_name] = value
                    df_value = pd.merge(df_value,pd.DataFrame.from_dict(cityratio, orient='index', columns=[date]).reset_index().rename(columns={'index':'city'}),on='city',how='outer')
        
    df_value.to_csv(f"alldata//{areaname}-{nameofdire}.csv")      #保存


def circu_exe_direction(areaname,classname,no):
    mukous = ['in','out']
    for mukou in mukous:
        migration_all_date(areaname,classname,no,mukou)
    print(str(areaname)+'---','完成')


if __name__=="__main__":
    df  = pd.read_csv("areacode.csv")
    for index,p in df.iterrows():
        areaname = p["cityname"]
        circu_exe_direction(areaname,'city',-1)
