import streamlit as st
import requests
import json
import random
import re

# --------------------------------------------------
# Github RAW 이미지 사용
# --------------------------------------------------
image_urls = [
    f"https://raw.githubusercontent.com/inkun00/earthworm/main/image/image{i}.png"
    for i in range(1, 10)
]

if "selected_image" not in st.session_state:
    st.session_state.selected_image = random.choice(image_urls)
bot_profile_url = st.session_state.selected_image

# --------------------------------------------------
# 대화 기록 초기화
# --------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "system",
            "content": (
                "너는 지렁이야. 너의 이름은 너가 알아서 지어. "
                "너는 내 친구야. 다정한 말투로 대화해. 나에게 친한 말투로 반말을 사용해. "
                "대화는 2문장 이내로 간단하게 해. 지렁이는 습하고 기름진 땅을 좋아해. "
                "피부를 통해 산소를 빨아들여. 비가 오면 흙 속 산소가 부족해져서 "
                "숨 쉬려고 땅 밖으로 나오는데, 흙을 못 찾으면 강한 햇볕에 말라 죽기도 해."
            ),
        },
        {"role": "assistant", "content": "알겠어."},
        {
            "role": "assistant",
            "content": "안녕! 나는 지렁이야. 궁금한 거 있니?",
        },
    ]

if "copied_chat_history" not in st.session_state:
    st.session_state.copied_chat_history = ""

# --------------------------------------------------
# 스트리밍 응답 합치기용 실행기
# --------------------------------------------------
class CompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val, request_id):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id

    def execute(self, completion_request):
        headers = {
            "X-NCP-CLOVASTUDIO-API-KEY": self._api_key,
            "X-NCP-APIGW-API-KEY": self._api_key_primary_val,
            "X-NCP-CLOVASTUDIO-REQUEST-ID": self._request_id,
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/event-stream",
        }
        try:
            r = requests.post(
                self._host + "/testapp/v1/chat-completions/HCX-003",
                headers=headers,
                json=completion_request,
                stream=True,
                timeout=60,
            )
            r.raise_for_status()  # HTTP 오류 발생 시 예외 처리

            full_response = ""
            for raw_line in r.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue
                line = raw_line.strip()
                if not line.startswith("data:"):
                    continue
                data_str = line[5:].strip()
                if data_str == "[DONE]":
                    break

                try:
                    chunk = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                delta = chunk.get("message", {}).get("content", "")
                if delta:
                    # 일부 모델은 전체 응답을 누적해서 보내는 경우가 있음
                    if delta.startswith(full_response):
                        full_response = delta
                    else:
                        full_response += delta
            
            return full_response.strip()

        except requests.exceptions.RequestException as e:
            st.error(f"API 요청 중 오류 발생: {e}")
            return "미안, 지금은 대답하기 어려워. 흙 속에서 잠시 쉬어야겠어."
        except Exception as e:
            st.error(f"응답 처리 중 알 수 없는 오류 발생: {e}")
            return "지금 뭔가 문제가 생겼나 봐. 다시 시도해 줄래?"


# --------------------------------------------------
# 클로바 스튜디오 실행기
# --------------------------------------------------
completion_executor = CompletionExecutor(
    host="https://clovastudio.stream.ntruss.com",
    api_key="NTA0MjU2MWZlZTcxNDJiY6Yo7+BLuaAQ2B5+PgEazGquXEqiIf8NRhOG34cVQNdq",
    api_key_primary_val="DilhGClorcZK5OTo1QgdfoDQnBNOkNaNksvlAVFE",
    request_id="d1950869-54c9-4bb8-988d-6967d113e03f",
)

# --------------------------------------------------
# 페이지 스타일 (카카오톡 스타일)
# --------------------------------------------------
st.markdown(
    """
    <style>
    /* --- 전체 배경 --- */
    body, .main, .block-container {
        background-color: #BACEE0 !important;
    }
    
    /* --- 타이틀 --- */
    .title {
        font-size: 28px !important;
        font-weight: bold;
        text-align: center;
        padding-top: 10px;
        color: #000;
    }
    
    /* --- 채팅 메시지 영역 --- */
    .chat-box {
        background-color: #BACEE0; /* 배경과 동일한 색 */
        border: none;
        padding: 20px;
        padding-bottom: 120px; /* 하단 입력창을 위한 여백 */
        border-radius: 10px;
        max-height: 65vh; /* 화면 높이의 65% */
        overflow-y: scroll;
        margin: 0 auto;
        width: 100%; /* 모바일/PC 대응을 위해 100%로 설정 (컨테이너가 중앙 정렬) */
    }
    
    /* --- 메시지 한 줄(프로필+말풍선) 컨테이너 --- */
    .message-container {
        display: flex;
        margin-bottom: 10px;
        align-items: flex-start; /* 프로필 사진 상단 정렬 */
    }
    
    /* --- 사용자(나) 말풍선 --- */
    .message-user {
        background-color: #FEE500; /* 카카오 노란색 */
        color: #3C1E1E; /* 카카오 텍스트 브라운 */
        text-align: left; /* 말풍선 내 텍스트는 좌측 정렬 */
        padding: 10px 12px;
        border-radius: 10px 0px 10px 10px; /* 뾰족한 꼬리 느낌 */
        margin-left: auto; /* 우측 정렬 */
        max-width: 65%;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        word-wrap: break-word; /* 긴 텍스트 줄바꿈 */
    }
    
    /* --- 봇(상대) 말풍선 --- */
    .message-assistant {
        background-color: #FFFFFF;
        color: #000000;
        text-align: left;
        padding: 10px 12px;
        border-radius: 0px 10px 10px 10px; /* 뾰족한 꼬리 느낌 */
        margin-right: auto; /* 좌측 정렬 */
        max-width: 65%;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        word-wrap: break-word;
    }
    
    /* --- 봇 프로필 사진 --- */
    .profile-pic {
        width: 40px;
        height: 40px;
        border-radius: 15px; /* 카카오톡 프로필 (동근 사각형) */
        margin-right: 10px;
    }
    
    /* --- 하단 입력창 컨테이너 --- */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #FFFFFF; /* 입력창 배경은 흰색 */
        padding: 10px 10%; /* 좌우 여백 (채팅창과 맞춤) */
        box-shadow: 0 -2px 5px rgba(0,0,0,0.05);
        box-sizing: border-box; /* 패딩을 너비에 포함 */
    }
    
    /* --- 텍스트 입력 필드 --- */
    .stTextInput > div > div > input {
        height: 38px;
        width: 100%;
        background-color: #F5F5F5; /* 카톡 입력창 회색 */
        border: none;
        border-radius: 5px;
        padding-left: 10px;
    }
    
    /* --- 입력창 내부 컬럼 간격 --- */
    div[data-testid="column"] {
        padding-left: 5px !important;
        padding-right: 5px !important;
    }
    
    /* --- 전송/복사 버튼 --- */
    .stButton button {
        height: 38px;
        width: 100%; /* 컬럼 너비 꽉 채우기 */
        padding: 0 10px;
        margin: 0 !important;
        background-color: #FEE500; /* 카카오 노란색 */
        color: #3C1E1E;
        border: none;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #F0D900;
        color: #3C1E1E;
    }
    
    /* '복사' 버튼만 회색으로 만들기 (조금 복잡한 선택자) */
    div[data-testid="column"]:nth-of-type(3) .stButton button {
        background-color: #F0F0F0;
        color: #555;
    }
    div[data-testid="column"]:nth-of-type(3) .stButton button:hover {
        background-color: #E0E0E0;
        color: #333;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 페이지 레이아웃
# --------------------------------------------------
st.markdown('<h1 class="title">지렁이와 대화나누기</h1>', unsafe_allow_html=True)

# --------------------------------------------------
# 대화 내역 표시
# --------------------------------------------------
st.markdown('<div class="chat-box">', unsafe_allow_html=True)
for msg in st.session_state.chat_history[3:]:
    if msg["role"] == "user":
        st.markdown(
            f"""
            <div class="message-container">
                <div class="message-user">{msg['content']}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="message-container">
                <img src="{bot_profile_url}" class="profile-pic" alt="프로필">
                <div class="message-assistant">{msg['content']}</div>
            </div>""",
            unsafe_allow_html=True,
        )
st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# 복사된 대화 내용 표시 (입력창 위로 이동)
# --------------------------------------------------
if st.session_state.copied_chat_history:
    st.markdown("### 대화 내용 정리")
    st.text_area("", value=st.session_state.copied_chat_history, height=200)

# --------------------------------------------------
# 입력창 및 버튼 (가로 정렬)
# --------------------------------------------------
st.markdown('<div class="input-container">', unsafe_allow_html=True)
with st.form("input_form", clear_on_submit=True):
    # 컬럼을 사용해 텍스트 입력창과 버튼을 가로로 배치
    col1, col2, col3 = st.columns([0.75, 0.125, 0.125])  # 비율로 너비 조절
    with col1:
        user_input = st.text_input(
            "메시지를 입력하세요:",
            key="input_message",
            label_visibility="collapsed",  # 레이블 숨기기
            placeholder="메시지를 입력하세요...",  # placeholder 텍스트
        )
    with col2:
        send = st.form_submit_button("전송")
    with col3:
        copy = st.form_submit_button("복사")
st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# '전송' 처리
# --------------------------------------------------
if send and user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    req = {
        "messages": st.session_state.chat_history,
        "topP": 0.8,
        "topK": 0,
        "maxTokens": 256,
        "temperature": 0.7,
        "repeatPenalty": 1.2,
        "stopBefore": [],
        "includeAiFilters": True,
        "seed": 0,
    }
    
    # 응답 대기 중 스피너 표시
    with st.spinner("지렁이가 꿈틀꿈틀 생각 중..."):
        assistant_text = completion_executor.execute(req)

    def _norm(text):
        return re.sub(r"\s+", " ", text.strip())

    last_assistant = next(
        (
            m["content"]
            for m in reversed(st.session_state.chat_history[:-1])
            if m["role"] == "assistant"
        ),
        "",
    )
    if assistant_text and _norm(assistant_text) != _norm(last_assistant):
        st.session_state.chat_history.append(
            {"role": "assistant", "content": assistant_text}
        )
    
    # 대화 내용 복사 기록은 초기화
    if st.session_state.copied_chat_history:
        st.session_state.copied_chat_history = ""
        
    st.rerun()

# --------------------------------------------------
# '복사' 처리
# --------------------------------------------------
if copy:
    lines = st.session_state.chat_history[3:]
    st.session_state.copied_chat_history = "\n".join(
        f"{'나' if m['role'] == 'user' else '지렁이'}: {m['content']}" for m in lines
    )
    st.rerun()

# '복사된 대화 내용 표시' 섹션은 위로 이동했으므로 여기서는 제거됨
