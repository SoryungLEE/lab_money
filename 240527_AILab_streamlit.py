import pandas as pd
import numpy as np
import streamlit as st
from utils import *

# Set page configuration
st.set_page_config(page_title="AI연구센터 부비확인", layout="wide")

# Load data frames
df_company = process_company_data(company_folder_path, empno_list, type_list)
df_kakao = process_kakao_data(kakao_folder_path)
# full_table= making_tables()
regular_money = regular_money_function()
out_person = False

# Main layout
col1, col2, col3 = st.columns([1, 8, 1])
with col2:
    st.title('AI연구센터 부비확인')

    st.divider()

    check_name = st.selectbox("이름 선택", emp_nm_list, index=None, key='check_name')
    if check_name:
        col1, col2 = st.columns(2)
        with col1:
            st.write('출장 내역입니다.')
            df_company_personal = df_company[df_company['성명']==check_name]
            st.write(df_company_personal)

        with col2:
            st.write('카카오 통장 입금내역입니다.')
            df_kakao_personal = df_kakao[(df_kakao['거래구분']=='일반입금') & (df_kakao['내용']==check_name)]
            st.write(df_kakao_personal)

        count_days = sum(df_company_personal['출장일수'].astype(int))
        kakao_money = sum(df_kakao_personal['거래금액'])


        if check_name=='김성훈':  #8만원 보냄(24.6 기준 오버된 금액)
            kakao_money-=(5*10000)
        if check_name=='김세훈':
            regular_money -=1 
        if check_name=='이충성':
            regular_money -=3
        if check_name=='정지영':
            regular_money -=5
        if check_name=='이승한':
            regular_money -=13
        if check_name=='이동근':
            regular_money -=13
        if check_name=='이소령':
            count_days+=5
        if check_name=='정희진':
            kakao_money-=75000 #부비대신 사비로 긁어서 재입금했음
            st.write("(참고) 카카오 통장 입금내역에는 75,000이 있지만, 실제 계산할때는 제외했습니다.")
        if check_name=='주경원':
            out_person = True
        if check_name=='장현준':
            out_person = True

        must_pay =  (count_days + regular_money)*10000

        if out_person:
            st.write('퇴사자입니다.')

        else :
            st.write(f"{check_name}님의 출장일은 총 {count_days}일이고, 정기회비는 {regular_money*10000}원 입니다.")
            st.write(f"부비로 내야하는 돈은 {must_pay}원 이며,")
            st.write(f"모임통장 입금액은 {kakao_money}원 입니다.")

            if must_pay > kakao_money:
                st.write(f"따라서 {check_name}님은 {must_pay-kakao_money}만큼 부비를 더 내야합니다.")
            elif must_pay == kakao_money:
                st.write(f"차액이 0이므로 아주 잘하고 있습니다bb")
            else:
                st.write("차액을 돌려받거나 해당 일 수만큼 나중에 입금하시기 바랍니다.")


    # st.divider()

    # st.write('<현재까지 전체 부비확인>')
    # st.markdown("""['기타'] 칼람 설명   
    #         (김세훈 -1) 23년 01월부터 시작    
    #         (이충성 -3) 23년 03월부터 시작    
    #         (정지영 -5) 23년 05월부터 시작   
    #         (이승한 -13) 24년 01월부터 시작   
    #         (이동근 -13) 24년 01월부터 시작   
    #         (이소령 +5) 23년 02월 문제검수반   
    #         """
    #     )


    # full_table= making_tables()
    # st.write(full_table)
    # st.dataframe(full_table, height=600, width=1000)


    # st.divider()
    # st.write('#### 참고 조회')
    # on_1 = st.checkbox('근태 조회하기', key='attendance')
    # if on_1:
    #     with st.container():
    #         col1, col2, col3 = st.columns(3)
    #         with col1: 
    #             selected_year = st.selectbox("원하는 연도를 선택하세요:", range(2022, 2025), key='attendance_year')
    #         with col2: 
    #             selected_month = st.selectbox("원하는 월을 선택하세요:", range(1, 13), key='attendance_month')
    #         with col3: 
    #             selected_name = st.selectbox("원하는 이름을 선택하세요:", emp_nm_list, index=None, key='attendance_name', placeholder="이름을 선택하세요. 선택하지 않으면 해당하는 년/월의 전체 데이터를 불러옵니다.")
    #         st.write("")
    #         with col3: 
    #             search_button = st.button("검색", key='attendance_search')

    #         if search_button:
    #             # Filter data based on selection
    #             filtered_data = filter_company_data(df_company, selected_year, selected_month, selected_name)

    #             if not filtered_data.empty:
    #                 st.write(f"{selected_name}님의 출장내역입니다.")
    #                 st.write(filtered_data)
    #             else:
    #                 st.write("해당하는 데이터가 없습니다.")
    #                 pre_filtered_data = df_company[(df_company['시작일'].dt.year == selected_year) & 
    #                                                 (df_company['시작일'].dt.month == selected_month)]
                    
    #                 if not pre_filtered_data.empty:
    #                     st.write(f"{selected_year}년 {selected_month}월의 전체 출장 기록을 불러옵니다.")
    #                     st.write(pre_filtered_data)
    #                 else:
    #                     st.write("해당하는 기간의 데이터가 없습니다.")

    # on_2 = st.checkbox('카카오 뱅크 내역 보기', key='payment')
    # if on_2:
        
    #     selected_name = st.selectbox("원하는 이름을 선택하세요:", emp_nm_list, index=None, key='attendance_name', placeholder="이름을 선택하세요. 선택하지 않으면 전체 입금내역을 불러옵니다.")

    #     filtered_data = df_kakao[(df_kakao['거래구분']=='일반입금') & (df_kakao['내용']==emp_nm_list)]

    #     if not filtered_data.empty:
    #         st.write(f"{selected_name}님의 전체 입금내역입니다.")
    #         st.write(filtered_data)

    #     else:
    #         st.write("전체 입금내역입니다.")
    #         df_kakao_in = df_kakao[(df_kakao['거래구분']=='일반입금')]
    #         st.write(df_kakao_in)

