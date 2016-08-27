# -*- coding:utf-8 -*- #

import os
os.chdir('E:\Learning lifetime\QUANT\Down Risk Beta\low volatility')

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

prices = pd.read_csv('ZZ800_Daily_Prices.csv', index_col = 0)
returns = prices.pct_change()
returns.index = pd.to_datetime(returns.index)
#returns.to_csv('Returns.csv')

mv = pd.read_csv('ZZ800_monthly_mv.csv',index_col = 0)
mv.index = pd.to_datetime(mv.index)

codes = pd.read_csv('ZZ800_Monthly_Codes.csv', index_col = 0)
codes.index = pd.to_datetime(codes.index)


def downside_volatility(x, thresh):
	'''
	x: daily return
	thresh: the minimum value to define the downside, 'mean' or float
	'''
	if thresh != 'mean':
		downside = x - thresh
		downside_volatility = np.sqrt((np.where(downside > 0, 0, downside) ** 2).sum(axis = 0))
	else:
		downside = x - x.mean()
		downside_volatility = np.sqrt((np.where(downside > 0, 0, downside) ** 2).sum(axis = 0))

	return downside_volatility

def volatility_strategy(data, codes, m, n, Type, thresh = None):
	'''
	data: daily returns
	codes: monthly index sample codes
	m: hold time horizon, months
	n: number of stocks chosed
	Type: the way to calculate volatility, 'standard' or 'downside'
	'''
	return_for_all_period = pd.DataFrame()
	for t in range(0, len(codes.index), m):
		hist_return = data[codes.ix[t]][:codes.index[t]]
		if Type == 'standard':
			sigma = hist_return[-126:].std()
		elif Type == 'downside':
			sigma = pd.Series(downside_volatility(hist_return[-126:], thresh), 
				index = hist_return[-126:].columns)
		else:
			print('Type should be standard or downside')

		sorted_mv = mv[codes.ix[t]][codes.index[t]].sort_values()
		low_mv = sorted_mv[:100].index
		mid_mv = sorted_mv[100:200].index
		high_mv =sorted_mv[200:].index

		return_for_one_period = pd.DataFrame()
		for i in [low_mv, mid_mv, high_mv]:
			sorted_i = sigma[i].sort_values()
			i_low_vol = sorted_i[:n].index
			i_high_vol = sorted_i[-n:].index

			if t + m <= len(codes.index) - 1:
				i_low_return = data[i_low_vol][(codes.index[t] + timedelta(1)) : (codes.index[t + m])].mean(axis = 1)
				i_high_return =data[i_high_vol][(codes.index[t] + timedelta(1)) : (codes.index[t + m])].mean(axis = 1)
			else:
				i_low_return = data[i_low_vol][(codes.index[t] + timedelta(1)) : ].mean(axis = 1)
				i_high_return =data[i_high_vol][(codes.index[t] + timedelta(1)) : ].mean(axis = 1)
			return_for_one_period = pd.concat([return_for_one_period, i_low_return, i_high_return], axis = 1)

		return_for_all_period = pd.concat([return_for_all_period, return_for_one_period])
	return_for_all_period.columns = [['low_mv','low_mv','mid_mv','mid_mv','high_mv','high_mv'],
                                     ['low_volatility','high_volatility','low_volatility','high_volatility','low_volatility','high_volatility']]
	return return_for_all_period

m = 3
RETURNS = volatility_strategy(returns,codes,m,50,Type='downside',thresh='mean')
