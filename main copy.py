from tarfile import ENCODING
from anyio import CapacityLimiter
import pandas as  pd
from pandas import DataFrame
import networkx as nx
from os import  walk
from chinese_calendar import is_workday
import datetime
import pypinyin as ppy
from sklearn.metrics import SCORERS
from sqlalchemy import null

#百度规模转换为迁徙人数
def flowPopulation(file):
   
    movein_data = pd.read_csv(file)
    city = movein_data.iloc[:,0:1]
    data = movein_data.iloc[:,1:]/3.24*100000
    movein_population = pd.concat([city,data],axis=1)
    
    return movein_population

#生成查询日期数字
def splitDate(startdatem,enddate):

    day = pd.date_range(start='20210915',end='20211115')      # 从元旦开始的连续40天
    weekday = []   # 工作日
    weekend = []   # 休息日
    for date in day:
        if is_workday(date):
            weekday.append(int(date2str(date)))
        else:
            weekend.append(int(date2str(date)))
    return weekday,weekend

#生成查询日期字符串
def splitDatestr(startdatem,enddate):

    day = pd.date_range(start='20210915',end='20211115')      # 从元旦开始的连续40天
    weekday = []   # 工作日
    weekend = []   # 休息日
    for date in day:
        if is_workday(date):
            weekday.append(date2str(date))
        else:
            weekend.append(date2str(date))
    return weekday,weekend

#日期转字符串
def date2str(date,date_formate = "%Y%m%d"):
    str = date.strftime(date_formate)
    return str


#城市转换
def cityFilterbyname (filterfile):
    df  = pd.read_csv(filterfile)
    Cityfilter = []
    for index,p in df.iterrows():
        Cityfilter.append(p["cityname"])
    
    
    #walk会返回3个参数，分别是路径，目录list，文件list，你可以按需修改下
    for f, _, i in walk('D:\code\长江经济带数据分析\全国'):
        for j in i:
            df2 =  pd.read_excel(f + '/' + j)
            if '迁入来源地' in df2.columns:
                df3 = df2[df2['迁入来源地'].isin(Cityfilter)]#判断过滤
                filename = j.split('.')[0]
                df3.to_csv("D://code//长江经济带数据分析//data//"+filename+".csv")#保存
            elif '迁出目的地' in df2.columns:
                df3 = df2[df2['迁出目的地'].isin(Cityfilter)]
                filename = j.split('.')[0]
                df3.to_csv("D://code//长江经济带数据分析//data//"+filename+".csv")#保存

def pinyin(word):
    s = ''
    for i in ppy.pinyin(word, style=ppy.NORMAL):
        s += ''.join(i)
    return s


#生成图
def makegraph():
    move_out_data = flowPopulation('全国 迁出规模指数.csv')
    #move_in_data = flowPopulation('全国 迁入规模指数.csv')
    

    weekday,weekend = splitDate('20210915','20211115')
    weekdaystr,weekendstr = splitDatestr('20210915','20211115')
    weekday.remove(20210930)
    weekday.remove(20211115)

    weekdaystr.remove('20210930')
    weekdaystr.remove('20211115')
    
    citynames = move_out_data['城市']
    weekdaypop = pd.concat([citynames,move_out_data[weekday]],axis=1)


    G = nx.DiGraph()
    
    
    
    df3 =  pd.read_csv('region.csv')
    for city in df3['区划名称']:
        
        lng = df3.loc[df3['区划名称'] == city]['经度'].values[0]
        lat = df3.loc[df3['区划名称'] == city]['纬度'].values[0]
    
        
        #G.add_node(city, name = str(city).encode('utf-8').decode('iso-8859-1'),Wkt='POINT (' + str(lng) + ' ' + str(lat) + ')',x =str(lng),y=str(lat)) 
        G.add_node(city,id =df3.loc[df3['区划名称'] == city].index[0]+1, Label = str(city),x=lng,y=lat) 

     

    for city in citynames:
        df =  pd.read_csv('data//'+city+"-迁出目的地.csv").dropna(axis=1)#特定城市迁出比例
        df2 = pd.DataFrame()
        citypop = weekdaypop[(weekdaypop['城市'] == city)].iloc[:,1:] #工作日城市迁出人口数量
        propotion_df = df.iloc[:,3:][weekdaystr] #工作日迁出到各城市的比例
        for  col in citypop.columns:
            df2[col] = citypop[col].iloc[0]* propotion_df[str(col)]/100     
              
        city_pop_df = pd.concat([df.iloc[:,1:3],df2],axis=1) #工作日各城市迁出人数
        city_pop_df['均值'] = city_pop_df.iloc[:,2:].apply(lambda x:x.mean(),axis =1)
        
        for dest in city_pop_df['迁出目的地']:
            if city != dest:
              
                
                weight =  city_pop_df.loc[city_pop_df['迁出目的地'] == dest].loc[:,'均值'].values[0] 

                if weight > 0:
                    #oriid =df3.loc[df3['区划名称'] == city].index[0]+1
                    #destid = df3.loc[df3['区划名称'] == dest].index[0]+1
                    
                    #x1 = G.nodes[oriid]['x']
                    #y1 = G.nodes[oriid]['y']
                    #x2 = G.nodes[destid]['x']
                    #y2 = G.nodes[destid]['y']
                    #line = 'LINESTRING  (' + str(x1) + ' ' + str(y1)+ ',' + str(x2) + ' ' + str(y2)  + ')'
                    
                   
                    
                    G.add_edge(city,dest)
                    G.edges[city,dest]['weight'] = float(weight)
                    #G.edges[city,dest]['Wkt'] = line
            else:
                weight = 0        

    nx.write_gexf(G,'全国迁出网络.gexf')
    #nx.write_pajek(G,'全国迁出网络3.net')
    
    #topNBetweeness(G)
    #topNBetweeness_degree(G)
    #nx.write_shp(G,'全国迁出网络.shp')
    
    
# 计算网络中的节点的介数中心性，并进行排序输出
def topNBetweeness(G):
    score = nx.betweenness_centrality(G)
    score = sorted(score.items(), key=lambda item:item[1], reverse = True)
    output = []
    df = pd.DataFrame(columns=('city','weight'))
    index = 0
    for node in score:
        df.append({'city':node[0],'weight':node[1]})

        
        output.append(node[0])        
    print(df)
 
    fout = open("betweennessSorted.data", 'w')
    for target in output:
        fout.write(str(target)+" ")

# 计算网络中的节点的介数中心性，并进行排序输出
def topNBetweeness_degree(G):
    score = nx.in_degree_centrality(G)
    score = sorted(score.items(), key=lambda item:item[1], reverse = True)
    print("degree_centrality: ", score)
    output = []
    for node in score:
        output.append(node[0])
 
    print(output)  
    fout = open("degreecentralitySorted.data", 'w')
    for target in output:
        fout.write(str(target)+" ")

    

if __name__ == "__main__":
    
   
   #makegraph()
   G = nx.read_gexf('全国迁出网络.gexf')
   topNBetweeness(G)
   topNBetweeness_degree(G)
    
    
    