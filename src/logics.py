import logging as lg
import pandas as pd
import os
import zipfile
import numpy as np
import re
import phonenumbers as pn

from src.namespaces.namespace import *

def read_file() -> pd.DataFrame:
    '''Simple file reading from .xlsx format'''
    lg.info('Reading file')
    for f in os.listdir('.'):
        if f.endswith('.xlsx') and os.path.isfile(f) and not os.path.isdir(f):
            lg.info(f)
            try:
                with open(f, 'rb') as f_obj:
                    if zipfile.is_zipfile(f_obj):
                        return pd.read_excel(f, engine='openpyxl')
            except Exception as e:
                print(f"Error reading file {f}: {e}")
    return pd.DataFrame()

def save_file(df: pd.DataFrame) -> None:
    '''Saving file to output.xlsx'''
    lg.info('Saving file')
    df.to_excel('output.xlsx', sheet_name='Main', index=False, engine='openpyxl')

def drop_unnamed(df: pd.DataFrame) -> None:
    '''Dropping unused columns in the dataframe'''
    lg.info('Dropping unused fields')
    df.dropna(subset=df.columns[df.columns.str.contains('^Unnamed')], how='all', inplace=True)
    df.drop(df.filter(regex='^Unnamed').columns, axis=1, inplace=True)

def split_passport_number(row) -> pd.Series:
    '''Split passport to passport series and passport number (when every exists in column)'''
    if len(row['passport_div']) >= 11:
        passport_series = row['passport_div'][:5]
        passport_num = row['passport_div'][5:]
    else:
        passport_series = row['passport_series']
        passport_num = row['passport_div']
    return pd.Series([passport_series, passport_num])

def split_passport_full(row):
    '''Another split for different situation occuring'''
    row = str(row)
    if len((row)) <= 6 and not check_passport(row):
        return pd.Series(['', row])
    else:
        passport_series = row[:4]
        passport_num = row[4:]
        return pd.Series([passport_series, passport_num])

def split_passport(row) -> pd.Series:
    '''Splitting full passport with format series/number/org/date'''
    passport_series = row[:4]
    passport_num = row[4:11]
    passport_date = row[-11:]
    passport_org = row[len(passport_series) + len(passport_num) + 2:-len(passport_date)]
    return pd.Series([passport_series, passport_num, passport_date, passport_org])

def add_zeroes(row):
    '''Adding zeroes to passport number'''
    if len(row) <= 5:
        return '0' + row
    else:
        return row
    
def add_cumulative_zeroes(row, length):
    '''Adding zeroes with length specified'''
    row = str(row)
    if len(row) == length:
        return row
    else:
        while len(row) < length:
            row = '0' + row
            return row

def check_passport(row) -> bool:
    '''Checking passport for non-russian validity'''
    row = str(row)
    if row[0].isalpha(): 
        return True
    if len(row) >= 8: # was 7, may cause future errors
        return True
    else:
        return False

def find_passport(row) -> str:
    '''Mapping passport according to country'''
    return 'Паспорт ин. гос.' if check_passport(row) else 'Паспорт РФ'

def split_phone_numbers(row, delimiter):
    '''Split phone numbers in 'phones' column by passing delimiter'''
    numbers_count = row['phones']
    split_numbers = numbers_count.split(delimiter)
    for i, num in enumerate(split_numbers):
        if len(num) > i:
            row[f'p{i+1}'] = num.strip()
    return row

def get_delimiter(column) -> str:
    '''Obtaining a delimiter for future split phone numbers'''
    for delimiter in [',', ';']:
        if column.str.contains(delimiter).any():
            return delimiter
    return '\t'

def split_mail(row):
    '''Split 'mails' column into separate ones'''
    mail_count = row['mails']
    split_mail = mail_count.split(',')
    for i, num in enumerate(split_mail):
        if len(num) > i:
            row[f'm{i+1}'] = num.strip()
    return row

def format_passport_series(row) -> str:
    '''Format passport series from 5555 to 55 55'''
    if row != '':
        row = str(int(row))
    if isinstance(row, str) and (row == '' or row is None):
        return row
    elif len(str(row)) == 4 and str(row).isnumeric():
        return str(row)[0:2] + ' ' + str(row)[2:4]
    elif len(str(row)) == 5 and str(row).isnumeric():
        return row
    elif len(str(int(row))) < 4 and str(row).isnumeric():
        return '0' + str(int(row))[0:1] + ' ' + str(int(row))[1:3]
    else:
        return str(row)

def concat_values(row) -> str:
    '''Value concatenation for client'''
    return str(row['client_id']) + '|' + str(row['credit_id']) + '|' + str(row['outer_id'])

def find_person_by_number(row) -> str:
    '''Find person by phone number # ZAIM EXPRESS'''
    row = str(row)[20:].rstrip(')')
    return row
 
def set_scheme(row) -> str:
    '''Set the scheme for the client based on calculation results'''
    try:
        if 'total_debt' in row.index and 'total_sum' in row.index:
            if round(row['total_debt'], 0) == round(row['total_sum']):
                return 'FULL_COLLECT'
            elif round(row['total_debt'], 0) != round(row['total_sum'], 0):
                lg.info(f"TOTAL DEBT::{round(row['total_debt'], 1)}")
                lg.info(f"TOTAL SUM::{round(row['total_sum'], 1)}")
                return 'BACK_TO_SCHEDULE'
            else:
                return 'FULL_COLLECT'
    except Exception as ex:
        lg.warn(f"ERR::{ex}")
        lg.warn("Unable to set fileds for scheme.")
        return 'UNABLE TO SET FIELDS'

def phone_numbers(row):
    '''Parse and format phone numbers'''
    try:
        row = row.replace(' ', '')
        phone_number = pn.parse(row, 'CH')
        fmt_number = pn.format_number(phone_number, pn.PhoneNumberFormat.E164)
        fmt_number = fmt_number[1:]
        return fmt_number
    except Exception as e:
        lg.info(f'Error parsing phone number by lib.: {e}')
        return ''

def extract_int(row) -> int:
    '''Extract integer from 'placement' column'''
    if row is None:
        return 0
    match = re.search(r'\d+', row)
    if match:
        return int(match.group())
    else:
        return 0

def drop_nulls(row) -> str:
    if not isinstance(row, str):
        row = str(row)
    else:
        pass
    row = '' if row in ['null', 'NULL', 'Null', ' null', ' NULL', ' Null'] else row
    return row

# -- MAIN FUNCTIONS -- #
def name_split(df: pd.DataFrame) -> pd.DataFrame:
    if 'fio_full' in df.columns:
        lg.info('fio_full found in columns, splitting names.')
        try:
            df[['surname', 'first_name', 'last_name']] = df['fio_full'].str.split(' ', expand=True)
        except ValueError as e:
            lg.info(f'Error splitting fio_full: {e}')
            lg.info('Trying to solve the problem...')
            names = df['fio_full'].str.split(' ')#.apply(lambda x: x[:3] + x[4:] if len(x) > 3 else x)
            names = names.apply(lambda x: [i for i in x if i != ''])
            df[['surname', 'first_name', 'last_name']] = pd.DataFrame(names.tolist(), columns=['first_name', 'surname', 'last_name'])
            lg.info("Problem solved.")
    if 'ifo_full' in df.columns:
        lg.info('ifo_full found in columns, splitting names.')
        try:
            df[['first_name', 'surname', 'last_name']] = df['ifo_full'].str.split(' ', expand=True)
        except ValueError as e:
            lg.info(f'Error splitting ifo_full: {e}')
            names = df['ifo_full'].str.split(' ').apply(lambda x: x[:3] + x[4:] if len(x) > 3 else x)
            df[['first_name', 'surname', 'last_name']] = pd.DataFrame(names.tolist(), columns=['first_name', 'surname', 'last_name'])
            lg.info('Trying to solve the problem...')
    return df

def sex_finder(df: pd.DataFrame) -> pd.DataFrame:
    if 'sex' in df.columns:
        lg.info('sex found in columns, processing...')
        df['sex'] = df['sex'].apply(lambda x: 'Ж' if x == 'Женский' or x == 1 or x == 'Ж' else 'М')
    if 'sex' not in df.columns and 'last_name' in df.columns:
        lg.info('sex not found in columns, but last_name is present. Processing sex with respect to last name')
        df['sex'] = df['last_name'].apply(lambda x: x[-4:] if x is not None else '')
        df['sex'] = df['sex'].apply(lambda x: 'М' if x[-2:] in ['ич', 'ов', 'ин'] else 'Ж')
    return df

def date_fetcher(df: pd.DataFrame) -> pd.DataFrame:
    try: 
        if 'birth_date' in df.columns:
            lg.info('birth_date in columns, formatting dates...')
            df['birth_date'] = pd.to_datetime(df['birth_date'], format='%d.%m.%Y').dt.date
        if 'passport_date' in df.columns:
            lg.info('passport_date in columns, formatting dates...')
            df['passport_date'] = pd.to_datetime(df['passport_date'], format='%d.%m.%Y').dt.date
        if 'credit_start_date' in df.columns:
            lg.info('credit_start_date in columns, formatting dates...')
            df['credit_start_date'] = pd.to_datetime(df['credit_start_date'], format='%d.%m.%Y').dt.date
        if 'credit_end_date' in df.columns:
            lg.info('credit_end_date in columns, formatting dates...')
            df['credit_end_date'] = pd.to_datetime(df['credit_end_date'], format='%d.%m.%Y').dt.date
    except:
        lg.warn("Could not fetch dates.")
        pass
    return df

def get_passport(df: pd.DataFrame) -> pd.DataFrame:
    if 'passport' in df.columns:
        lg.info('found passport column, trying to migrate data...')
        df[['passport_series', 'passport_num', 'passport_date', 'passport_org']] = df['passport'].apply(split_passport)
    if 'passport_full' in df.columns:
        lg.info('found passport_full column, using split_passport_full')
        df['passport_full'] = df['passport_full'].astype(str)
        df[['passport_series', 'passport_num']] = df['passport_full'].apply(split_passport_full)
    if 'passport_series' in df.columns and 'passport_div' not in df.columns:
       lg.info('looking to passport_series. applying format_passport_series')
       df['passport_series'] = df['passport_series'].apply(format_passport_series)
       lg.info('Adding zeroes to passport_num..')
       df['passport_num'] = df['passport_num'].astype(str).apply(add_zeroes)
       df['passport_num'] = df['passport_num'].apply(add_zeroes)
    if 'passport_div' in df.columns:
        lg.info('found passport_div column, using split_passport_number')
        df[['passport_series', 'passport_num']] = df[['passport_div', 'passport_series']].apply(split_passport_number, axis=1)
    if 'passport_num' in df.columns:
        lg.info('found passport_series column, formatting document type')
        df['doctype'] = df['passport_num'].astype(str).apply(find_passport)
    if 'passport_series' in df.columns:
        lg.info('found passport_series column, mapping the region based on passport series')
        df['region'] = df['passport_series'].astype(str).apply(lambda x: REG_REG.get(x[:2], 'UNKNOWN'))
    try:    
        lg.info('Checking for zeroes in passport_num..')
        df['passport_num'] = df['passport_num'].astype(str).apply(lambda row: add_cumulative_zeroes(row, 6))
        lg.info('Seeking nulls in passport_org..')
        df['passport_org'] = df['passport_org'].apply(lambda x: '' if x in ['null', 'NULL'] else x)
    except Exception as e:
        lg.warn('Could not drop nulls in passport_org')
        pass
    return df

def old_phones(df: pd.DataFrame) -> pd.DataFrame:
    if 'phone_num_zaim' in df.columns:
        lg.info('found phone_num_zaim column (UNIQUE), applying zaim express mapping')
        df['phone_num_zaim'].dropna()
        df['phone_num_zaim'] = df['phone_num_zaim'].astype(str)
        try:
            lg.info("Finding person by phone number..")
            df['contact_person'] = df["phone_num_zaim"].apply(find_person_by_number)
            lg.info("Person found.")
        except Exception as e:
            lg.info("Couldn't find person, moving on..")
            pass
        try:
            df['phone_num_zaim'] = df['phone_num_zaim'].apply(phone_numbers)
            df['phone_code'] = df["phone_num_zaim"].str.slice(1, 4)
            df['phone_rest'] = df["phone_num_zaim"].str.slice(4)
        except Exception as e:
            lg.info("Couldn't split phone numbers [ZAIM]. Please, rename them to p1, p2..p(n)")
            pass
    if 'phone_code' in df.columns:
        lg.info('replacing nans in phone_code...')
        df['phone_code'] = df["phone_code"].str.replace('an', '')
    if 'home_phone' in df.columns:
        lg.info('Found home_phone in columns, fetching..')
        df['home_phone'] = df["home_phone"].astype(str)
        for i, row in df.iterrows():
            if row['home_phone'].startswith('+7'):
                df.at[i, 'homephone_code'] = df.at[i, 'home_phone'].replace("+7", "8")[1:4]
                df.at[i, 'homephone_rest'] = df.at[i, 'home_phone'].replace("+7", "8")[4:] 
            elif row['home_phone'].startswith('8'):
                df.at[i, 'homephone_code'] = row['home_phone'][1:4]
                df.at[i, 'homephone_rest'] = row['home_phone'][4:] 
    return df

def main_phones(df: pd.DataFrame) -> pd.DataFrame:
    if 'phones' in df.columns:
        lg.info('found phones column (MULTIPLE), applying multiple mapping')
        delimiter = get_delimiter(df['phones'])
        lg.info('Getting delimiter of phones..')
        lg.info(f'Delimiter is: {delimiter}')
        df['phones'] = df['phones'].astype(str)
        df = df.apply(lambda row: split_phone_numbers(row, delimiter=delimiter), axis=1)
    for col in ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12', 'p13']:
        if col in df.columns:
            lg.info(f'Added {col} based on phone numbers')
            df[col].dropna()
            df[col] = df[col].astype(str)
            for i, row in df.iterrows():
                if row[col].endswith('.0'):
                    df.at[i, col] = row[col][:-2]
                if row[col].startswith('8'):
                    df.at[i, col] = re.sub(r'\D', '', row[col]) if len(row[col]) >= 13 else row[col]
                    df.at[i, col + '_code'] = row[col][1:4]
                    df.at[i, col + '_rest'] = row[col][4:11]
                elif row[col].startswith('+7'):
                    df.at[i, col] = re.sub(r'\D', '', row[col]) if len(row[col]) >= 13 else row[col]
                    df.at[i, col + '_code'] = re.sub(r"^7", "", df.at[i, col])[:3]
                    df.at[i, col + '_rest'] = re.sub(r"^7", "", df.at[i, col])[3:11]
                elif row[col].startswith('7'):
                    df.at[i, col] = re.sub(r'\D', '', row[col]) if len(row[col]) >= 13 else row[col]
                    df.at[i, col + '_code'] = re.sub(r"^7", "", df.at[i, col])[:3]
                    df.at[i, col + '_rest'] = re.sub(r"^7", "", df.at[i, col])[3:11]
                elif row[col].startswith('9'):
                    df.at[i, col + '_code'] = df.at[i, col][:3]
                    df.at[i, col + '_rest'] = df.at[i, col][3:]
                elif row[col].startswith('мт'):
                    df.at[i, col + '_code'] = df.at[i, col][4:7]
                    df.at[i, col + '_rest'] = df.at[i, col][7:15]
                #else:
                #    df.at[i, col] = re.sub(r'\D', '', row[col])
    df = df.replace(['nan', 'an'], '', regex=True)
    return df

def currency(df: pd.DataFrame) -> pd.DataFrame: 
    if 'currency' in df.columns:
        lg.info('Mapping currency...')
        if df['currency'].isin(['RUB', 'RUR']).any():
            df['currency'] = getattr(Namespace, 'currency')
        else:
            df['currency'] = 'ERROR_CHECK_CURRENCY'
    if 'currency' not in df.columns:
        lg.info('adding currency...')
        df['currency'] = getattr(Namespace, 'currency')
    return df

def debt(df: pd.DataFrame) -> pd.DataFrame:
    if 'total_debt' in df.columns:
        df['total_debt'] = df['total_debt'].apply(lambda x: 0 if x in ['null', 'NULL', None, '', ' '] else x)
    if 'fcd' in df.columns and 'fcp' in df.columns:
        lg.info('found fcd and fcp columns, updating total_sum and setting up scheme...')
        df['total_sum'] = (df.get('fcd', 0)) + (df.get('fcp', 0)) + (df.get('overdue_debt', 0)) + (df.get('overdue_percent', 0)) + (df.get('fines', 0)) + (df.get('comission', 0)) + (df.get('gp', 0))
        df['scheme'] = df.apply(set_scheme, axis=1)
    elif 'current_debt' not in df.columns and 'current_percent' not in df.columns:
        lg.info('current_debt and current_percent not found in columns, applying FULL_COLLECT scheme...')
        df['total_sum'] = df.get('overdue_debt', 0) + (df.get('overdue_percent', 0)) + (df.get('comission', 0)) + (df.get('fines', 0))
        df['scheme'] = df.apply(set_scheme, axis=1)
    elif 'current_debt' in df.columns and 'current_percent' in df.columns and 'fcd' not in df.columns and 'fcp' not in df.columns:
        lg.info('current_debt and current_percent found in columns, calculating scheme...')
        df['current_debt_calc'] = df['current_debt'] - df.get('overdue_debt', 0)
        df['current_percent_calc'] = df['current_percent'] - df.get('overdue_percent', 0)
        df['total_sum'] = (df.get('current_debt_calc', 0)) + df.get('overdue_debt', 0) + df.get('current_percent_calc', 0) + (df.get('overdue_percent', 0)) + (df.get('comission', 0)) + (df.get('fines', 0))
        df['scheme'] = df.apply(set_scheme, axis=1)
    return df

def workplace(df: pd.DataFrame) -> pd.DataFrame:
    if 'position' in df.columns:
        lg.info('found position column. mapping workplace...')
        df['work'] = df['position'].apply(lambda x: 'ООО' if x is None or x == '' else x)
    return df

def mail(df: pd.DataFrame) -> pd.DataFrame:
    if 'mail' in df.columns:
        lg.info('found mail column (UNIQUE). mapping mail...')
        df['mail'] = df['mail'].str.lower()
        df['mail'] = df['mail'].apply(lambda x: '' if x == 'не задано' else x)
        df['mail'] = df['mail'].apply(lambda x: '' if x in ['null', 'NULL'] else x)
    if 'mails' in df.columns:
        lg.info('found mails column (MULTIPLE). applying multiple mapping...')
        df = df.apply(split_mail, axis=1)
    return df

def regliv(df: pd.DataFrame) -> pd.DataFrame:
    try:
        lg.info('found registration and living related columns. concatenating results...')
        df['registration'] = df[['rg_reg', 'np_reg', 'st_reg', 'hs_reg', 'cp_reg', 'ft_reg']].apply(lambda x: ', '.join(x.astype(str)), axis=1)
        df['living'] = df[['rg_liv', 'np_liv', 'st_liv', 'hs_liv', 'cp_liv', 'ft_liv']].apply(lambda x: ', '.join(x.astype(str)), axis=1)
        df = df.drop(['rg_reg', 'np_reg', 'st_reg', 'hs_reg', 'cp_reg', 'ft_reg',
                      'rg_liv', 'np_liv', 'st_liv', 'hs_liv', 'cp_liv', 'ft_liv',],
                    axis=1)
    except:
        pass
    if 'reg_addr' in df.columns and 'home_addr' in df.columns:
        df['home_addr'] = np.where(df['reg_addr'] == df['home_addr'], '', df['home_addr'])
    return df

def concatenate_ids(df: pd.DataFrame) -> pd.DataFrame:
    if 'client_id' in df.columns and 'credit_id' in df.columns and 'outer_id' in df.columns:
        lg.info('found client_id, credit_id and outer_id columns. concatenating results...')
        df['extend'] = df.apply(concat_values, axis=1)
        df = df.drop(['client_id', 'credit_id', 'outer_id'], axis=1)
    return df

def product_group(df: pd.DataFrame) -> pd.DataFrame:
    if 'product_group' in df.columns:
        lg.info('found product_group column. mapping product...')
        df['product'] = np.where(df['product_group'].isin(CARD_GROUP), 'CARD',
                        np.where(df['product_group'] == 'Автокредит', 'CAR',
                        np.where(df['product_group'] == 'Целевой потребительский кредит', 'POS',
                        np.where(df['product_group'] == 'Нецелевой потребительский кредит', 'CASH', np.nan))))
        df['product_name'] = np.where(df['product'].isin(['CARD']), 'Карточные продукты',
                        np.where(df['product'] == 'CAR', 'Автокредит',
                        np.where(df['product'] == 'POS', 'Потребительский целевой кредит',
                        np.where(df['product'] == 'CASH', 'Потребительский нецелевой кредит', np.nan))))
    return df

def lifetimes(df: pd.DataFrame) -> pd.DataFrame:
    lg.info('Setting lifetime attributes...')
    if 'placement' not in df.columns:
        df['placement'] = getattr(Namespace, 'placement')
    if 'placement' in df.columns:
        df['placement'] = df['placement'].apply(extract_int)
    df['reg_name'] = getattr(Namespace, 'reg_name')
    df['reg_date'] = getattr(Namespace, 'reg_date')
    return df

def fuck_nans(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df['passport_org'] = df['passport_org'].apply(drop_nulls)
    except:
        pass
    return df

def truncate(df: pd.DataFrame) -> pd.DataFrame:
    '''Main function to truncate the dataframe and bring it to XC format'''
    lg.info('Truncating file')
    df = df.fillna('')
    df = df.map(lambda x: '' if x in ['null', 'NULL'] else x)
    # ----------- F+ ----------- #
    df['credit_num'] = df['credit_num'].astype(str)
    if 'inn' in df.columns:
        df['inn'] = df['inn'].astype(str).apply(lambda row: add_cumulative_zeroes(row, 12))
    if 'passport_full' in df.columns:
        df['passport_full'] = df['passport_full'].fillna('').astype(str).apply(lambda row: add_cumulative_zeroes(row, 10))
    # ----------- NAME SPLITTER ----------- #
    try:
        df = name_split(df)
    except Exception as e:
        lg.warn("EXCEPTION CAUGHT IN NAMESPLIT")
        lg.warn(f"Err::{e}")
        pass
    # ----------- SEX FINDER ----------- #
    try:
        df = sex_finder(df)
    except Exception as e:
        lg.warn("EXCEPTION CAUGHT IN SEX FINDER")
        lg.warn(f"Err::{e}")
        pass
    # ----------- TO DATETIME CONVERTION ----------- #
    try:
        df = date_fetcher(df)
    except Exception as e:
        lg.warn("EXCEPTION CAUGHT IN DATE FETCHER")
        lg.warn(f"Err::{e}")
        pass
    # ----------- PASSPORT INFO ----------- #
    try:
        if 'passport_series' in df.columns and 'passport_num' in df.columns:
            df['passport_series'] = df['passport_series'].astype(str)
            df['passport_num'] = df['passport_num'].astype(str)
        df = get_passport(df)
    except Exception as e:
        lg.warn("EXCEPTION CAUGHT IN PASSPORT FUNCTIONS")
        lg.warn(f"Err::{e}")
        pass
    # ----------- PHONE NUMBER MAIN ----------- #
    try:
        df = old_phones(df)
    except Exception as e:
        lg.warn("EXCEPTION CAUGHT IN NOMAIN PHONES")
        lg.warn(f"Err::{e}")
        pass
    # ----------- PHONE NUMBERS MNOGO ----------- #
    try:
        df = main_phones(df)
    except Exception as e:
        lg.warn("EXCEPTION CAUGHT IN MAIN PHONES LIST")
        lg.warn(f"Err::{e}")
        pass
    # ----------- CURRENCY CHECKING ----------- #
    try: 
        df = currency(df)
    except Exception as e:
        lg.warn("EXCEPTION CAUGHT IN CURRENCY")
        lg.warn(f"Err::{e}")
        pass
    # ----------- DEBT CALCULATION ----------- #
    try:
        df = debt(df)
    except Exception as e:
        lg.warn("EXCEPTION CAUGHT IN DEBT CALCULATION")
        lg.warn(f"Err::{e}")
        pass
    # ----------- FILLING ROWS ----------- #
    try:
        df = workplace(df)
        df = mail(df)
    except Exception as e:
        lg.warn("EXCEPTION CAUGHT IN WORKPLACE/MAIL")
        lg.warn(f"Err::{e}")
        pass
    # ----------- REGISTRATION/LIVING ADDRESSES ----------- #
    try:
        df = regliv(df)
    except Exception as e:
        lg.warn("EXCEPTION CAUGHT IN REG/LIV ADDRESSES")
        lg.warn(f"Err::{e}")
        pass
    # ----------- ID CONCATENATION ----------- #
    try:
        df = concatenate_ids(df)
    except Exception as e:
        lg.warn("EXCEPTION CAUGHT IN ID CONCATENATION")
        lg.warn(f"Err::{e}")
        pass
    # ----------- MTS PRODUCT GROUP ----------- #
    try:
        df = product_group(df)
    except Exception as e:
        lg.warn("EXCEPTION CAUGHT IN MTS PRODUCT GROUP")
        lg.warn(f"Err::{e}")
        pass
    # ----------- SETTING LIFETIME ATTRIBUTES ----------- #
    try:
        df = lifetimes(df)
    except Exception as e:
        lg.warn("EXCEPTION CAUGHT IN LIFETIME ATTRIBUTES")
        lg.warn(f"Err::{e}")
        pass
    try:
        df = df.fillna('')
        df = fuck_nans(df)
    except Exception as e:
        lg.warn("Could not delete NANs.")
        pass
    return df

def execute() -> None:
    '''Execution of the functions mentioned above'''
    lg.info('Executing $main')
    try:
        df = read_file()
        drop_unnamed(df)
        out_df = truncate(df)
        save_file(df=out_df)
    except Exception as e:
        lg.exception('Error in $main')