#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 16:30:08 2020

@author: jaoming
"""

import os
os.chdir('/Users/jaoming/Documents/Codes/UnboXed Challenge (PSA)/Cleaned')

import pandas as pd
import seaborn as sns
import datetime
from matplotlib import pyplot

jan_data = pd.read_csv('jan2020Cleaned.csv')
feb_data = pd.read_csv('feb2020Cleaned.csv')

all_category_1 = list(jan_data['category1'].unique())
for i in feb_data['category1']:
       if i not in all_category_1:
              all_category_1.append(i)
all_category_1.sort()
all_category_1_wo_dates = all_category_1[17:]
all_category_1_dates = all_category_1[:17]

all_category_2 = list(jan_data['category2'].unique())
for i in feb_data['category2']:
       if i not in all_category_2:
              all_category_2.append(i)   

# all the data. both jan and feb. without the notices
total_data = jan_data.append(feb_data)
total_data = total_data.loc[~total_data['category1'].isin(all_category_1_dates), :]
total_data = total_data.reset_index()
total_data = total_data.drop('index', axis = 1)

# Exploratory Data Analysis
## looking at the organisations
org_names = list(jan_data['orgCode'].unique()) # all the organisations
for org in feb_data['orgCode'].unique():
       if org not in org_names:
              org_names.append(org)

orgs = {}
for org in org_names:
       users = list(total_data[total_data['orgCode'] == org]['userID'].unique())           
       orgs[org] = {'users': users, 'size': len(users)}

orgs_and_size = [[i, orgs[i]['size']] for i in orgs]
orgs_and_size.sort(key = lambda x: x[1], reverse = True)

## shows how many employees each organisation has
plot1 = sns.barplot([i[1] for i in orgs_and_size],
                    [i[0] for i in orgs_and_size])
plot1.set_xticklabels(plot1.get_xticklabels(), 
                      horizontalalignment = 'right', 
                      fontsize = 'x-small',
                      fontweight = 'light')
plot1.set_title('Organisation Sizes')
plot1.set_xlabel('Organisations'); plot1.set_ylabel('Size')

## looking at the most accessed category - cat1
plot2 = sns.barplot(total_data['category1'].value_counts()[:20].values, 
                    total_data['category1'].value_counts()[:20].index)
plot2.set_title('Most Accessed Category 1 Tab')
plot2.set_xlabel('No. of Accesses'); plot2.set_ylabel('Category Name')
### It seems that Container and Pregate Services are the most frequently visited tabs

## looking at the most accessed category - cat2
plot3 = sns.barplot(total_data['category2'].value_counts()[:20].values, 
                    total_data['category2'].value_counts()[:20].index)
plot3.set_title('Most Accessed Category 2 Tab')
plot3.set_xlabel('No. of Accesses'); plot2.set_ylabel('Category Name')

## diving into what services they have in the most accessed cat1
total_data[total_data['category1'].isin(['Container', 'Pregate Services'])].loc[:, ['userID', 'category1', 'category2']].groupby(['category1', 'category2']).count()


# pre-processing for MBA (association between services in Portnet)
sorted_total_data = total_data.sort_values(by = ['orgCode', 'userID', 'date'])
sorted_total_data = sorted_total_data.reset_index()
sorted_total_data = sorted_total_data.drop('index', axis = 1)
login = []
count = -1
for i in sorted_total_data['category1']:
       if i[:8] == 'Internet':
              count += 1
       login.append(count)
sorted_total_data['login'] = login
clean_sorted_total_data = sorted_total_data.loc[:, ['login', 'category1', 'category2']]
clean_sorted_total_data = clean_sorted_total_data[clean_sorted_total_data['category1'] != 'Internet (Primary)']
clean_sorted_total_data = clean_sorted_total_data[clean_sorted_total_data['category1'] != 'Internet (Secondary)']

ohe_cstd = clean_sorted_total_data.groupby(['login'])['category1'].unique()

# MBA for category1
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules
te = TransactionEncoder()
ohe_cstd_raw = te.fit(ohe_cstd).transform(ohe_cstd)
ohe_cstd = pd.DataFrame(ohe_cstd_raw, columns = te.columns_)
# ohe_cstd.to_csv('onehotencoded_data.csv')
frequent_itemsets = apriori(ohe_cstd, min_support = 0.05, use_colnames = True)
rules = association_rules(frequent_itemsets, metric = "lift", min_threshold = 1)
rules = rules.sort_values(by = 'lift', ascending = False)
rules

# =============================================================================
# org4_data = total_data[total_data['orgCode'] == 'ORG4']
# org4_data = org4_data.fillna('Log-in')
# org4_actions = {}
# for i in org4_data.iloc[:, 5]:
#        if i not in org4_actions.keys():
#               org4_actions[i] = 1
#        else:
#               org4_actions[i] += 1
# =============================================================================


# code to look at an organisation's most used category1 tab
# total_data[total_data['orgCode'] == org_names[0]].iloc[:,4].value_counts().reset_index()



# Looking at the dates to find the peak and non peak hours
total_data_dates = total_data['date']
total_data_dates = total_data_dates.reset_index()
total_data_dates = total_data_dates.drop('index', axis = 1)
total_data_dates = list(total_data_dates.values.reshape([1, -1])[0])
for i in range(len(total_data_dates)):
       if total_data_dates[i].count(':') > 1:
              total_data_dates[i] = total_data_dates[i][-8:-3].strip()
              if total_data_dates[i][1] == ':':
                     total_data_dates[i] = '0' + total_data_dates[i]
       else:
              total_data_dates[i] = total_data_dates[i][-5:].strip()
              if total_data_dates[i][1] == ':':
                     total_data_dates[i] = '0' + total_data_dates[i]
total_data_dates = [datetime.datetime.strptime(i, '%H:%M') for i in total_data_dates]
total_data_dates = pd.DataFrame(total_data_dates)
total_data_dates.columns = ['date']
total_data_dates['count'] = [1]*len(total_data_dates)
total_data_dates = total_data_dates.groupby(pd.Grouper(key = 'date', freq = '30min')).sum()
# pd.DataFrame(list(zip(list(map(lambda x: x.strftime("%H:%M"), total_data_dates.index)), list(total_data_dates.values.reshape(1, -1)[0]))))
fig, ax = pyplot.subplots(figsize = (16, 8))
time_plot = sns.barplot(list(map(lambda x: x.strftime("%H:%M"), total_data_dates.index)), list(total_data_dates.values.reshape(1, -1)[0]))
time_plot.set_xticklabels(time_plot.get_xticklabels(), rotation = 45, horizontalalignment = 'right')
time_plot.set_title('Active Timings')
time_plot.set_xlabel('Timings'); time_plot.set_ylabel('Activity Count')



total_data_dates = total_data_dates['date'].apply(lambda x: x.strftime("%H:%M"))
total_data['date'] = total_data_dates

total_data_peak = total_data.loc[list(total_data['date'] >= '08:30'), :]
total_data_peak = total_data_peak.loc[list(total_data_peak['date'] <= '09:30'), :]

peak_categories = total_data_peak.groupby(['category2']).count().index
peak_count_access = total_data_peak.groupby(['category2']).count()['date'].values
peak_data = list(zip(peak_categories, peak_count_access))
peak_data.sort(key = lambda x: x[1], reverse = True)
peak_data = peak_data[:22]
peak_data = [i for i in peak_data if i[0][:8] != 'Internet']

peak1_plot = sns.barplot([i[1] for i in peak_data], [i[0] for i in peak_data])
peak1_plot.set_title('Frequent Categories between 8:30am to 9:30am', weight = 'bold')
peak1_plot.set_xlabel('No. of Accesses'); peak1_plot.set_ylabel('Category2')

total_data_non_peak = total_data.loc[list(total_data['date'] >= '14:00'), :]
total_data_non_peak = total_data_non_peak.loc[list(total_data_non_peak['date'] <= '16:30'), :]

non_peak_categories = total_data_non_peak.groupby(['category2']).count().index
non_peak_count_access = total_data_non_peak.groupby(['category2']).count()['date'].values
non_peak_data = list(zip(non_peak_categories, non_peak_count_access))
non_peak_data.sort(key = lambda x: x[1], reverse = True)
non_peak_data = non_peak_data[:22]
non_peak_data = [i for i in non_peak_data if i[0][:8] != 'Internet']

peak2_plot = sns.barplot([i[1] for i in non_peak_data], [i[0] for i in non_peak_data])
peak2_plot.set_title('Frequent Categories between 2:00pm to 4:30pm', weight = 'bold')
peak2_plot.set_xlabel('No. of Accesses'); peak2_plot.set_ylabel('Category2')






