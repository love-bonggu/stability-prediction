import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

# ✅ 한글 폰트 설정 (윈도우용)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ✅ Streamlit 앱 시작
def main():
    st.title("유효기한 예측 앱")
    st.markdown("안정성시험 결과를 기반으로 각 로트의 유효기한을 추정합니다.")

    # ✅ 측정 데이터
    months = np.array([0, 3, 6, 9, 12])
    lot1 = np.array([98, 97, 96, 95, 95])
    lot2 = np.array([99, 98, 97, 96, 95])
    lot3 = np.array([97, 96, 95, 94, 94])
    lots = {
        '로트1': lot1,
        '로트2': lot2,
        '로트3': lot3,
        '평균': np.mean([lot1, lot2, lot3], axis=0)
    }

    # ✅ 설정값
    LCL = 95
    UCL = 105
    confidence = 0.95

    # ✅ 유효기한 계산 함수
    def estimate_shelf_life(x, y, label):
        result = linregress(x, y)
        slope = result.slope
        intercept = result.intercept
        stderr = result.stderr

        if slope < 0:
            adjusted_slope = slope + 2 * stderr if confidence == 0.95 else slope + 1.64 * stderr
        else:
            adjusted_slope = slope

        if adjusted_slope == 0:
            shelf_life = np.inf
        else:
            shelf_life = (LCL - intercept) / adjusted_slope
            shelf_life = max(shelf_life, 0)

        return result, shelf_life

    # ✅ 그래프 그리기
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#F08080', "#6488ED", 'green', 'black']

    shelf_life_results = {}

    for i, (label, data) in enumerate(lots.items()):
        result, shelf = estimate_shelf_life(months, data, label)
        predicted = result.slope * months + result.intercept

        ax.plot(months, data, 'o', color=colors[i], label=f"{label} 측정값")
        ax.plot(months, predicted, '-', color=colors[i], label=f"{label} 추세선\n(유효기한: {shelf:.1f}개월)")

        shelf_life_results[label] = shelf

    ax.axhline(LCL, color='red', linestyle='--', linewidth=2, label='하한선 95%')
    ax.axhline(UCL, color='red', linestyle='--', linewidth=2, label='상한선 105%')
    ax.set_xlim(0, 36)
    ax.set_ylim(80, 120)
    ax.set_xticks(np.arange(0, 37, 3))
    ax.set_xlabel('보관 기간 (개월)')
    ax.set_ylabel('함량 (%)')
    ax.set_title('안정성시험 결과 및 유효기한 추정')
    ax.grid(True)
    ax.legend(loc='upper left', bbox_to_anchor=(0.58, 1), ncol=2)

    st.pyplot(fig)

    # ✅ 유효기한 요약 표시
    st.subheader("예측된 유효기한 요약")
    for label, shelf in shelf_life_results.items():
        st.write(f"📌 **{label}** → **{shelf:.1f}개월**")

# ✅ 실행
if __name__ == "__main__":
    main()
