from dataclasses import dataclass
from pandas import DataFrame
from datetime import date
from typing import Any

REG_REG: dict = {
    '45':'Москва',
    '46':'Московская',
    '65':'Свердловская',
    '60':'Ростовская',
    '80':'Башкортостан',
    '03':'Краснодарский',
    '75':'Челябинская',
    '32':'Кемеровская',
    '52':'Омская',
    '92':'Татарстан',
    '36':'Самарская',
    '18':'Волгоградская',
    '40':'Санкт-Петербург',
    '50':'Новосибирская',
    '63':'Саратовская',
    '01':'Алтайский',
    '07':'Ставропольский',
    '53':'Оренбургская',
    '25':'Иркутская',
    '04':'Красноярский',
    '22':'Нижегородская',
    '57':'Пермский',
    '20':'Воронежская',
    '14':'Белгородская',
    '81':'Бурятия',
    '12':'Астраханская',
    '73':'Ульяновская',
    '71':'Тюменская',
    '28':'Тверская',
    '56':'Пензенская',
    '38':'Курская',
    '37':'Курганская',
    '24':'Ивановская',
    '94':'Удмуртская',
    '15':'Брянская',
    '17':'Владимирская',
    '78':'Ярославская',
    '61':'Рязанская',
    '67':'Тюменская',
    '42':'Липецкая',
    '66':'Смоленская',
    '70':'Тульская',
    '33':'Кировская',
    '19':'Вологодская',
    '83':'Кабардино-Балкарская',
    '69':'Томская',
    '68':'Тамбовская',
    '30':'Краснодарский',
    '54':'Орловская',
    '11':'Архангельская',
    '41':'Ленинградская',
    '97':'Чувашская республика -',
    '27':'Калининградская',
    '05':'Приморский',
    '87':'Коми',
    '86':'Карелия',
    '88':'Марий Эл',
    '34':'Костромская',
    '29':'Калужская',
    '79':'Адыгея',
    '08':'Хабаровский',
    '89':'Мордовия',
    '10':'Алтайский',
    '95':'Хакасия',
    '58':'Псковская',
    '31':'Краснодарский',
    '85':'Калмыкия',
    '49':'Новгородская',
    '47':'Мурманская',
    '91':'Карачаево-Черкесская',
    '76':'Забайкальский',
    '90':'Северная Осетия - Алания',
    '98':'Саха /Якутия/',
    '84':'Алтайский',
    '64':'Сахалинская',
    '74':'Ямало-Ненецкий',
    '99':'Еврейская',
    '62':'Иркутская',
    '82':'Дагестан',
    '51':'Приморский',
    '93':'Тыва',
    '39':'Крым',
    '48':'Коми',
    '44':'Магаданская',
    '55':'Ненецкий',
    '77':'Чукотский АО',
    '96':'Чеченская',
    '26':'Ингушетия',
    '59':'Таймырский',
    '43':'Агинский Бурятский АО',
}

CARD_GROUP = ['НСО', 'МТС MICRON', 'МТС Деньги GRACE', 'Кредитная карта в рамках Пассивных продаж GRACE', 'КЗП',
             'КЗП GRACE', 'МТС Деньги', 'Расчетная карта с РО', 'Расчетные карты VIP/Premium Card GRACE'] 

@dataclass(frozen=False, kw_only=True, repr=True, init=True)
class Namespace(object):

    # Initialisation
    dataframe: DataFrame 

    #Indexes
    name: str 
    surname: str
    last_name: str
    sex: str
    birth_date: str
    birth_place: str
    passport_series: str
    passport_num: str
    passport_org: str
    passport_date: str 
    reg_addr: str
    home_addr: str
    phone_num: str
    mail: str
    position: str 
    credit_num: str
    credit_start_date: str
    credit_end_date: str
    credit_sum: str
    currency: str = 'RUR'
    credit_term: str
    
    total_debt: str
    current_debt: str
    fcd: str 
    current_percent: str
    fcp: str 
    overdue_debt: str
    overdue_percent: str
    comission: str
    fines: str
    dpd: str
    obl: str
    
    # Lifetime properties
    status: str = 'MORATORUM'
    placement: int = 1 
    reg_name: str = ''
    reg_date: date = date.today()
    plan: str = 'ST-090_M-02'
    scheme: str = 'FULL_COLLECT'
    work: str = 'ООО'

    # Added properties
    phone_code: str 
    phone_rest: str
    total_sum: float

    # Mutable properties
    fio_full: str
    passport_div: str 

    # Special properties
    phone_list: list[str]

    def __setattr__(self, __name: str, __value: Any) -> None:
        print(f'__setattr__ call with name: {__name}, value: {__value}')
        super().__setattr__(__name, __value)

    def __getattribute__(self, __name: str) -> Any:
        if __name == '__dict__':
            raise AttributeError('__dict__')
        return super().__getattribute__(__name)
    