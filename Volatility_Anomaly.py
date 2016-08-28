# -*- coding:utf-8 -*- #

import os
os.chdir('E:\Learning lifetime\QUANT\Down Risk Beta\low volatility')

import numpy as np
import pandas as pd

#导入并处理数据

#价格数据

prices =  pd.read_csv('ZZ800_Daily_Prices.csv',index_col=0)
prices = prices.replace(0.,np.nan)
prices.index = pd.to_datetime(prices.index)

#交易状态
status = pd.read_csv('TradingorNot.csv',index_col = 0, encoding = 'gb2312')
status_code = pd.DataFrame(np.where((status == 0) | (status == '0'),np.nan,1),
                           index = status.index, columns = status.columns)
status_code = pd.DataFrame(np.where(status == u'停牌一天',0,status_code), 
                           index = status.index, columns = status.columns)
status_code.index = pd.to_datetime(status_code.index)
status_code

#收益率
returns = prices.pct_change()
returns
#returns.to_csv('Returns.csv')
return_cleaned = pd.DataFrame(np.where(status_code == 1, returns, np.nan),
                              index = status_code.index,
                              columns = status_code.columns)
return_cleaned

#导入每月成分股代码
codes = pd.read_csv('ZZ800_Monthly_Codes.csv',index_col=0)
codes.index = pd.to_datetime(codes.index)
codes

mv = pd.read_csv('ZZ800_monthly_mv.csv',index_col = 0)
mv.index = pd.to_datetime(mv.index)

industry_name = pd.read_csv('Industry_Names.csv',
                            encoding = 'gb2312',index_col = 0)
industry_name = industry_name['Industry_Name'].dropna()

monthly_price = prices.resample('M').last()
monthly_returns = monthly_price.pct_change()

def downside_volatility(x, thresh):
	'''
	x: daily return
	thresh: the minimum value to define the downside, 'mean' or float
	'''
	if thresh != 'mean':
		downside = x - thresh
		downside_volatility = np.sqrt((np.where(downside > 0, 
                                          0, downside) ** 2).mean(axis = 0))
	else:
		downside = x - x.mean()
		downside_volatility = np.sqrt((np.where(downside > 0, 
                                          0, downside) ** 2).mean(axis = 0))

	return downside_volatility
 
def volatility(hist_return,window,Type):
    available_stocks = hist_return.ix[-1].dropna().index
    sigmas = pd.DataFrame(columns = available_stocks)
    if Type == 'standard':
        for s in available_stocks:
            Temp = hist_return[s].dropna()
            if len(Temp) < window:
                sigma = Temp.std()
            else:
                sigma = Temp[-window:].std()
            sigmas[s] = [sigma]
    elif Type == 'downside':
        for s in available_stocks:
            Temp = hist_return[s].dropna()
            if len(Temp) < window:
                sigma = downside_volatility(Temp,0)
            else:
                sigma = downside_volatility(Temp[-window:],0)
            sigmas[s] = [sigma]
    else:
        print('Type should be standard or downside')
    return sigmas.ix[0] 
 

monthly_price = prices.resample('M').last()
monthly_returns = monthly_price.pct_change()
monthly_mv = mv.resample('M').last()
timeline = pd.date_range('2006-12-31','2016-06-30',freq='M')

Y = pd.DataFrame()  #收益率
X1 = pd.DataFrame()  #市值
for t in range(len(timeline)-1):
    time_s = timeline[t]
    sample_stocks = list(codes.ix[time_s])
    time_e = timeline[t+1]
    y = pd.DataFrame(monthly_returns.ix[time_e][sample_stocks]).T
    x1 = pd.DataFrame(monthly_mv.ix[time_s][sample_stocks]).T
    Y = pd.concat([Y,y])
    X1 = pd.concat([X1, x1])

X1 = np.log(X1)

data = return_cleaned
Type = 'standard'
sigmas = pd.DataFrame()
for t in range(len(timeline) - 1):
    Time = timeline[t]
    hist_return = data[codes.ix[Time]][:Time]
    #计算波动率方法一
    '''
    if Type == 'standard':  
        sigma = hist_return[-126:].std()
    elif Type == 'downside':
        sigma = pd.Series(downside_volatility(hist_return[-126:],thresh),
        index=hist_return[-126:].columns)
    else:
        print 'Type should be standard or downside'
    '''
            
    # 计算波动率方法二
    sigma = volatility(hist_return,126,Type)
    sigmas = pd.concat([sigmas,sigma],axis =1)
sigmas.columns = timeline[:-1]
X2 = sigmas.T

Y.index = timeline[:-1]

reg_var = pd.DataFrame()
reg_var['returns'] = Y.stack()
reg_var['mv'] = X1.stack()
reg_var['volatility'] = X2.stack()

import statsmodels.api as sm
reg_var = reg_var.dropna(axis =0,how = 'any')
reg_var = sm.add_constant(reg_var)
reg = sm.OLS(reg_var['returns'],reg_var[['mv','volatility','const']]).fit()
reg.summary()

reg = pd.ols(y=reg_var['returns'], x=reg_var[['mv','volatility']])
reg