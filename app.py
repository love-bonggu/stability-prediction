import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import matplotlib

# ✅ 한글 폰트 설정 (NanumGothic) 사용 - 시스템에 설치되어 있어야 함
matplotlib.rcParams['font.family'] = 'NanumGothic'
matplotlib.rcParams['axes.unicode_minus'] = False

# ✅ Streamlit 앱 시작
def main():
    st.title("📊 유효기한 예측 앱")
    st.markdown("안정성시험 데이터를 입력하면 각 로트의 유효기한을 추정합니다.")

    st.subheader("🔢 데이터 입력")

    # ✅ 사용자 입력값
    month_str = st.text_input("📆 측정 개월 (쉼표로 구분)", "0, 3, 6, 9, 12")
    lot1_str = st.text_input("🧪 로트1 실험값", "98, 97, 96, 95, 95")
    lot2_str = st.text_input("🧪 로트2 실험값", "99, 98, 97, 96, 95")
    lot3_str = st.text_input("🧪 로트3 실험값", "97, 96, 95, 94, 94")

    LCL = st.number_input("🔻 하한선 (%)", value=95)
    UCL = st.number_input("🔺 상한선 (%)", value=105)
    conf_level = st.selectbox("📈 신뢰수준", options=["95%", "90%"], index=0)

    if conf_level == "95%":
        z_factor = 2.0
    else:
        z_factor = 1.64

    try:
        # ✅ 문자열 → 배열 변환
        months = np.array([int(x.strip()) for x in month_str.split(",")])
        lot1 = np.array([float(x.strip()) for x in lot1_str.split(",")])
        lot2 = np.array([float(x.strip()) for x in lot2_str.split(",")])
        lot3 = np.array([float(x.strip()) for x in lot3_str.split(",")])
        lots = {
            '로트1': lot1,
            '로트2': lot2,
            '로트3': lot3,
            '평균': np.mean([lot1, lot2, lot3], axis=0)
        }

        # ✅ 유효기한 계산 함수
        def estimate_shelf_life(x, y, label):
            result = linregress(x, y)
            slope = result.slope
            intercept = result.intercept
            stderr = result.stderr

            if slope < 0:
                adjusted_slope = slope + z_factor * stderr
                shelf_life = (LCL - intercept) / adjusted_slope
                shelf_life = max(shelf_life, 0)
                note = ""
            else:
                shelf_life = np.inf
                note = "(통계적 의미 없음)"

            return result, shelf_life, note

        # ✅ 그래프
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#F08080', "#6488ED", 'green', 'black']
        shelf_life_results = {}

        for i, (label, data) in enumerate(lots.items()):
            result, shelf, note = estimate_shelf_life(months, data, label)
            predicted = result.slope * months + result.intercept

            ax.plot(months, data, 'o', color=colors[i], label=f"{label} 측정값")
            ax.plot(months, predicted, '-', color=colors[i],
                    label=f"{label} 추세선\n(유효기한: {'∞' if shelf == np.inf else f'{shelf:.1f}'}개월 {note})")

            shelf_life_results[label] = (shelf, note)

        ax.axhline(LCL, color='red', linestyle='--', linewidth=2, label='하한선')
        ax.axhline(UCL, color='red', linestyle='--', linewidth=2, label='상한선')
        ax.set_xlim(0, 36)
        ax.set_ylim(80, 120)
        ax.set_xticks(np.arange(0, 37, 3))
        ax.set_xlabel('보관 기간 (개월)')
        ax.set_ylabel('함량 (%)')
        ax.set_title('안정성시험 결과 및 유효기한 추정')
        ax.grid(True)
        ax.legend(loc='upper left', bbox_to_anchor=(0.58, 1), ncol=2)

        st.pyplot(fig)

        # ✅ 유효기한 결과 출력
        st.subheader("📌 유효기한 요약")
        for label, (shelf, note) in shelf_life_results.items():
            if shelf == np.inf:
                st.write(f"✅ **{label}** → ∞개월 {note}")
            else:
                st.write(f"✅ **{label}** → **{shelf:.1f}개월** {note}")

    except Exception as e:
        st.error(f"❌ 데이터 입력 오류: {e}")

# ✅ 실행
if __name__ == "__main__":
    main()
