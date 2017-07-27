#coding:utf-8

import pandas as pd
import datetime
import calendar as cal
import numpy as np
import random
import copy



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
    df = sample_neight_work(df, night_pool, person_info)
    df = sample_day_work(df, work_pool, dt_state)
    
    
    work_count = []
    for i in range(df.shape[0]):
        work_count.append(df.iloc[i,:].sum())
        for l in range(df.shape[1]):
            if pd.isnull(df.iloc[i,l]) or df.iloc[i,l] == 0:
                df.iloc[i,l] = '--'
            elif df.iloc[i,l]==1.0:
                df.iloc[i,l] = u'白'
            elif df.iloc[i,l]==1.5:
                df.iloc[i,l] = u'夜'
                
    df['work_count'] = work_count
    df.index =  person_info['name']
          
    df.to_excel('test.xlsx')
          
    return df
    

                
def is_over_max_night(df, person_info, i):
    max_night = person_info.iloc[i]['max_night']
    if len(filter(lambda x: x == 1.5 ,df.iloc[i,:])) >= 2*max_night:
        return True
    elif len(filter(lambda x: x == 1.5 ,df.iloc[i,:])) < 2*max_night:
        return False
    
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
        
                    night_person = random.sample(today_index, 2)
        
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
            
def sample_day_work(data, work_pool, dt_state):
    #while True:
    #try:
    df = data.copy()
    sample_index = copy.deepcopy(list(work_pool.index))
    full_person = []
    for i in range(df.shape[1]):
        rank_list = []
        for l in sample_index:
            rank_list.append([l, df.iloc[l,:].sum()])
            rank_list = sorted(rank_list, key=lambda x:x[1])
            sample_index, cout_value = zip(*rank_list)
        
        if dt_state[i].weekday() in [5, 6]:
            work_num = 2
        else:
            work_num = 5
        
        not_use_person = list(df.iloc[:,i].dropna().index)      
        can_use_person = filter(lambda x: x not in not_use_person, sample_index)
    
        work_person = can_use_person[:work_num]

        for r in work_person:
            df.iloc[r,i] = 1
            #if df.iloc[r,:].sum()>=21:
                #full_person.append(r)

        
        
        #sample_index = filter(lambda x:x not in full_person, rank_list)
            
        
    #except Exception as e:
        #print e
    return df
if __name__ == '__main__':
    
    df = auto() 

