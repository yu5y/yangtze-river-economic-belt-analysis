from operator import index
import pandas as pd
import matplotlib 
import matplotlib.cm as cm
import numpy as np
import math
import numpy as np

from matplotlib import  pyplot as plt


def load_csv():

    df_in = pd.read_csv('全国迁出规模指数.csv',index_col= ['city'])
    df_in_re = df_in.drop(columns = ['Unnamed: 0'])
    df_out = pd.read_csv('全国迁入规模指数.csv',index_col = ['city'])
    df_out_re = df_out.drop(columns = ['Unnamed: 0'])
    df = df_in_re - df_out_re
    
    return df_in_re,df_out_re,df


def aggregate(df):
    data = pd.Series(pd.to_datetime(df.index))
    data_year = data.dt.year
    data_month = data.dt.month
    data_day = data.dt.day
    
    df['year'] = data_year.values
    df['month'] = data_month.values   
    df['day'] = data_day.values
    return  df
    
def pltIndex(df,expert_path):
    day_statics = df.groupby(['year','month','day']).sum()
    month_statics = df.groupby(['year','month']).mean()
    year_statics = df.groupby(['year']).mean()
    
    plt.figure(figsize=(40,20),dpi=80)

    _x=year_statics.columns.drop('month').drop('day')
    _y_2019=year_statics.loc[2019].drop('month').drop('day').values
    _y_2020=year_statics.loc[2020].drop('month').drop('day').values
    _y_2021=year_statics.loc[2021].drop('month').drop('day').values
    _y_2022=year_statics.loc[2022].drop('month').drop('day').values


    ln1, = plt.plot(_x,_y_2019,linestyle='-', color='#fc8d62', marker='o', linewidth=1.5,alpha=0.8, markersize=15)
    ln2, = plt.plot(_x,_y_2020,linestyle='-', color='#66c2a5', marker='H', linewidth=1.5,alpha=0.8, markersize=15)
    ln3, = plt.plot(_x,_y_2021,linestyle='-', color='#e78ac3', marker='X', linewidth=1.5,alpha=0.8, markersize=15)
    ln4, = plt.plot(_x,_y_2022,linestyle='-', color='#8da0cb', marker='D', linewidth=1.5,alpha=0.8, markersize=15)

    plt.xticks(fontsize = 30,rotation=45)
    plt.yticks(fontsize = 30,fontfamily='Times New Roman')
  
    plt.ylabel("迁移规模指数",fontsize=30)
    plt.legend(handles=[ln4,ln3,ln2,ln1],labels = ['2022','2021','2020','2019'],loc='upper right',fontsize=30)
    plt.grid(color='b', ls = '-.', lw = 0.25)
    plt.savefig(expert_path)

def pltMedian(df,expert_path):
    
    month_statics_mean = df.groupby(['year','month']).mean()
    month_statics_median = df.groupby(['year','month']).median()

    fig, ax = plt.subplots(figsize=(30,15), dpi= 300)
    
    axismax = math.ceil(month_statics_mean.drop(columns=['day']).max().max())
    axismin = math.floor(month_statics_mean.drop(columns=['day']).min().min())
    
    ax.hlines(y=month_statics_mean.drop(columns=['day']).columns, xmin=axismin, xmax=axismax, color='gray', alpha=0.5, linewidth=.5, linestyles='dashdot')

    
    for i, date in enumerate(month_statics_mean.loc[(2021,)].index):
        df_date = month_statics_mean.loc[(2021,date)]
        df_date.sort_index()
    
        dx =df_date.drop(index=['day']).values 
        dy=month_statics_mean.loc[(2021,date)].drop(index=['day']).index.values


        map_vir = cm.get_cmap(name='PiYG')  
        
        
        ax.scatter(x=dx, y=dy, s=130, edgecolors='gray', c=map_vir(date/12), alpha=0.2,marker='o')
    
        for a in zip(dx,dy):
            ax.text(x=a[0], y=a[1], s= str(date),ha='center', va='center', fontsize=14,fontfamily='SimHei')
        
        
    df_date_median =  month_statics_median.median(axis=0)
    ax.scatter(y=month_statics_median.loc[(2021,date)].drop(index=['day']).index, x=df_date_median.drop(index=['day']).values, s=150, marker='^',c='firebrick')
   

   
    # Decorations
    red_patch = plt.plot([],[], marker="^", ms=15, ls="", mec=None, color='firebrick', label="中位数")
    plt.legend(handles=red_patch,fontsize=20)
   # ax.set_title('Distribution of City Mileage by Make', fontdict={'size':22})
    ax.set_xlabel('迁移规模指数', alpha=0.7,fontsize=20)
    #ax.set_yticks(df.index)
    #ax.set_yticklabels(df.manufacturer.str.title(), fontdict={'horizontalalignment': 'right'}, alpha=0.7)
    
    
    
    ax.set_xlim(axismin, axismax)
    plt.xticks(alpha=0.7,fontsize= 20,fontfamily='Times New Roman')
    plt.yticks(alpha=0.7,fontsize= 20)
   
    plt.gca().spines["top"].set_visible(False)    
    plt.gca().spines["bottom"].set_visible(False)    
    plt.gca().spines["right"].set_visible(False)    
    plt.gca().spines["left"].set_visible(False)   
    plt.grid(axis='both', alpha=.4, linewidth=.1)

    plt.savefig(expert_path)


if __name__ == "__main__":
   
    plt.rcParams[ 'font.sans-serif' ] = [ 'SimSun' ] # 步骤一(替换sans-serif字体)
    plt.rcParams[ 'axes.unicode_minus' ] = False  # 步骤二(解决坐标轴负数的负号显示问题)


    df_in_re,df_out_re,df_re =  load_csv()
    df_in = aggregate(df_in_re.T)
    df_out = aggregate(df_out_re.T)
    df = aggregate(df_re.T)
    df_out_2 = pd.concat([df_out.iloc[:,0:36]*-1,df_out.iloc[:,36:]],axis=1)


    #pltIndex(df,'出图//1-整体指数-按年.png')
    #pltIndex(df_in,'出图//2-迁入整体指数-按年.png')
    #pltIndex(df_out,'出图//3-迁出整体指数-按年.png')


    pltMedian(df,'出图//4-整体_中位数.png')
    pltMedian(df_in,'出图//5-迁入整体指数-中位数.png')
    pltMedian(df_out_2,'出图//6-迁出整体指数-中位数.png')
    
    
