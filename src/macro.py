import openpyxl
import logging as lg
import os 
import zipfile
from main import TF
import win32com.client as win
import pythoncom
import time

def prepare_excel():
    lg.info('Reading file')
    #win.CoInitialize()
    for f in os.listdir('.'):
        if f.endswith('.xlsx') and os.path.isfile(f) and not os.path.isdir(f):
            lg.info('Absolute path: ' + os.path.abspath(f))
            lg.info('File: ' + f)
            try:
                with open(f, 'rb') as f_obj:
                    if zipfile.is_zipfile(f_obj):
                        #return openpyxl.load_workbook(f), str(f)
                        return win.DispatchEx("Excel.Application"), str(f)
            except Exception as e:
                lg.info(f"Error reading file {f}: {e}")
    return None

def start_macros(cols, xl, f):
    lg.info('Starting macros')
    wb = xl.Workbooks.Open(os.path.abspath(f))
    ws = wb.Worksheets[0]
    lg.info(f"Columns are: %s" % cols)
    try:
        vba = wb.VBProject
        vba_module = vba.VBComponents.Import("\\\\storage1\\userdata\\AnaliticalDepartment\\Tools\\VBA\\товары_загруз.bas")
        wb.Save()
    except Exception as e:
        lg.error(f'Failed to load the VBA macro. Error: {e}')
        if wb is not None:
            wb.Close(SaveChanges=True)
        return
    try:
        selection = ws.Range("B1:C20")
        #selection = ",".join(f"{ws.Columns(col).Address}" for col in cols)
        lg.info(f"Selection: {selection}") 
        lg.info(f"Running on coordinates: {selection}") 
        xl.Application.Run("Товар", selection) # {f}!PERSONAL.XLSB!Товар {col} 
        wb.Save()
    except Exception as e:
        lg.error(f'Error: {e}')
        if wb is not None:
            wb.Close(SaveChanges=True)
        return
    finally:
        xl.Quit()
        del xl

def macro(text_value):
    pythoncom.CoInitialize()
    xl, f = prepare_excel()
    if xl is not None:
        start_macros(cols=text_value, xl=xl, f=f)
    else:
        lg.error(f'No Excel file found in the current directory {os.getcwd()}. Found files: {os.listdir(".")}')
    pythoncom.CoUninitialize()
