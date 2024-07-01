import pandas as pd
import phonenumbers as pn
import logging as lg    
import zipfile
import os
import re

def read_file() -> pd.DataFrame:
    '''Simple file reading from .xlsx format'''
    lg.info('Reading .xlsx')
    for f in os.listdir('.'):
        if f == 'phones.xlsx' and os.path.isfile(f) and not os.path.isdir(f):
            lg.info(f"File::{f}")
            try:
                with open(f, 'rb') as f_obj:
                    if zipfile.is_zipfile(f_obj):
                        return pd.read_excel(f, engine='openpyxl')
            except Exception as e:
                print(f"Error reading file {f}: {e}")
    return pd.DataFrame()

def save_file(df: pd.DataFrame) -> None:
    '''Saving file to phones.xlsx'''
    lg.info('Saving file to phones.xlsx')
    df.to_excel('phones.xlsx', sheet_name='Main', index=False)

def delete_symbols(row):
    '''Deletes symbols from string except for actual phone number'''
    for sym in row:
        if sym not in '0123456789;,':
            row = row.replace(sym, '')
    return row

def get_delimiter(column) -> str:
    '''Obtaining a delimiter for future split phone numbers'''
    column = column.astype(str)
    for delimiter in [',', ';']:
        if column.str.contains(delimiter).any():
            return delimiter
    return '\t'

def split_phone_numbers(row, delimiter, col):
    '''Split phone numbers in 'phones' column by passing delimiter'''
    numbers_count = row[col]
    split_numbers = numbers_count.split(delimiter)
    for i, num in enumerate(split_numbers):
        if len(num) > i:
            row[f'phones::{i+1}::{col}'] = num.strip()
            lg.info(f"Splitted phones::{i+1}")
    return row

def remove_zeroes(df):
    for col in df.columns:
        df[col] = df[col].astype(str)
        for i, row in df.iterrows():
            if row[col].endswith('0') and len(row[col]) >= 7:
                df.at[i, col] = row[col][:-2]

def numbers_iteration(df, col):
    for i, row in df.iterrows():
        lg.debug(f'Iterating.. {i} /ph/')
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

def phones(df):
    ph_short = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12', 'p13']
    ph_long = ['phones_1','phones_2','phones_3','phones_4','phones_5','phones_6','phones_7','phones_8','phones_9','phones_10','phones_11','phones_12','phones_13']
    for col in ph_short:
        if col in df.columns:
            lg.info(f'Added {col} based on phone numbers')
            df[col].dropna()
            df[col] = df[col].astype(str)
            df[col] = df[col].apply(delete_symbols)
            numbers_iteration(df=df, col=col)
    for col in ph_long:
        if col in df.columns:
            lg.info(f'found {col}')
            delimiter = get_delimiter(df[col])
            lg.info('Getting delimiter of phones..')
            lg.info(f'Delimiter is: {delimiter}')
            df[col] = df[col].astype(str)
            df = df.apply(lambda row: split_phone_numbers(row, delimiter=delimiter, col=col), axis=1)
            df = df.drop(col, axis=1)
            lg.debug(f"Dropped {col}")
            for column in df.columns:
                if column.endswith(('code', 'rest')):
                    pass
                elif column.startswith('phones::'):
                    df[column].dropna()
                    df[column] = df[column].astype(str)
                    df[column] = df[column].apply(delete_symbols)
                    numbers_iteration(df=df, col=column)
    return df

def execute_phones():
    df = read_file()
    df = phones(df)
    save_file(df)