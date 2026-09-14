import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 페이지 기본 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

# 앱 제목 및 소개
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.markdown("KOBIS 일별 박스오피스 데이터를 바탕으로 시간 흐름에 따른 관객수 변화를 분석합니다.")

# 1. 데이터 로드 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
    df = pd.read_csv(url)
    
    # YYYYMMDD 형태의 숫자/문자열 날짜를 실제 datetime 객체로 변환
    df['날짜'] = pd.to_datetime(df['날짜'].astype(str), format='%Y%m%d')
    
    # 수치형 데이터 변환
    numeric_cols = ['순위', '일관객', '누적관객', '스크린수', '상영횟수']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

st.divider()

# ==========================================
# 구역 1: 개별 영화 일관객 변화
# ==========================================
st.header("📌 1. 영화별 일일 관객수 추이")

# 관객수 총합 기준으로 영화 목록 정렬하여 드롭다운 생성
movie_list = df.groupby('영화명')['일관객'].sum().sort_values(ascending=False).index.tolist()
selected_movie = st.selectbox("분석할 영화를 선택하세요:", movie_list)

if selected_movie:
    # 선택된 영화 데이터 필터링 및 날짜순 정렬
    movie_df = df[df['영화명'] == selected_movie].sort_values('날짜')
    
    # Plotly 선 그래프 작성
    fig1 = px.line(
        movie_df,
        x='날짜',
        y='일관객',
        title=f"'{selected_movie}' 날짜별 일관객수 변화",
        labels={'날짜': '날짜', '일관객': '일일 관객수(명)'},
        markers=True,
        custom_data=['순위', '누적관객']
    )
    
    # 마우스 오버(Hover) 시 툴팁 설정
    fig1.update_traces(
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<br><b>순위:</b> %{customdata[0]}위<br><b>누적관객:</b> %{customdata[1]:,}명<extra></extra>"
    )
    fig1.update_layout(
        xaxis_title="날짜",
        yaxis_title="일일 관객수",
        hovermode="x unified",
        template="plotly_white"
    )
    
    # Streamlit 화면에 플롯 출력
    st.plotly_chart(fig1, use_container_width=True)
    
    # 그래프 해설/문구 자리
    st.info(f"💡 **이 그래프로 알 수 있는 것:** {selected_movie}의 개봉 초기 관객 집중도와 주말/평일 관객수 변동 패턴을 한눈에 파악할 수 있습니다.")

st.divider()

# ==========================================
# 구역 2: 상위 5개 영화 일관객 비교
# ==========================================
st.header("📌 2. 기간 내 관객수 상위 5개 영화의 일별 관객수 비교")

# 전체 기간 일관객 합계 상위 5개 영화 선정
top5_movies = df.groupby('영화명')['일관객'].sum().nlargest(5).index.tolist()
top5_df = df[df['영화명'].isin(top5_movies)].sort_values('날짜')

# 상위 5개 영화 선 그래프 작성 (영화명으로 색상 구분)
fig2 = px.line(
    top5_df,
    x='날짜',
    y='일관객',
    color='영화명',
    title="기간 내 관객수 TOP 5 영화의 날짜별 일관객수 추이",
    labels={'날짜': '날짜', '일관객': '일일 관객수(명)', '영화명': '영화 제목'},
    markers=True,
    custom_data=['순위', '누적관객']
)

fig2.update_traces(
    hovertemplate="<b>%{fullData.name}</b><br>날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<br>순위: %{customdata[0]}위<extra></extra>"
)

fig2.update_layout(
    xaxis_title="날짜",
    yaxis_title="일일 관객수",
    hovermode="x unified",
    template="plotly_white",
    legend=dict(
        title="영화 제목 (클릭하여 ON/OFF)",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig2, use_container_width=True)

# 그래프 해설/문구 자리
st.info("💡 **이 그래프로 알 수 있는 것:** 기간 내 가장 흥행한 상위 5개 영화의 개봉 시기별 최고 관객수 전개 양상과 경쟁 구도를 한눈에 비교할 수 있습니다.")

st.divider()

# ==========================================
# 구역 3: 날짜별 Top 10 관객수 합계 영역 그래프
# ==========================================
st.header("📌 3. 일별 박스오피스 Top 10 총 관객수 추이 (영역 그래프)")

# 날짜별 10위권 관객수 합계 집계
daily_total = df.groupby('날짜')['일관객'].sum().reset_index().sort_values('날짜')

# 관객수가 가장 컸던 상위 3일 선별
top3_days = daily_total.nlargest(3, '일관객')

# Plotly 영역 그래프 생성 (px.area)
fig3 = px.area(
    daily_total,
    x='날짜',
    y='일관객',
    title="날짜별 박스오피스 Top 10 총 관객수 합계",
    labels={'날짜': '날짜', '일관객': 'Top 10 총 관객수(명)'}
)

fig3.update_traces(
    line_color='#1f77b4',
    fillcolor='rgba(31, 119, 180, 0.3)',
    hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>Top 10 총 관객수:</b> %{y:,}명<extra></extra>"
)

# 상위 3일에 빨간색 마커와 날짜/관객수 텍스트 표시
for idx, row in top3_days.iterrows():
    date_str = row['날짜'].strftime('%Y-%m-%d')
    audience_str = f"{int(row['일관객']):,}명"
    
    fig3.add_trace(go.Scatter(
        x=[row['날짜']],
        y=[row['일관객']],
        mode='markers+text',
        marker=dict(color='red', size=10),
        text=[f"🏆 {date_str}<br>({audience_str})"],
        textposition="top center",
        name="최고 관객수 Top 3",
        showlegend=False,
        hovertemplate=f"<b>최고 관객수일</b><br>날짜: {date_str}<br>관객수: {audience_str}<extra></extra>"
    ))

fig3.update_layout(
    xaxis_title="날짜",
    yaxis_title="Top 10 총 관객수",
    hovermode="x unified",
    template="plotly_white"
)

st.plotly_chart(fig3, use_container_width=True)

# 그래프 해설/문구 자리
st.info("💡 **이 그래프로 알 수 있는 것:** 전체 영화 시장의 성수기/비수기 흐름과 특정 명절·연휴 등 극장가 관객 동원력이 가장 높았던 상위 3일을 직관적으로 확인할 수 있습니다.")

st.divider()

# ==========================================
# 구역 4: 기간 내 누적 관객수 TOP 10 영화 (가로 막대)
# ==========================================
st.header("📌 4. 기간 내 총 관객수 TOP 10 영화")

# 영화별 총 관객수 및 10위권 차트인 일수 집계
top10_summary = df.groupby('영화명').agg(
    총관객수=('일관객', 'sum'),
    차트인일수=('날짜', 'nunique')
).reset_index()

# 총 관객수 기준 TOP 10 추출
top10_summary = top10_summary.nlargest(10, '총관객수')
top10_summary = top10_summary.sort_values('총관객수', ascending=True)

fig4 = px.bar(
    top10_summary,
    x='총관객수',
    y='영화명',
    orientation='h',
    title="기간 내 총 관객수 TOP 10 영화 (가로 막대)",
    labels={'총관객수': '기간 내 총 관객수(명)', '영화명': '영화 제목'},
    custom_data=['차트인일수'],
    color='총관객수',
    color_continuous_scale='Blues'
)

fig4.update_traces(
    hovertemplate="<b>영화명:</b> %{y}<br><b>총 관객수:</b> %{x:,}명<br><b>10위권 차트인 일수:</b> %{customdata[0]}일<extra></extra>",
    texttemplate="%{x:,}명",
    textposition="outside"
)

fig4.update_layout(
    xaxis_title="기간 내 총 관객수",
    yaxis_title="영화 제목",
    yaxis=dict(categoryorder="total ascending"),
    coloraxis_showscale=False,
    template="plotly_white"
)

st.plotly_chart(fig4, use_container_width=True)

# 그래프 해설/문구 자리
st.info("💡 **이 그래프로 알 수 있는 것:** 해당 기간 동안 가장 많은 관객을 끌어모은 최고 흥행작 TOP 10 순위와 각 영화가 Box Office 10위권 내에 방영·유지되었던 일수를 비교 분석할 수 있습니다.")

st.divider()

# ==========================================
# 구역 5: 월×요일별 일관객 합계 히트맵
# ==========================================
st.header("📌 5. 월×요일별 관객수 집계 히트맵")

# 날짜 데이터에서 월과 요일 추출
heatmap_df = df.copy()
heatmap_df['월'] = heatmap_df['날짜'].dt.month.astype(str) + "월"
heatmap_df['요일'] = heatmap_df['날짜'].dt.day_name()

# 요일 한글 변환 및 월요일~일요일 순서 정렬 지정
day_map = {
    'Monday': '월요일',
    'Tuesday': '화요일',
    'Wednesday': '수요일',
    'Thursday': '목요일',
    'Friday': '금요일',
    'Saturday': '토요일',
    'Sunday': '일요일'
}
day_order = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
heatmap_df['요일'] = heatmap_df['요일'].map(day_map)

# 월(1월~12월) 정렬 순서 준비
month_order = [f"{i}월" for i in range(1, 13)]

# 월 x 요일 피벗 테이블 생성 (일관객 합계)
pivot_df = heatmap_df.pivot_table(
    index='월',
    columns='요일',
    values='일관객',
    aggfunc='sum',
    fill_value=0
)

# 지정한 월/요일 순서대로 재정렬
pivot_df = pivot_df.reindex(index=month_order, columns=day_order).fillna(0)

# Plotly imshow 히트맵 생성 (진한 색상이 높은 관객수를 의미)
fig5 = px.imshow(
    pivot_df,
    labels=dict(x="요일", y="월", color="총 관객수"),
    x=day_order,
    y=month_order,
    color_continuous_scale="YlOrRd", # 관객수가 많을수록 붉고 진한 색상
    title="월×요일별 관객수 합계 히트맵"
)

fig5.update_traces(
    hovertemplate="<b>%{y} %{x}</b><br>총 관객수: %{z:,}명<extra></extra>"
)

fig5.update_layout(
    xaxis_title="요일",
    yaxis_title="월",
    template="plotly_white"
)

st.plotly_chart(fig5, use_container_width=True)

# 그래프 해설/문구 자리
st.info("💡 **이 그래프로 알 수 있는 것:** 연중 어떤 월(Month)과 무슨 요일(Day)의 조합에 극장 관객이 가장 집중되었는지(예: 주말/연휴/특수 시즌) 한눈에 분석할 수 있습니다.")

st.divider()

# ==========================================
# 구역 6: 추후 그래프 추가용 영역
# ==========================================
st.header("📌 6. 신규 그래프 (추가 예정)")
st.caption("※ 향후 스크린수 대비 관객수 효율성 등 추가 시계열 분석 그래프가 들어갈 자리입니다.")
