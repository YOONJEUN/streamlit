import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib

df = pd.read_csv("./HR Data.csv")
hr = df.copy()

# 퇴직 여부를 0과 1로 변환
hr['퇴직'] = hr['퇴직여부'].map({'No': 0, 'Yes': 1}).astype('int8')

# 연령대 생성
hr['연령대'] = pd.cut(
    hr['나이'],
    bins=[0, 29, 39, 49, 59, 100],
    labels=['20대 이하', '30대', '40대', '50대', '60대 이상']
)

hr['근속구간'] = pd.cut(
    hr['근속연수'],
    bins=[-1, 2, 5, 10, 100],
    labels=['2년 이하', '3-5년', '6-10년', '11년 이상']
)

hr['월급여구간'] = pd.qcut(
    hr['월급여'],
    q = 4, # 쿼터. 4구간으로 나누기
    labels=['하위 25%', '25~50%', '50~75%', '상위 25%']
)

# KPI 3개
total_employees = len(hr)
total_attritions = hr['퇴직'].sum()
overall_rate = round(hr['퇴직'].mean() * 100 , 1)

col1, col2, col3 = st.columns(3)
col1.metric(label="직원수", value=f"{total_employees}명", delta="+1명")
col2.metric(label="총퇴직자수", value=f"{total_attritions:,}명", delta="-300명")
col3.metric(label="전체 퇴직률", value=f"{overall_rate:.1f}%", delta="-1.2%")


# 사이드바 필터
st.sidebar.title("조회 조건")

dept = st.sidebar.selectbox("부서를 선택하세요:", ["전체"] + list(hr['부서'].unique()))

min_tenure, max_tenure = st.sidebar.slider("근속연수를 선택하세요", 
                                         min_value=0, max_value=hr['근속연수'].max(), value=(0, hr['근속연수'].max()), step=1)

# 데이터 필터링
if dept != "전체": # 전체가 아니면 , 개발부나 영업부인거니까  해당하는 부서만 필터링
    hr = hr[hr["부서"] == dept]

hr = hr[(hr["근속연수"] >= min_tenure) & (hr["근속연수"] <= max_tenure)]

def attritions_summary(data, group_column) :
    result = data.groupby(group_column, observed=True).agg(직원수 = ('퇴직', 'size'),
                                    퇴직자수 = ('퇴직', 'sum'),
                                      퇴직률 = ('퇴직', 'mean')).reset_index()

    result['퇴직률'] = (result['퇴직률'] * 100).round(1)
    return result.sort_values('퇴직률', ascending=False)

department_result = attritions_summary(hr, '부서')
age_result = attritions_summary(hr, '연령대')
tenure_result = attritions_summary(hr, '근속구간')
overtime_result = attritions_summary(hr, '야근정도')
travel_result = attritions_summary(hr, '출장빈도')
income_result = attritions_summary(hr, '월급여구간')

# 2행 3열 그래프 생성
fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# 1. 부서별 퇴직률
ax1 = sns.barplot(data=department_result, y='부서', x='퇴직률', ax=axes[0, 0])
axes[0, 0].axvline(overall_rate, color='red', linestyle='--')
axes[0, 0].set_title('부서별 퇴직률')
axes[0, 0].set_xlabel('퇴직률(%)')

# 2. 연령대별 퇴직률
ax2 = sns.barplot(data=age_result, x='연령대', y='퇴직률', ax=axes[0, 1])
axes[0, 1].axhline(overall_rate, color='red', linestyle='--')
axes[0, 1].set_title('연령대별 퇴직률')
axes[0, 1].set_ylabel('퇴직률(%)')

# 3. 근속구간별 퇴직률
ax3 = sns.barplot(data=tenure_result, x='근속구간', y='퇴직률', ax=axes[0, 2])
axes[0, 2].axhline(overall_rate, color='red', linestyle='--')
axes[0, 2].set_title('근속구간별 퇴직률')
axes[0, 2].set_ylabel('퇴직률(%)')

# 4. 야근 여부별 퇴직률
ax4 = sns.barplot(data=overtime_result, x='야근정도', y='퇴직률', ax=axes[1, 0])
axes[1, 0].axhline(overall_rate, color='red', linestyle='--')
axes[1, 0].set_title('야근 여부별 퇴직률')
axes[1, 0].set_ylabel('퇴직률(%)')

# 5. 출장 빈도별 퇴직률
ax5 = sns.barplot(data=travel_result, x='출장빈도', y='퇴직률', ax=axes[1, 1])
axes[1, 1].axhline(overall_rate, color='red', linestyle='--')
axes[1, 1].set_title('출장 빈도별 퇴직률')
axes[1, 1].set_ylabel('퇴직률(%)')
axes[1, 1].tick_params(axis='x', rotation=15)

# 6. 월급여 구간별 퇴직률
ax6 = sns.barplot(data=income_result, x='월급여구간', y='퇴직률', ax=axes[1, 2])
axes[1, 2].axhline(overall_rate, color='red', linestyle='--')
axes[1, 2].set_title('월급여 구간별 퇴직률')
axes[1, 2].set_ylabel('퇴직률(%)')

st.pyplot(fig)

fig.suptitle('HR 퇴직 현황 대시보드', fontsize=21, fontweight='bold')

plt.tight_layout()
plt.savefig('HR_퇴직현황_대시보드.png', dpi=150, bbox_inches='tight')
plt.show()