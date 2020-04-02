setwd('/Users/jaoming/Documents/Codes/UnboXed Challenge (PSA)')
library(arules)
library(arulesViz)
library(tidyverse)

mba_data = read.csv('cstd.csv')
mba_data = mba_data %>% select(-c(X, category2))
mba_data_split = split(mba_data$category1, mba_data$login)
rules = apriori(mba_data_split, 
                parameter = list(support = 0.05, 
                                 confidence = 0.05))
inspect(sort(rules, by = 'lift'))
plot(rules[1:25], method = 'graph')
plot(rules[1:25], method = 'graph', control = list(type = 'Items'))
  