import pandas as pd

def split_passport_number(row: str) -> pd.Series[str]:
    '''Split passport to passport series and passport number (when every exists in column)'''
    if len(row['passport_div']) >= 11:
        passport_series = row['passport_div'][:5]
        passport_num = row['passport_div'][5:]
    else:
        passport_series = row['passport_series']
        passport_num = row['passport_div']
    return pd.Series([passport_series, passport_num])

def split_passport_full(row: str) -> pd.Series[str]:
    '''Another split for different situation occuring'''
    row = str(row)
    if len((row)) <= 6 and not check_passport(row):
        return pd.Series(['', row])
    else:
        passport_series = row[:4]
        passport_num = row[4:]
        return pd.Series([passport_series, passport_num])

def split_passport(row: str) -> pd.Series:
    '''Splitting full passport with format series/number/org/date'''
    passport_series = row[:4]
    passport_num = row[4:11]
    passport_date = row[-11:]
    passport_org = row[len(passport_series) + len(passport_num) + 2:-len(passport_date)]
    return pd.Series([passport_series, passport_num, passport_date, passport_org])

def add_zeroes(row: str) -> str:
    '''Adding zeroes to passport number'''
    if len(row) <= 5:
        return '0' + row
    else:
        return row

def add_cumulative_zeroes(row: str, length: int) -> str:
    '''Adding zeroes with length specified'''
    row = str(row)
    if len(row) == length:
        return row
    else:
        while len(row) < length:
            row = '0' + row
            return row

def check_passport(row: str) -> bool:
    '''Checking passport for non-russian validity'''
    row = str(row)
    if row[0].isalpha(): 
        return True
    if len(row) >= 8: # was 7, may cause future errors
        return True
    else:
        return False

def find_passport(row: str) -> str:
    '''Mapping passport according to country'''
    return 'Паспорт ин. гос.' if check_passport(row) else 'Паспорт РФ'