# --------------------------------------------------
# 페이지 스타일 (입력창 배경 변경)
# --------------------------------------------------
st.markdown(
    """
    <style>
    /* --- 1. 부모 요소들 높이 100% 강제 --- */
    html, body, #root, div[data-testid="stAppViewContainer"], .main {
        height: 100% !important;
        background-color: #BACEE0 !important;
    }

    /* --- 2. 메인 컨텐츠 영역 (Flexbox 프레임) --- */
    div[data-testid="stAppViewContainer"] > .main .block-container {
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        padding: 0 !important;
        margin: 0 auto !important;
        background-color: #BACEE0 !important; 
        max-width: 730px !important; 
    }

    /* --- 3. (Row 1) 타이틀 --- */
    .title {
        flex-shrink: 0 !important; /* ★ 프레임 고정 */
        font-size: 24px !important;
        font-weight: bold;
        text-align: center;
        padding: 15px 10px 10px 10px !important;
        color: #000 !important;
    }
    
    /* --- 4. (Row 2) 채팅창 --- */
    .chat-box {
        flex-grow: 1 !important; /* ★ 프레임 (남는 공간 모두 차지) */
        overflow-y: auto !important; /* ★ 스크롤 */
        background-color: #BACEE0 !important;
        padding: 10px 20px 0 20px !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
    
    /* --- 5. (Optional) 복사 영역 CSS 제거 --- */
    
    /* --- 6. (Row 3) 입력창 --- */
    .input-container {
        flex-shrink: 0 !important; /* ★ 프레임 고정 */
        
        /* ★★★ 수정된 부분 ★★★ */
        background-color: #BACEE0 !important; /* 배경색을 하늘색으로 */
        box-shadow: none !important; /* 그림자 제거 */
        
        padding: 10px 20px !important;
        box-sizing: border-box !important;
        width: 100% !important;
    }
    .input-container div[data-testid="stForm"] {
        padding: 0 !important;
    }

    /* --- 7. 메시지 말풍선 --- */
    .message-container { display: flex; margin-bottom: 10px; align-items: flex-start; }
    .message-user { background-color: #FEE500 !important; color: #3C1E1E !important; padding: 10px 12px; border-radius: 10px 0px 10px 10px; margin-left: auto; max-width: 65%; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); word-wrap: break-word; }
    .message-assistant { background-color: #FFFFFF !important; color: #000000 !important; padding: 10px 12px; border-radius: 0px 10px 10px 10px; margin-right: auto; max-width: 65%; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); word-wrap: break-word; }
    .profile-pic { width: 40px; height: 40px; border-radius: 15px; margin-right: 10px; }
    
    
    /* --- 8. 입력 필드/버튼 --- */
    .stTextInput > div > div > input {
        /* ★★★ 수정된 부분 ★★★ */
        background-color: #FFFFFF !important; /* 입력 상자 흰색 */
        border: none !important;
    }
    
    /* ★ '전송' 버튼 강제 스타일 */
    div[data-testid="column"]:nth-of-type(2) .stButton button {
        /* ★★★ 수정된 부분 ★★★ */
        background-color: #FFFFFF !important; /* 전송 버튼 흰색 */
        color: #3C1E1E !important; /* 글자색 검정/갈색 */
        border: none !important;
        font-weight: bold !important;
    }
    div[data-testid="column"]:nth-of-type(2) .stButton button:hover {
        background-color: #F0F0F0 !important; /* 호버 시 회색 */
        color: #3C1E1E !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)
