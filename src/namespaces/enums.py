from enum import Enum

class Person(Enum):
    NAME = "first_name"
    SURNAME = "surname"
    LASTNAME = "last_name"
    SEX = "sex"
    BIRTH_DATE = "birth_date"
    BIRTH_PLACE = "birth_place"
    REG_ADDRESS = "reg_addr"
    HOME_ADDRESS = "home_addr"
    MAIL = "mail"
    POSITION = "position"
    WORK = "work"
    REGISTRATION = "registration"

class NameVariants(Enum):
    IFO = "ifo_full"
    FIO = "fio_full"

class Passport(Enum):
    SERIES = 'passport_series'
    NUMBER = 'passport_num'
    ORGANIZATION = 'passport_org'
    DATE = 'passport_date'
    TYPE = 'doctype'
    REGION = 'region'
    
class PassportVariants(Enum):
    DIVISION = 'passport_div'
    FULL = 'passport_full'
    DEFAULT = 'passport'

class Register(Enum):
    STATUS = "status"
    PLACEMENT = "placement"
    NAME = "reg_name"
    DATE = "reg_date"
    COLLECT_PLAN = "plan"
    COLLECT_SCHEME = "scheme" 
    EXTENSION = "extend"
    CLIENT_ID = "client_id"
    CREDIT_ID = "credit_id"
    OUTER_ID = "outer_id"
    PRODUCT = "product"
    PRODUCT_GROUP = "product_group"
    PRODUCT_NAME = "product_name"
    CURRENCY = "currency"

class Debt(Enum):
    NUM = "credit_num"
    START_DATE = "credit_start_date" 
    END_DATE = "credit_end_date "
    SUM = "credit_sum"
    CURRENCY = "currency"
    TERM = "credit_term" 
    
    TOTAL = "total_debt" 
    TOTAL_SUM = "total_sum"
    CURRENT = "current_debt"
    CURRENT_PERCENT = "current_percent" 
    CURRENT_CALCULATED = "current_debt_calc"
    CURRENT_PERCENT_CALCULATED = "current_percent_calc"
    OVERDUE = "overdue_debt"
    OVERDUE_PERCENT = "overdue_percent"
    COMISSIONS = "comission"
    FINES = "fines"
    FINAL_CURRENT = "fcd"
    FINAL_CURRENT_PERCENT = "fcp"
    STATE_DUTY = "gp"

    DPD = "dpd"

class Phones(Enum):
    MULTIPLE = "phones"
    CODE = "phone_code"
    REST = "phone_rest"
    CONTACT = "contact_person"
    ZAIM = "phone_num_zaim"

class PhoneEnum(Enum):
    PHONES = "phones"
    PHONES_2 = "phones_2"
    PHONES_3 = "phones_3"
    PHONES_4 = "phones_4"
    PHONES_5 = "phones_5"
    P1 = "p1"
    P2 = "p2"
    P3 = "p3"
    P4 = "p4"
    P5 = "p5"
    P6 = "p6"
    P7 = "p7"
    P8 = "p8"
    P9 = "p9"
    P10 = "p10"


class Clients(Enum):
    DEFAULT = 'default'
    POST = 'post'