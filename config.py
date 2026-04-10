#config.py
import os
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
from datetime import timezone, timedelta

KST = timezone(timedelta(hours=9))

GOOGLE_NEWS_RSS_SEARCH_URL = "https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"

ALLOWED_SOURCES = [
    "전기신문",
    "에너지데일리",
    "에너지경제",
    "에너지프로슈머",
    "임팩트온",
    "이투뉴스",
    "투데이에너지",
    "에너지경제신문",
    "에너지신문",
    "에너지플랫폼뉴스",
    "전자신문",
    "뉴스1",
    "환경일보",
    "연합뉴스",
    "한국경제",
    "매일경제",
    "서울경제",
    "머니투데이",
]

STOCK_EXCLUDE_KEYWORDS = [
    "목표주가",
    "주가",
    "급등",
    "급락",
    "상승",
    "하락",
    "투자의견",
    "매수",
    "매도",
    "증권사",
    "리포트",
    "수혜주",
    "관련주",
    "컨센서스",
    "밸류에이션",
]

LOCAL_EXCLUDE_KEYWORDS = [
    "시의원",
    "도의원",
    "시의회",
    "도의회",
    "공공청사",
    "어린이",
    "챌린지",
    "체험관",
    "발대식",
    "행사",
    "특별강연",
    "캘린더",
    "조례",
    "구청",
    "시청",
    "군청",
    "교육",
    "봉사",
    "대회",
    "축제",
    "주민",
    "시민",
    "지역사회",
    "개관",
    "캠페인",
]

FOREIGN_KEYWORDS = [
    "미국", "일본", "호주", "유럽", "EU",
    "중국", "베트남", "인도", "러시아", "중동",
    "아프리카", "브라질", "멕시코", "캐나다", "싱가포르",
    "태국", "인도네시아", "말레이시아", "필리핀",
    "대만", "홍콩", "몽골", "사우디", "UAE", "두바이",
]

ALLOWED_FOREIGN_KEYWORDS = [
    "미국", "일본", "호주", "유럽", "EU", "중국", "중동"
]

KEYWORDS = [
    "그리드위즈 OR Gridwiz",
    "수요반응 OR 플러스DR OR 전력수요관리 OR 수요관리",

    # K-충전, 충전CPO 추가
    "전기차 충전 OR 전기자동차 OR EV 충전 OR V2G OR 충전인프라 OR K-충전 OR 충전사업자 OR 충전CPO",

    "재생에너지 OR 신재생에너지 OR 태양광 OR 풍력",

    # 광역정전 추가
    "전력시장 OR 전력계통 OR 전력시스템 OR 전력거래소 OR 계통안정화 OR 정전 OR 대규모정전",

    "ESS OR 에너지저장장치 OR BESS OR 배터리에너지저장장치", "그리드포밍"
    "가상발전소 OR VPP OR 분산에너지 OR 분산자원",
    "전기요금 OR PPA OR 기후부","김성환","기후부장관"
    "배출권거래제 OR ETS",
    "AI 데이터센터 OR 데이터센터 OR 전력수요",
    "출력제한 OR 계통 포화 OR 저수요 고발전 OR 송배전망 OR 접속지연",
    "P2X OR 잉여전력 OR 전력저장",
    "산단공 OR 산업단지 OR 탄소중립 산단",
    "배터리 제조사 OR 배터리 인증 OR 인증 취소",
    "기후정책 OR 탄소정책 OR 에너지정책",
    "해상풍력 OR 육상풍력 OR 재생에너지 입찰",

    # RE100 특별법, 산단 조합 추가
    "RE100 OR 직접 PPA OR 기업 PPA OR RE100 특별법 OR RE100 산단",

    # 신규: 수소 (수소발전 입찰 커버)
    "수소발전 OR 수소입찰 OR 청정수소 OR 수소법 OR 수소경제",

    # 신규: 에너지 기관/협회/포럼
    "전기산업연합회 OR 에너지전환포럼 OR 대한전기협회 OR 전기협회",
]

TRUSTED_SOURCES = [
    "전기신문",
    "전자신문",
    "연합뉴스",
    "뉴스1",
    "한국경제",
    "매일경제",
    "서울경제",
    "머니투데이",
    "이투뉴스",
    "에너지경제신문",
    "투데이에너지",
    "에너지신문",
    "에너지데일리",
    "에너지프로슈머",
    "임팩트온",
]

TOP_NEWS_MIN = 0
TOP_NEWS_MAX = 2

MARKET_SNAPSHOT_MIN = 5
MARKET_SNAPSHOT_MAX = 20

CLUSTER_SIMILARITY_THRESHOLD = 0.25