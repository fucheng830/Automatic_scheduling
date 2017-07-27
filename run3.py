#coding:utf-8

import pandas as pd
import datetime
import calendar as cal
import numpy as np
import random
import copy
import math



def load_person_info(file_path):
    df = pd.read_excel(file_path)
    return df

def make_month_df(person_num):
    today = datetime.datetime.now()
    year = today.year
    d = cal.monthrange(today.year, today.month)
    drange = pd.date_range(start='%d-%d-%d'%(year, today.month, 1), end='%d-%d-%d'%(year, today.month, d[1]), freq='D')
    #dt_state = [d.weekday() for d in drange]
    row = [np.NaN for r in range(drange.shape[0])]
    #[row for i in range(person_num)]
    table = np.zeros((person_num, drange.shape[0]))
    df = pd.DataFrame([row for i in range(person_num)])
    return df, drange

def auto():
    person_info = load_person_info('person_info.xlsx')
    night_pool = person_info[(person_info['state']==1) & (person_info['max_night']>0)]
    work_pool = person_info[person_info['state']==1]
    df, dt_state = make_month_df(person_info.shape[0])
    neight_work, day_work = work_day_count(person_info, dt_state)
    score_list = []
    #for i in range(100):
    neight_df = sample_neight_work(df, night_pool, person_info)
    day_work_plan = day_work_distribute(neight_df[neight_df.index.isin(work_pool.index)], day_work)    
    working_df = sample_day_work(neight_df, day_work_plan, work_pool, dt_state)
    #print working_df
    work_count = []
    for i in range(working_df.shape[0]):
        work_count.append(working_df.iloc[i,:].sum())
        for l in range(working_df.shape[1]):
            if pd.isnull(working_df.iloc[i,l]) or working_df.iloc[i,l] == 0:
                working_df.iloc[i,l] = '--'
            elif working_df.iloc[i,l]==1.0:
                working_df.iloc[i,l] = u'白'
            elif working_df.iloc[i,l]==1.5:
                working_df.iloc[i,l] = u'夜'
                
    working_df['work_count'] = work_count
    working_df.index =  person_info['name']
          
    working_df.to_excel('test.xlsx')
          
    return working_df

def check(df):
    pass


def work_day_count(persion_df, dt_state):
    neight_work = len(dt_state)*2
    day_work = 0
    for r in dt_state: 
        if r.weekday() in [5, 6]:
            work_num = 2
        else:
            work_num = 5
        day_work += work_num
    
    return neight_work,day_work

    
def is_over_max_night(df, person_info, i):
    max_night = person_info.iloc[i]['max_night']
    if len(filter(lambda x: x == 1.5 ,df.iloc[i,:])) >= 2*max_night:
        return True
    elif len(filter(lambda x: x == 1.5 ,df.iloc[i,:])) < 2*max_night:
        return False

def count_neight_value(df):
    for i in range(df.shape[0]):
        last_neight = None
        for l in range(df.shape[1]):
            pass
        
def count_day_value(row):
    value = 0
    for r in row:
        if r==1:
            value+=0.5
        elif r==1.5:
            value+=2
        elif value==0:
            value-=2
    return value
        
        
def day_work_distribute(df, need):
    day_work = []
    for i in range(df.shape[0]):
        used_day = df.iloc[i,:].sum()
        day_work.append(21-used_day)
    
    total_day_work = sum(day_work)
    #print total_day_work,need
    if total_day_work>need:
        pass
    elif total_day_work<need:
        diff = need-total_day_work
        for r in range(int(math.ceil(diff/len(day_work)))):
            for i in range(len(day_work)):
                day_work[i]+=1
                diff-=1
                if diff==0:
                    break
    return day_work
                
    
def sample_neight_work(data, night_pool, person_info):

    while True:
        try:
            df = data.copy()
            last_night_work = None
            sample_index = copy.deepcopy(list(night_pool.index))
            for i in range(df.shape[1]):
                if 1.5 not in list(df.iloc[:,i]):
                    if last_night_work:
                        today_index = filter(lambda x: x not in last_night_work, sample_index)
                    else:
                        today_index = sample_index
                    
                    rank_list = []
                    for l in today_index:
                        rank_list.append([l, df.iloc[l,:].sum()])
                    rank_list = sorted(rank_list, key=lambda x:x[1])
                    sample, cout_value = zip(*rank_list)
                    
                    night_person = list(sample)[:2]
        
                    df.iloc[night_person[0],i] = 1.5
                    df.iloc[night_person[1],i] = 1.5
                    if i+1 < df.shape[1]:
                        df.iloc[night_person[0],i+1] = 1.5
                        df.iloc[night_person[1],i+1] = 1.5
                    if i+2 < df.shape[1]:
                        df.iloc[night_person[0],i+2] = 0
                        df.iloc[night_person[1],i+2] = 0
                    if i+3 < df.shape[1]:
                        df.iloc[night_person[0],i+3] = 0
                        df.iloc[night_person[1],i+3] = 0
                    
                    #print night_person[0],len(filter(lambda x: x == 1.5 ,df.iloc[night_person[0],:]))
                    #print night_person[1],len(filter(lambda x: x == 1.5 ,df.iloc[night_person[1],:]))
                    if is_over_max_night(df, person_info, night_person[0]):
                        sample_index = filter(lambda x: x != night_person[0], sample_index)
                    
                    if is_over_max_night(df, person_info, night_person[1]):
                        sample_index = filter(lambda x: x != night_person[1], sample_index)
                        
                    last_night_work = night_person
            break
        except:
            pass
    
    return df
            
def sample_day_work(data, daywork_plan, work_pool, dt_state):

    df = copy.deepcopy(data)
    sample_index = copy.deepcopy(list(work_pool.index))
    full_person = []
    for i in range(df.shape[1]):
        if dt_state[i].weekday() in [5, 6]:
            work_num = 2
        else:
            work_num = 5
        
        not_use_person = list(df.iloc[:,i].dropna().index)      
        can_use_person = filter(lambda x: x not in not_use_person, sample_index)
        
        plan_list = []
        for r in can_use_person:
            temp_df = copy.deepcopy(df)
            isover_max = False
            total_value = 0
            temp_df.iloc[r,i] = 1
            value = count_day_value(temp_df.iloc[r,:i+1])
            if (temp_df.iloc[r,:].apply(lambda x:1 if x==1 else 0)).sum()>daywork_plan[r]:
                continue
            else:
                plan_list.append([r, abs(value)])
        sorted_plan = sorted(plan_list, key=lambda x:x[1])
        print sorted_plan
        for index, l in enumerate(sorted_plan):  
            #print index,l[0]
            if index < work_num:
                df.iloc[l[0],i]=1
                
                print l[0],index
            else:
                df.iloc[l[0],i]=0
                print l[0],index

                   
        print df           
        
    return df
if __name__ == '__main__':
    
    df = auto() 

