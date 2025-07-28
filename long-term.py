import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import matplotlib.font_manager as fm

# ✅ 한글폰트 설정 (윈도우 기본 폰트인 Malgun Gothic 사용)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ✅ 측정 데이터 입력 (월, 함량)
months = np.array([0, 3, 6, 9, 12])  # 최대 36개월까지 입력 가능
lot1 = np.array([98, 97, 96, 95, 95])
lot2 = np.array([99, 98, 97, 96, 95])
lot3 = np.array([97, 96, 95, 94, 94])

# ✅ 모든 데이터 로트로 저장
lots = {
    '로트1': lot1,
    '로트2': lot2,
    '로트3': lot3,
    '평균': np.mean([lot1, lot2, lot3], axis=0)
}

LCL = 95  # 하한선 (%)
confidence = 0.95  # 신뢰수준

# ✅ 유효기한 추정 함수
def estimate_shelf_life(x, y, label):
    result = linregress(x, y)
    slope = result.slope
    intercept = result.intercept
    stderr = result.stderr

    # 신뢰구간 반영 (간단히 2*표준오차 보정)
    if slope < 0:
        adjusted_slope = slope + 2 * stderr if confidence == 0.95 else slope + 1.64 * stderr
    else:
        adjusted_slope = slope  # 기울기가 양수일 땐 보정하지 않음

    # 유효기한 계산
    if adjusted_slope == 0:
        shelf_life = np.inf
    else:
        shelf_life = (LCL - intercept) / adjusted_slope
        if shelf_life < 0:
            shelf_life = 0

    return result, shelf_life

# ✅ 그래프 그리기
plt.figure(figsize=(12, 8))

colors = ['#F08080', "#6488ED", 'green', 'black']
for i, (label, data) in enumerate(lots.items()):
    slope_info, shelf = estimate_shelf_life(months, data, label)
    predicted = slope_info.slope * months + slope_info.intercept
    plt.plot(months, data, 'o', color=colors[i], label=f"{label} 측정값")
    plt.plot(months, predicted, '-', color=colors[i], label=f"{label} 추세선\n(유효기한: {shelf:.1f}개월)")
plt.legend()
plt.xlim(0, 36)
plt.ylim(80, 120)
plt.xticks(np.arange(0, 37, 3))
plt.legend(loc='upper left', bbox_to_anchor=(0.58, 1), ncol=2)
LCL = 95  # 하한선
UCL = 105  # 상한선 (원하는 값으로 조정)

plt.axhline(LCL, color='red', linestyle='--', linewidth=2, label='하한선 95%')
plt.axhline(UCL, color='red', linestyle='--', linewidth=2, label='상한선 105')
plt.title('안정성시험 결과 및 유효기한 추정')
plt.xlabel('보관 기간 (개월)')
plt.ylabel('함량 (%)')
plt.grid(True)
plt.show()