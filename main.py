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
            r.raise_for_status()

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
# 페이지 스타일 (position: fixed 사용)
# --------------------------------------------------
st.markdown(
    """
    <style>
    /* --- 1. 페이지 전체 배경 --- */
    body, .main, div[data-testid="stAppViewContainer"] {
        background-color: #BACEE0 !important;
    }
    
    /* --- 2. 메인 컨텐츠 영역 (가운데 정렬) --- */
    .block-container {
        background-color: #BACEE0 !important;
        /* max-width는 Streamlit 기본값을 따름 */
    }

    /* --- 3. 타이틀 --- */
    .title {
        font-size: 24px !important;
        font-weight: bold;
        text-align: center;
        padding: 15px 10px 10px 10px;
        color: #000;
    }
    
    /* --- 4. 채팅창 --- */
    .chat-box {
        background-color: #BACEE0;
        padding: 10px 20px 0 20px;
        width: 100%;
        box-sizing: border-box;
        
        /* ★★★ 핵심 ★★★ */
        /* 화면 높이에서 타이틀, 입력창 높이를 대략 뺀 값 */
        height: 75vh; 
        overflow-y: auto; /* ★ 스크롤 */
        
        /* ★ 입력창에 가려지지 않도록 하단에 충분한 여백 */
        padding-bottom: 120px; 
    }
    
    /* --- 5. 복사 영역 (채팅창 내부) --- */
    h3[data-testid="stHeading"] {
        padding-top: 10px;
        font-size: 16px;
    }
    div[data-testid="stTextArea"] textarea { 
        height: 150px !important; 
    }
    
    /* --- 6. 입력창 --- */
    .input-container {
        /* ★★★ 핵심 ★★★ */
        position: fixed; /* 화면에 고정 */
        bottom: 0;       /* 화면 맨 아래에 */
        
        /* Streamlit의 .block-container 너비와 맞춤 */
        left: 50%; 
        transform: translateX(-50%);
        max-width: 730px; /* Streamlit 기본 centered 너비 */
        width: 100%;      /* 부모 너비에 맞춤 */

        background-color: #FFFFFF;
        padding: 10px 20px;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.05);
        box-sizing: border-box;
    }
    .input-container div[data-testid="stForm"] {
        padding: 0 !important;
    }

    /* --- 7. 메시지 말풍선 스타일 --- */
    .message-container { display: flex; margin-bottom: 10px; align-items: flex-start; }
    .message-user { background-color: #FEE500; color: #3C1E1E; padding: 10px 12px; border-radius: 10px 0px 10px 10px; margin-left: auto; max-width: 65%; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); word-wrap: break-word; }
    .message-assistant { background-color: #FFFFFF; color: #000000; padding: 10px 12px; border-radius: 0px 10px 10px 10px; margin-right: auto; max-width: 65%; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); word-wrap: break-word; }
    .profile-pic { width: 40px; height: 40px; border-radius: 15px; margin-right: 10px; }
    
    /* --- 8. 입력 필드/버튼 스타일 --- */
    .stTextInput > div > div > input { height: 38px; width: 100%; background-color: #F5F5F5; border: none; border-radius: 5px; padding-left: 10px; }
    div[data-testid="column"] { padding-left: 5px !important; padding-right: 5px !important; }
    .stButton button { height: 38px; width: 100%; padding: 0 10px; margin: 0 !important; background-color: #FEE500; color: #3C1E1E; border: none; border-radius: 5px; font-weight: bold; }
    .stButton button:hover { background-color: #F0D900; color: #3C1E1E; }
    div[data-testid="column"]:nth-of-type(3) .stButton button { background-color: #F0F0F0; color: #555; }
    div[data-testid="column"]:nth-of-type(3) .stButton button:hover { background-color: #E0E0E0; color: #333; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 페이지 레이아웃 (순서 변경)
# --------------------------------------------------

# --- (Row 1) 타이틀 ---
st.markdown('<h1 class="title">지렁이와 대화나누기</h1>', unsafe_allow_html=True)

# --- (Row 2) 대화 내역 (스크롤 영역) ---
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

# --- (Moved) 복사된 대화 내용 (채팅창 내부에 표시) ---
if st.session_state.copied_chat_history:
    st.markdown("### 대화 내용 정리")
    st.text_area(
        "", 
        value=st.session_state.copied_chat_history, 
        height=150, 
        label_visibility="collapsed"
    )
st.markdown("</div>", unsafe_allow_html=True) # chat-box 닫기


# --- (Row 3) 입력창 (화면 하단 고정) ---
st.markdown('<div class="input-container">', unsafe_allow_html=True)
with st.form("input_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([0.75, 0.125, 0.125])
    with col1:
        user_input = st.text_input(
            "메시지를 입력하세요:",
            key="input_message",
            label_visibility="collapsed",
            placeholder="메시지를 입력하세요...",
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
