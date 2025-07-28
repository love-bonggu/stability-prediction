import os
import urllib.request
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from scipy import stats
import streamlit as st

# ✅ Nanum Gothic 폰트 다운로드 및 설정
FONT_PATH = "/tmp/NanumGothic.ttf"
FONT_URL = "https://github.com/naver/nanumfont/blob/master/TTF/NanumGothic.ttf?raw=true"

if not os.path.exists(FONT_PATH):
    urllib.request.urlretrieve(FONT_URL, FONT_PATH)

plt.rcParams['font.family'] = fm.FontProperties(fname=FONT_PATH).get_name()
plt.rcParams['axes.unicode_minus'] = False

# ✅ Streamlit UI
st.set_page_config(page_title="유효기한 예측 도구", layout="centered")
st.title("📈 의약품 유효기한 예측 도구")

st.markdown("안정성시험 데이터를 입력하세요. **3개 로트**의 값을 넣고 평균을 기준으로 예측합니다.")

# ✅ 사용자 입력
months = st.text_input("시험 개월 (쉼표로 구분)", "0,3,6,9,12,18,24,36")
lot1 = st.text_input("로트1 실측값", "100.0,98.1,96.2,95.8,94.7,92.3,90.1,88.4")
lot2 = st.text_input("로트2 실측값", "100.0,98.3,96.6,95.5,94.2,92.0,90.5,88.0")
lot3 = st.text_input("로트3 실측값", "100.0,98.0,96.3,95.6,94.5,92.1,90.4,88.2")
limit = st.number_input("허용 하한 (%)", min_value=0.0, max_value=100.0, value=90.0)
conf = st.selectbox("신뢰수준", ["90%", "95%"])

# ✅ 버튼 클릭 시 실행
if st.button("🔍 유효기한 예측"):
    try:
        # 입력값 처리
        x = np.array([float(i) for i in months.split(",")])
        y1 = np.array([float(i) for i in lot1.split(",")])
        y2 = np.array([float(i) for i in lot2.split(",")])
        y3 = np.array([float(i) for i in lot3.split(",")])
        y_avg = (y1 + y2 + y3) / 3

        # 회귀 분석
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y_avg)

        alpha = 0.10 if conf == "90%" else 0.05
        t_val = stats.t.ppf(1 - alpha / 2, df=len(x) - 2)
        y_pred = intercept + slope * x
        se = np.sqrt(np.sum((y_avg - y_pred) ** 2) / (len(x) - 2))
        mean_x = np.mean(x)
        conf_interval = t_val * se * np.sqrt(1 / len(x) + (x - mean_x) ** 2 / np.sum((x - mean_x) ** 2))
        lower = y_pred - conf_interval
        upper = y_pred + conf_interval

        # 유효기한 계산
        if slope >= 0:
            result_text = "∞개월 (통계적 의미 없음)"
        else:
            t = (limit - intercept - t_val * se * np.sqrt(1 / len(x) + (0 - mean_x) ** 2 / np.sum((x - mean_x) ** 2))) / slope
            if t < 0:
                result_text = "0개월 (기준 초과)"
            else:
                result_text = f"{t:.1f}개월"

        st.success(f"✅ **예측 유효기한: {result_text}**")

        # 그래프
        fig, ax = plt.subplots()
        ax.plot(x, y_avg, 'o-', label='평균 실측값')
        ax.plot(x, y_pred, 'r--', label='회귀선')
        ax.fill_between(x, lower, upper, color='pink', alpha=0.3, label=f'{conf} 신뢰구간')
        ax.axhline(limit, color='gray', linestyle=':', label='허용 하한')
        ax.set_title("유효기한 예측 회귀분석")
        ax.set_xlabel("개월")
        ax.set_ylabel("성분함량 (%)")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
