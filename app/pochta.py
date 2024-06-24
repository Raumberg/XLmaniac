import os
import pandas as pd
import numpy as np
import re
import logging
import zipfile
from app.namespaces.namespace import CARD_GROUP, REG_REG

lg = logging.getLogger(__name__)

def read_file() -> dict:
    '''Simple file reading from .xlsx format'''
    lg.info('Reading file')
    excel_files = []
    for f in os.listdir('.'):
        if f.endswith('.xlsx') and os.path.isfile(f) and not os.path.isdir(f):
            lg.info(f)
            excel_files.append(f)
    if not excel_files:
        lg.warning('No .xlsx files found')
        return {}
    dataframes = {}
    for f in excel_files:
        try:
            with pd.ExcelFile(f, engine='openpyxl') as xl:
                sheet_names = xl.sheet_names
                for sheet_name in sheet_names:
                    dataframes[sheet_name] = pd.read_excel(xl, sheet_name=sheet_name)
        except Exception as e:
            lg.info(f"Error reading file {f}: {e}")
    return dataframes

def save_file(ctr: pd.DataFrame, filename: str) -> None:
    '''Saving file to output.xlsx'''
    lg.info('Saving file' + filename)
    ctr.to_excel(filename, sheet_name='Main', index=False)

def drop_unnamed(ctr: pd.DataFrame) -> None:
    '''Dropping unused columns in the dataframe'''
    lg.info('Dropping unused fields')
    ctr.dropna(subset=ctr.columns[ctr.columns.str.contains('^Unnamed')], how='all', inplace=True)
    ctr.drop(ctr.filter(regex='^Unnamed').columns, axis=1, inplace=True)

def format_passport_series(row) -> str:
    '''Format passport series from 5555 to 55 55'''
    if row == '' or row is None:
        return row
    elif len(str(row)) == 4 and str(row).isnumeric():
        return str(row)[0:2] + ' ' + str(row)[2:4]
    elif len(str(row)) == 5 and str(row).isnumeric():
        return row
    elif len(str(int(row))) < 4 and str(row).isnumeric():
        return '0' + str(int(row))[0:1] + ' ' + str(int(row))[1:3]
    else:
        return str(row)

def add_zeroes(row):
    '''Adding zeroes to passport number'''
    if len(row) <= 5:
        return '0' + row
    else:
        return row

def set_scheme(row) -> str:
    '''Set the scheme for the client based on calculation results'''
    try:
        if 'total_debt' in row.index and 'total_sum' in row.index:
            if round(row['total_debt'], 0) == round(row['total_sum']):
                return 'FULL_COLLECT'
            elif round(row['total_debt'], 0) != round(row['total_sum'], 0):
                return 'BACK_TO_SCHEDULE'
            else:
                return 'FULL_COLLECT'
    except Exception as ex:
        lg.warn(f"ERR::{ex}")
        lg.warn("Unable to set fileds for scheme.")
        return 'UNABLE TO SET FIELDS'

def debt(df: pd.DataFrame) -> pd.DataFrame:
    df['current_debt_calc'] = df['current_debt'] - df.get('overdue_debt', 0)
    df['current_percent_calc'] = df['current_percent'] - df.get('overdue_percent', 0)
    df['total_sum'] = (df.get('current_debt_calc', 0)) + (df.get('current_percent_calc', 0)) + df.get('overdue_debt', 0) + (df.get('overdue_percent', 0)) + (df.get('comission', 0)) + (df.get('overdue_comission', 0)) + (df.get('overdraft', 0)) + (df.get('overdue_overdraft', 0)) + (df.get('collect_pennies', 0))
    df['scheme'] = df.apply(set_scheme, axis=1)
    return df

def format_frame(ctr: pd.DataFrame, tlf: pd.DataFrame):
    ##### CONTRACTS #####
    drop_unnamed(ctr)
        # ----------- SEX FINDER ----------- #
    if 'sex' in ctr.columns:
        lg.info('sex found in columns, processing...')
        ctr['sex'] = ctr['sex'].apply(lambda x: 'Ж' if x == 'Женский' or x == 1 else 'М')
    if 'sex' not in ctr.columns and 'last_name' in ctr.columns:
        lg.info('sex not found in columns, but last_name is present. Processing sex with respect to last name')
        ctr['sex'] = ctr['last_name'].apply(lambda x: x[-4:] if x is not None else '')
        ctr['sex'] = ctr['sex'].apply(lambda x: 'М' if x[-2:] in ['ич', 'ов', 'ин'] else 'Ж')
        # ----------- TO DATETIME CONVERTION ----------- #
    if 'birth_date' in ctr.columns:
        lg.info('birth_date in columns, formatting dates...')
        ctr['birth_date'] = pd.to_datetime(ctr['birth_date'], format='%d.%m.%Y').dt.date
    if 'passport_date' in ctr.columns:
        lg.info('passport_date in columns, formatting dates...')
        ctr['passport_date'] = pd.to_datetime(ctr['passport_date'], format='%d.%m.%Y').dt.date
    if 'credit_start_date' in ctr.columns:
        lg.info('credit_start_date in columns, formatting dates...')
        ctr['credit_start_date'] = pd.to_datetime(ctr['credit_start_date'], format='%d.%m.%Y').dt.date
    if 'credit_end_date' in ctr.columns:
        lg.info('credit_end_date in columns, formatting dates...')
        ctr['credit_end_date'] = pd.to_datetime(ctr['credit_end_date'], format='%d.%m.%Y').dt.date
        # ----------- PASSPORT SERIES FORMATTING ----------- #
    if 'passport_series' in ctr.columns:
       lg.info('looking to passport_series. applying format_passport_series')
       ctr['passport_series'] = ctr['passport_series'].apply(format_passport_series)
       ctr['passport_num'] = ctr['passport_num'].astype(str).apply(add_zeroes)
       ctr['passport_num'] = ctr['passport_num'].apply(add_zeroes)
    if 'passport_series' in ctr.columns:
        lg.info('found passport_series column, mapping the region based on passport series')
        ctr['region'] = ctr['passport_series'].astype(str).apply(lambda x: REG_REG.get(x[:2], 'UNKNOWN'))
    if 'passport_org' in ctr.columns:
        ctr['division_code'] = ctr['passport_org'].astype(str).apply(lambda row: row[-8:] if row is not None else None)
        # ----------- PASSPORT SERIES FORMATTING ----------- #
    if 'product_group' in ctr.columns:
        lg.info('found product_group column. mapping product...')
        ctr['product'] = np.where(ctr['product_group'].isin(['Карта']), 'CARD',
                        np.where(ctr['product_group'] == 'CAR - автокредит', 'CAR',
                        np.where(ctr['product_group'] == 'POS - кредит', 'POS',
                        np.where(ctr['product_group'] == 'CASH - кредит', 'CASH', np.nan))))
        ctr['product_name'] = np.where(ctr['product_group'].isin(['Карта']), 'Карточные продукты',
                        np.where(ctr['product_group'] == 'CAR - автокредит', 'Автокредит',
                        np.where(ctr['product_group'] == 'POS - кредит', 'Потребительский целевой кредит',
                        np.where(ctr['product_group'] == 'CASH - кредит', 'Потребительский нецелевой кредит', np.nan))))
    try:
        ctr = debt(ctr)
    except Exception as e:
        lg.warn("EXCEPTION CAUGHT IN DEBT CALCULATION")
        lg.warn(f"Err::{e}")
        pass
   ##### TELEPHONES ##### 
    for col in ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12', 'p13']:
        if col in tlf.columns:
            lg.info(f'Added {col} based on phone numbers')
            tlf[col].dropna()
            tlf[col] = tlf[col].astype(str)
            for i, row in tlf.iterrows():
                lg.info('Iterating through rows.. /dev/')
                if row[col].endswith('.0'):
                    tlf.at[i, col] = row[col][:-2]
                if row[col].startswith('8'):
                    tlf.at[i, col] = re.sub(r'\D', '', row[col]) if len(row[col]) >= 13 else row[col]
                    tlf.at[i, col + '_code'] = row[col][1:4]
                    tlf.at[i, col + '_rest'] = row[col][4:11]
                elif row[col].startswith('+7'):
                    tlf.at[i, col] = re.sub(r'\D', '', row[col]) if len(row[col]) >= 13 else row[col]
                    tlf.at[i, col + '_code'] = re.sub(r"^7", "", tlf.at[i, col])[:3]
                    tlf.at[i, col + '_rest'] = re.sub(r"^7", "", tlf.at[i, col])[3:11]
                elif row[col].startswith('7'):
                    tlf.at[i, col] = re.sub(r'\D', '', row[col]) if len(row[col]) >= 13 else row[col]
                    tlf.at[i, col + '_code'] = re.sub(r"^7", "", tlf.at[i, col])[:3]
                    tlf.at[i, col + '_rest'] = re.sub(r"^7", "", tlf.at[i, col])[3:11]
                elif row[col].startswith('9'):
                    tlf.at[i, col + '_code'] = tlf.at[i, col][:3]
                    tlf.at[i, col + '_rest'] = tlf.at[i, col][3:]
    if 'phone_type' in tlf.columns:
        lg.info('found phone_type column. mapping product...')
        tlf['type'] = np.where(tlf['phone_type'].isin(['Мобильный']), 'MOBILE',
                        np.where(tlf['phone_type'] == 'Домашний', 'HOME',
                        np.where(tlf['phone_type'] == 'Рабочий', 'WORK',
                        np.where(tlf['phone_type'] == 'Дополнительный', 'CONTACT', np.nan))))

def execute_pochta() -> None:
    '''Main function'''
    lg.info('Executing main function')
    dfs = read_file()
    ctr = dfs['Договоры']
    tlf = dfs['Телефоны']
    adr = dfs['Адреса']
    format_frame(ctr, tlf)
    save_file(ctr, 'Договоры.xlsx')
    save_file(tlf, 'Телефоны.xlsx')
    save_file(adr, 'Адреса.xlsx')
    lg.info('Main function finished')
    