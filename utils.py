import pandas as pd
import os
import warnings
from datetime import datetime

empno_list = [
    '19980455', '19980498', '20030488', '20052443', '20101005', '20101056', '20173904',
    '20222659', '20224464', '40047850', '40047980', '20101066', '40050175', '40050179', '20241603'
]

emp_nm_list = [
    '김성훈', '이호현', '김세훈', '정희진', '주경원', '이소령', '김용섭', '이아론',
    '이승한', '최영돈', '이충성', '정지영', '장현준', '이동근', '김학준', '류제완', '이승연'
]

emp_in_list = [
    '김성훈', '이호현', '김세훈', '정희진', '이소령', '김용섭', '이아론', '이승한',
    '최영돈', '이충성', '정지영', '이동근', '김학준', '류제완', '이승연'
]

emp_in_rank_list = [
    '상', '상', '중', '중', '하', '하', '하', '하',
    '중', '상', '상', '하', '하', '하', '하'
]


type_list = ['출장(일일)', '출장(일반)']
company_folder_path = './dataset/company'
kakao_folder_path = './dataset/kakao'

adjustments = {
    '김성훈': -80000, '김세훈': -1, '이충성': -3, '정지영': -5,
    '이승한': -13, '이동근': -13, '이소령': 5, '정희진': -75000,
    '김학준' : -20, '류제완':-21, '이승연':-21, 
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


def regular_money_function(name=None, rank=None, cutoff_date=datetime.strptime('2024-10-01', "%Y-%m-%d")):
    """
    정기 회비 계산 함수
    - 2024년 9월까지: 월 단위로 동일 금액 부비 계산
    - 2024년 10월부터: emp_in_rank_list에 따라 차등 금액 계산
    """
    start_date = datetime.strptime('2022-12-01', "%Y-%m-%d")
    end_date = datetime.strptime('2024-09-30', "%Y-%m-%d")
    months_before_cutoff = ((end_date.year - start_date.year) * 12 + end_date.month - start_date.month) + 1

    # 기존 방식
    regular_money_before = months_before_cutoff

    # Default regular money if no name and rank are provided
    if name is None or rank is None:
        return regular_money_before

    # 2024년 10월 이후 차등 금액 계산
    current_date = datetime.now()
    if current_date >= cutoff_date:
        months_after_cutoff = ((current_date.year - cutoff_date.year) * 12 + current_date.month - cutoff_date.month) + 1
        if rank == "상":
            regular_money_after = months_after_cutoff * 20000
        elif rank == "중":
            regular_money_after = months_after_cutoff * 15000
        else:  # "하"
            regular_money_after = months_after_cutoff * 10000
    else:
        regular_money_after = 0

    return regular_money_before * 10000 + regular_money_after



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
    """
    전체 데이터 프레임 계산
    - 각 직원의 출장일수, 카카오 입금 금액, 정기 회비를 계산하여 차액 반환
    """
    results = []
    for name, rank in zip(emp_in_list, emp_in_rank_list):
        df_company_personal = df_company[df_company['성명'] == name]
        df_kakao_personal = df_kakao[df_kakao['내용'] == name]
        count_days = df_company_personal['출장일수'].sum()
        kakao_money = df_kakao_personal['거래금액'].sum()

        # Adjustments 적용
        count_days, kakao_money, regular_money, out_person = apply_adjustments(
            name, count_days, kakao_money, regular_money_function(name, rank)
        )

        # 퇴사자 처리
        if out_person:
            results.append({
                "이름": name, "출장일": "퇴사", "정기회비": "퇴사", 
                "부비로 내야하는 돈": "퇴사", "모임통장 입금액": kakao_money, "차액": "퇴사"
            })
            continue

        # 총 내야 하는 돈 계산
        must_pay = (count_days * 10000) + regular_money
        diff = must_pay - kakao_money

        results.append({
            "이름": name, "출장일": count_days, "정기회비": regular_money,
            "부비로 내야하는 돈": must_pay, "모임통장 입금액": kakao_money, "차액": diff
        })

    return pd.DataFrame(results)


def format_currency(value):
    return f"{value:,.0f}"
