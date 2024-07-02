import pandas as pd
import numpy as np
import os
import warnings
from datetime import datetime




#필요한거 세팅
empno_list = ['19980455','19980498','20030488','20052443','20101005','20101056','20173904','20222659','20224464','40047850','40047980','20101066', '40050175', '40050179']
              #김세훈,    이호현,     최영돈,     정희진,    김성훈,    이충성      김용섭,    주경원,     이소령,     장현준,    이아론,     정지영     이승한,      이동근

emp_nm_list = ['김성훈','이호현','김세훈','정희진','주경원','이소령','김용섭','이아론','이승한','최영돈','이충성','정지영','장현준','이동근']

type_list = ['출장(일일)', '출장(일반)']
company_folder_path = './dataset/company'
kakao_folder_path = './dataset/kakao'



# 근태현황(구) 액셀파일 모두 가져오기
def process_company_data(folder_path, empno_list, type_list):
    warnings.simplefilter("ignore")
    # 해당 폴더 내의 모든 파일 리스트 가져오기
    file_list = os.listdir(folder_path)
    
    # 결과를 담을 빈 DataFrame 생성
    df_result = pd.DataFrame()
    
    # 각 파일에 대해 반복 수행
    for file_name in file_list:
        # 파일 경로 생성
        file_path = os.path.join(folder_path, file_name)
        
        # Excel 파일만 처리
        if file_path.endswith('.xlsx'):
            # Excel 파일을 DataFrame으로 읽기
            data = pd.read_excel(file_path)
            
            # 사번을 문자열로 변환
            data['사번'] = data['사번'].astype('str')


            # '시작일'과 '종료일'을 datetime 형식으로 변환
            data['시작일'] = pd.to_datetime(data['시작일'])
            data['종료일'] = pd.to_datetime(data['종료일'])

            # '출장 일수' 칼럼 추가
            data['출장일수'] = (data['종료일'] - data['시작일']).dt.days+1

            
            # 필터링
            df_filtered = data[(data['사번'].isin(empno_list)) & (data['근태유형'].isin(type_list))]
            
            # 필요한 열 선택
            df_filtered = df_filtered[['사번', '성명', '근태유형', '출장일수', '시작일', '종료일', '사유', '장소']]
            
            # 결과 DataFrame에 추가
            df_result = pd.concat([df_result, df_filtered])
    
    # 인덱스 재설정
    df_result.reset_index(drop=True, inplace=True)
    
    return df_result




# 카카오 거래내역 액셀파일 모두 가져오기
def process_kakao_data(folder_path):
    warnings.simplefilter("ignore")
    # 해당 폴더 내의 모든 파일 리스트 가져오기
    file_list = os.listdir(folder_path)
    
    # 결과를 담을 빈 DataFrame 생성
    df_result = pd.DataFrame()
    
    # 각 파일에 대해 반복 수행
    for file_name in file_list:

        # 파일 경로 생성
        file_path = os.path.join(folder_path, file_name)
        
        # Excel 파일만 처리
        if file_path.endswith('.xlsx'):
            # Excel 파일을 DataFrame으로 읽기
            data = pd.read_excel(file_path)
            
            
            # 내용 칼람을 문자열로 변환
            data['내용'] = data['내용'].astype('str')
            

            #거래금액, 거래후잔액을 int형으로 변환
            data['거래금액'] = data['거래금액'].str.replace(',', '').astype(int)
            data['거래 후 잔액'] = data['거래 후 잔액'].str.replace(',', '').astype(int)

             
            # 결과 DataFrame에 추가
            df_result = pd.concat([df_result, data])
    

    # 인덱스 재설정
    df_result.reset_index(drop=True, inplace=True)
    df_result = df_result[df_result['거래구분'] == '일반입금']
    
    return df_result



def filter_company_data(df, selected_year, selected_month, selected_name):
    filtered_df = df[(df['시작일'].dt.year == selected_year) & 
                     (df['시작일'].dt.month == selected_month) &
                     (df['성명'] == selected_name)]

    return filtered_df




###
def regular_money_function():

    # 현재 날짜와 시간을 가져옵니다.
    now = datetime.now()

    # 오늘 날짜를 YYYY-MM-DD 형식으로 출력합니다.
    today_date = now.strftime("%Y-%m-%d")

    # 문자열을 datetime 객체로 변환합니다.
    today_date_obj = datetime.strptime(today_date, "%Y-%m-%d")
    start_date_obj = datetime.strptime('2022-12-01', "%Y-%m-%d")

    # 두 날짜의 차이를 월 단위로 계산합니다.
    years_diff = today_date_obj.year - start_date_obj.year
    months_diff = today_date_obj.month - start_date_obj.month
    total_months_diff = years_diff * 12 + months_diff 

    regular_money = total_months_diff

    return regular_money


# def making_tables():
#     #필요한 df(근태, 카카오)
#     df_company = process_company_data(company_folder_path, empno_list, type_list)
#     df_kakao = process_kakao_data(kakao_folder_path)


#     df_days = df_company.groupby('사번')['출장일수'].sum().reset_index()

#     #껍데기
#     df_tmp = pd.DataFrame({'사번':empno_list,
#                           '이름':emp_nm_list,
#                           '정기회비':regular_money_function(),})
    

#     #근태 테이블 만들기
#     merged_df = pd.merge(df_tmp, df_days, on='사번', how='left')
#     merged_df['출장일수'] = merged_df['출장일수'].fillna(0)
#     merged_df['기타']=0


#     #미세조정
#     merged_df.loc[merged_df['이름'] == '김세훈', '기타'] = -1 #2212 정기부비 제외
#     merged_df.loc[merged_df['이름'] == '이소령', '기타'] = 5  #2302 문제검수반
#     merged_df.loc[merged_df['이름'] == '이충성', '기타'] = -3 #2303부터 근무
#     merged_df.loc[merged_df['이름'] == '정지영', '기타'] = -5  #2305 합류
#     merged_df.loc[merged_df['이름'] == '이승한', '기타'] = -13  #2401 합류
#     merged_df.loc[merged_df['이름'] == '이동근', '기타'] = -13  #2401 합류

#     merged_df['총_내야하는_돈'] = merged_df['출장일수']+merged_df['정기회비']+merged_df['기타']


#     #카카오 만들기
#     df_kakao_in = df_kakao[df_kakao['거래구분'] == '일반입금']

#     # 조정
#     df_kakao_in['내용'] = df_kakao_in['내용'].replace('주경원(KEITI출장)', '주경원')
#     df_kakao_in['내용'] = df_kakao_in['내용'].replace('김세훈(5월부비', '김세훈')

#     df_kakao_in_grouped = df_kakao_in.groupby('내용')['거래금액'].sum().reset_index()


#     #최종 합치기
#     result_df = pd.merge(merged_df, df_kakao_in_grouped, left_on='이름', right_on='내용', how='left')
#     result_df.drop(columns=['내용'], inplace=True)
#     result_df['거래금액'] = result_df['거래금액'].fillna(0)
#     result_df['카카오_입금액'] = result_df['거래금액']/10000
#     result_df.drop(columns=['거래금액'], inplace=True)

#     result_df['계산'] = result_df['총_내야하는_돈'] - result_df['카카오_입금액']

#     #비고란에 설명 넣기
#     result_df['비고']=''
#     result_df.loc[result_df['이름'] == '김세훈', '비고'] = '(기타 -1) 2023년 01월부터'
#     result_df.loc[result_df['이름'] == '이소령', '비고'] = '(기타 +5) 문제검수 참가비'
#     result_df.loc[result_df['이름'] == '이승한', '비고'] = '(기타 -13) 2024년 01월부터'
#     result_df.loc[result_df['이름'] == '이충성', '비고'] = '(기타 -3) 2024년 03월부터'
#     result_df.loc[result_df['이름'] == '정지영', '비고'] = '(기타 -5) 2024년 05월부터'
#     result_df.loc[result_df['이름'] == '이동근', '비고'] = '(기타 -13) 2024년 01월부터'

#     #퇴사자들 삭제
#     result_df = result_df.drop(result_df[result_df['이름'] == '주경원'].index)
#     result_df = result_df.drop(result_df[result_df['이름'] == '장현준'].index)


#     return result_df
