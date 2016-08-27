def hist_index_sample(codes_file,change_file,time):
    
    import pandas as pd
    
    codes = pd.read_csv(codes_file)
    codes.columns = [time]
    code = codes[time]
    
    hist_codes = pd.DataFrame({time:code})
    
    change = pd.read_csv(change_file)
    date = change['Date'].unique()
    code = set(code)
    for i in range(0,len(date)-1,2):
        include_c = set(change[change['Date'] == date[i]]['Code'])
        exclude_c = set(change[change['Date'] == date[i+1]]['Code'])
        code = (code - include_c) | exclude_c
        hist_codes[date[i+1]] = pd.Series(list(code))
    
    all_code = set(codes[time])| set(change['Code'])
    ALL_CODE = pd.Series(list(all_code))
    
    return hist_codes, ALL_CODE

hist_codes, ALL_CODE = hist_index_sample('ZZ800Sample.csv','index_log.csv','2016-07-26')
hist_codes.to_csv('ZZ800monthly_code.csv')
ALL_CODE.to_csv('ZZ800_all_code.csv')