#coding:utf-8

import pandas as pd
import datetime
import calendar as cal
import numpy as np
import random
import copy
import math
from matplotlib import pyplot as plt


def load_person_info(file_path):
    df = pd.read_excel(file_path)
    return df

person_info = load_person_info('person_info.xlsx')
step = 2

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
    #print night_pool, work_pool
    result = get_scheduling(df, dt_state, person_info, night_pool.index, work_pool.index)
    #neight_work, day_work = work_day_count(person_info, dt_state)
    #print neight_work, day_work
    result.to_excel('test_4.xlsx')
    
def select_person(person_list, num):
    return random.sample(person_list, num)

def get_scheduling(df, dt_state, person_df, night_list, day_list):
    for i in df.columns:
        if dt_state[i].weekday() in [5, 6]:
            num = 4
        else:
            num = 7
        
        if i==0:
            #第一天随机取数作为种子
            night_person = select_person(night_list, 2)
            day_person = select_person(filter(lambda x:x not in night_person, day_list), num-2)
            
            for p in night_person:
                df.iloc[p, i] = u'夜'
            for p in day_person:
                df.iloc[p, i] = u'白'
            #print df
            
        else:
            #蒙特卡洛搜索结果代入错误
            plan_list = []
            record = []
            for round in range(20):
                test_df = df.copy()
                score = montecarlo_search(test_df, i, step, num, day_list, night_list)
                plan_list.append([score, test_df])
                record.append([round, score])
            
            plan = sorted(plan_list, key=lambda x:x[0], reverse=True)
            df.loc[:,i] = plan[0][1].loc[:,i]
            #record_df = pd.DataFrame(record, columns=['round', 'score'])
            #record_df.plot()
            #plt.show()
    
    total_works = []
    night_works = []
    for p in df.index:
        row = df.iloc[p,:]
        day_work = filter(lambda x:True if x==u'白' else False, row)
        night_work = filter(lambda x:True if x==u'夜' else False, row)
        total_works.append(len(night_work)*1.5+len(day_work))
        night_works.append(len(night_work))
    df['night_work'] = night_works
    df['total_wrok'] = total_works
    df.index = person_df.index
    print df
    return df

#todo:利用蒙特卡洛多步搜索跳出局部最优解
def montecarlo_search(df, i, step, num, day_list, night_list):
    """i,当前日期指针;
    step,蒙特卡洛搜索步长
    num,总上班人数
    """
    all_score = 0
    for r in range(step):
        index = i+r
        if index>=len(df.columns):
            continue
        
        if (index)%2==0:
            #开始新的夜班轮换
            night_person = random.sample(night_list, 2)
            daywork_person = random.sample(filter(lambda x:x not in night_person, day_list), num-2)
            #todo:计算得分
        else:
            last_ser = df.iloc[:,index-1]
            night_person = list(last_ser[last_ser == u'夜'].index)
            daywork_person = random.sample(filter(lambda x:x not in night_person, day_list), num-2)
            #todo:计算得分
        round_score = 0
        #print index

        for p in daywork_person:
            row = df.iloc[p, :index]
            round_score += count_day_value(list(row), 21)
            df.iloc[p, index] = u'白'   
        for p in night_person:
            row = df.iloc[p, :index]
            round_score += count_night_value(list(row), person_info.iloc[p]['max_night']*2)
            df.iloc[p, index] = u'夜'
    all_score+=round_score
    return all_score
        

def select_day_person(df, person_df, day_list, i):
    max_score = None
    day_person = [] 
    for r in day_list:
        row = df.iloc[r, :i]
        max_workday = 21
        if max_score == None:
            max_score = count_day_value(list(row), max_workday)
            day_person.append(r)
        else:
            score = count_day_value(list(row), max_workday)
            if score>max_score:
                max_score = score
                day_person[0] = r
            elif score==max_score:
                day_person.append(r)
    
    print max_score
    if len(day_person)>1:
        return random.sample(day_person, 1)
    else:
        return day_person[0]
        
            
def select_night_person(df, person_df, night_list, i):
    max_score = None
    night_person = []
    for r in night_list:
        row = df.iloc[r, :i]
        max_night = person_df.iloc[r]['max_night']
        if max_score == None:
            max_score = count_neight_value(list(row), max_night)
            night_person.append(r)
        else:
            score = count_neight_value(list(row), max_night)
            
            if score>max_score:
                max_score = score
                night_person[0] = r
            elif score==max_score:
                night_person.append(r)
    
    if len(night_person)>1:
        return random.sample(night_person, 1)
    else:
        return night_person[0]

def count_day_value(row, max_workday):
    score = 0
    continue_work = 0
    
    for i in range(len(row)):
        if row[-(i+1)] == u'白':
            continue_work+=1
        else: 
            break
    if continue_work <5:
        score += 2*continue_work
    else:
        score -= 99
        
    if row[-1] == u'夜':
        score -= 99
    elif len(row)>1 and row[-2] == u'夜':
        score -= 99
    score+=count_sum_workday(row, max_workday)
    return score
    
def count_night_value(row, max_night):
    score = 0
    if row[-1] == u'夜':
        score -= 99
    elif row[-1] == np.NaN:
        score += 20
    elif row[-1] == u'白':
        score -= 26
    
    max_night_score = count_sum_night(row, max_night)
    score+=max_night_score
    return score

def count_sum_night(row, max_night):
    score = 0
    night_day = filter(lambda x:True if x==u'夜' else False, row)
    workday = filter(lambda x:True if x==u'白' else False, row)
    if len(night_day)>=max_night:
        score = -200
    score -= 9*len(night_day)
    score -= 4*len(workday)
    return score
    
def count_sum_workday(row, max_workday):
    score = 0
    night_day = filter(lambda x:True if x==u'夜' else False, row)
    workday = filter(lambda x:True if x==u'白' else False, row)
    all_day = 1.5*len(night_day) + 1*len(workday)
    if all_day >= max_workday:
        score = -500
    #score -= 9*len(night_day)
    score -= 4*len(workday)
    return score
    
def day_work_distribute(df, need):
    day_work = []
    for i in range(df.shape[0]):
        used_day = df.iloc[i,:].sum()
        day_work.append(21-used_day)
    
    total_day_work = sum(day_work)
    #print total_day_work, need
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



if __name__ == '__main__':
    
    df = auto() 

