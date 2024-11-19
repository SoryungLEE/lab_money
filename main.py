import pandas as pd
import streamlit as st
from utils import *

# Set page configuration
st.set_page_config(page_title="AI연구센터 부비확인", layout="wide")

# Load data frames
df_company = process_company_data(company_folder_path, empno_list, type_list)
df_kakao = process_kakao_data(kakao_folder_path)
regular_money = regular_money_function()

# Main layout
col1, col2, col3 = st.columns([1, 8, 1])
with col2:
    st.title('AI연구센터 부비확인')
    st.divider()

    st.write('### 개인별 조회')
    check_name = st.selectbox("이름 선택", emp_nm_list, index=None, key='check_name')
    if check_name:
        col1, col2 = st.columns(2)
        with col1:
            st.write('출장 내역입니다.')
            df_company_personal = df_company[df_company['성명'] == check_name]
            st.write(df_company_personal)

        with col2:
            st.write('카카오 통장 입금내역입니다.')
            df_kakao_personal = df_kakao[df_kakao['내용'] == check_name]
            st.write(df_kakao_personal)

        count_days = df_company_personal['출장일수'].sum()
        kakao_money = df_kakao_personal['거래금액'].sum()

        count_days, kakao_money, regular_money, out_person = apply_adjustments(check_name, count_days, kakao_money, regular_money)

        must_pay = (count_days + regular_money) * 10000

        if out_person:
            st.write('퇴사자입니다.')
        else:
            st.write(f"{check_name}님의 출장일은 총 {count_days}일이고, 정기회비는 {format_currency(regular_money * 10000)}원 입니다.")
            st.write(f"부비로 내야하는 돈은 {format_currency(must_pay)}원 이며, 모임통장 입금액은 {format_currency(kakao_money)}원 입니다.")
            if must_pay > kakao_money:
                st.write(f"따라서 {check_name}님은 {format_currency(must_pay - kakao_money)}만큼 부비를 더 내야합니다.")
            elif must_pay == kakao_money:
                st.write("차액이 0이므로 아주 잘하고 있습니다bb")
            else:
                st.write("차액을 돌려받거나 해당 일 수만큼 나중에 입금하시기 바랍니다.")

