import pandas as  pd
import networkx as nx
from os import  walk
from chinese_calendar import is_workday
import datetime


def flowPopulation(xlsfile):
   
    movein_data = pd.read_excel(xlsfile)
    city = movein_data.iloc[:,1:2]
    data = movein_data.iloc[:,2:]/3.24*100000
    movein_population = pd.concat([city,data],axis=1)
    
    return movein_population


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

def date2str(date,date_formate = "%Y%m%d"):
    str = date.strftime(date_formate)
    return str

def makegraph():
    move_out_data = flowPopulation('全国 迁出规模指数.xls')
    move_in_data = flowPopulation('全国 迁入规模指数.xls')
    

    weekday,weekend = splitDate('20210915','20211115')
    weekdaystr,weekendstr = splitDatestr('20210915','20211115')
    weekday.remove(20210930)
    weekday.remove(20211115)

    weekdaystr.remove('20210930')
    weekdaystr.remove('20211115')
    
    citynames = move_out_data['城市']
    weekdaypop = pd.concat([citynames,move_out_data[weekday]],axis=1)


    G = nx.Graph()

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
                G.add_node(city)
                G.add_node(dest)
                weight =  city_pop_df.loc[city_pop_df['迁出目的地']==dest].loc[:,'均值'].values[0] 

                if weight > 0:
                    G.add_edge(city,dest)
                    G.edges[city,dest]['weight'] = weight

    nx.write_gexf(G,'全国迁出网络.gexf')
    

if __name__ == "__main__":
    
   
   makegraph()
    
    
    