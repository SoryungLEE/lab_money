import pandas as pd
import os
import warnings
from datetime import datetime

empno_list = [
    '19980455', '19980498', '20030488', '20052443', '20101005', '20101056', '20173904',
    '20222659', '20224464', '40047850', '40047980', '20101066', '40050175', '40050179'
]

emp_nm_list = [
    '김성훈', '이호현', '김세훈', '정희진', '주경원', '이소령', '김용섭', '이아론',
    '이승한', '최영돈', '이충성', '정지영', '장현준', '이동근'
]

emp_in_list = [
    '김성훈', '이호현', '김세훈', '정희진', '이소령', '김용섭', '이아론', '이승한',
    '최영돈', '이충성', '정지영', '이동근'
]

type_list = ['출장(일일)', '출장(일반)']
company_folder_path = './dataset/company'
kakao_folder_path = './dataset/kakao'

adjustments = {
    '김성훈': -80000, '김세훈': -1, '이충성': -3, '정지영': -5,
    '이승한': -13, '이동근': -13, '이소령': 5, '정희진': -75000,
    '주경원': 'out', '장현준': 'out'
}

def process_company_data(folder_path, empno_list, type_list):
    warnings.simplefilter("ignore")
    file_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.xlsx')]
    df_result = pd.concat([pd.read_excel(file) for file in file_list], ignore_index=True)
    df_result['사번'] = df_result['사번'].astype(str)
    df_result['시작일'] = pd.to_datetime(df_result['시작일'])
    df_result['종료일'] = pd.to_datetime(df_result['종료일'])
    df_result['출장일수'] = (df_result['종료일'] - df_result['시작일']).dt.days + 1
    df_result = df_result[df_result['사번'].isin(empno_list) & df_result['근태유형'].isin(type_list)]
    return df_result[['사번', '성명', '근태유형', '출장일수', '시작일', '종료일', '사유', '장소']]

def process_kakao_data(folder_path):
    warnings.simplefilter("ignore")
    file_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.xlsx')]
    df_result = pd.concat([pd.read_excel(file) for file in file_list], ignore_index=True)
    df_result['내용'] = df_result['내용'].astype(str)
    df_result['거래금액'] = df_result['거래금액'].str.replace(',', '').astype(int)
    df_result['거래 후 잔액'] = df_result['거래 후 잔액'].str.replace(',', '').astype(int)
    return df_result[df_result['거래구분'] == '일반입금']

def regular_money_function():
    start_date = datetime.strptime('2022-12-01', "%Y-%m-%d")
    total_months_diff = (datetime.now().year - start_date.year) * 12 + datetime.now().month - start_date.month
    return total_months_diff

def apply_adjustments(name, count_days, kakao_money, regular_money):
    out_person = False
    if name in adjustments:
        adjustment = adjustments[name]
        if adjustment == 'out':
            out_person = True
        elif name == '이소령':
            count_days += adjustment
        elif name in ['김성훈', '정희진']:
            kakao_money += adjustment
        else:
            regular_money += adjustment
    return count_days, kakao_money, regular_money, out_person

def total_df(df_company, df_kakao):
    regular_money = regular_money_function()

    results = []
    for name in emp_in_list:
        df_company_personal = df_company[df_company['성명'] == name]
        df_kakao_personal = df_kakao[df_kakao['내용'] == name]
        count_days = df_company_personal['출장일수'].sum()
        kakao_money = df_kakao_personal['거래금액'].sum()

        count_days, kakao_money, regular_money, out_person = apply_adjustments(name, count_days, kakao_money, regular_money)

        must_pay = (count_days + regular_money) * 10000
        diff = must_pay - kakao_money


        results.append({
            "이름": name, "출장일": count_days, "정기회비": regular_money * 10000,
            "부비로 내야하는 돈": must_pay, "모임통장 입금액": kakao_money, "차액": diff
        })

    return pd.DataFrame(results)

def format_currency(value):
    return f"{value:,.0f}"
