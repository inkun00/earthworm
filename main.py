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
        r = requests.post(
            self._host + "/testapp/v1/chat-completions/HCX-003",
            headers=headers,
            json=completion_request,
            stream=True,
            timeout=60,
        )

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
# 페이지 스타일 (버튼 간격 최소화)
# --------------------------------------------------
st.markdown(
    """
    <style>
    body, .main, .block-container { background-color: #BACEE0 !important; }
    .title { font-size: 28px !important; font-weight: bold; text-align: center; padding-top: 10px; }
    .message-container { display: flex; margin-bottom: 10px; align-items: center; }
    .message-user { background-color: #FFEB33; color: black; text-align: right;
        padding: 10px; border-radius: 10px; margin-left: auto; max-width: 60%;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .message-assistant { background-color: #FFFFFF; text-align: left;
        padding: 10px; border-radius: 10px; margin-right: auto; max-width: 60%;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .profile-pic { width: 40px; height: 40px; border-radius: 50%; margin-right: 10px; }
    .chat-box { background-color: #BACEE0; border: none; padding: 20px;
        border-radius: 10px; max-height: 400px; overflow-y: scroll; margin: 0 auto; width: 80%; }
    .stTextInput > div > div > input { height: 38px; width: 100%; }
    .input-container { position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #BACEE0; padding: 10px; box-shadow: 0 -2px 5px rgba(0,0,0,0.1); }
    div[data-testid="column"] { padding-left: 2px !important; padding-right: 2px !important; }
    .stButton button { height: 38px; width: 70px; padding: 0 10px; margin: 0 !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

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
# 입력창 및 버튼 (가로로 한 줄, 딱 붙여서!)
# --------------------------------------------------
st.markdown('<div class="input-container">', unsafe_allow_html=True)
with st.form("input_form", clear_on_submit=True):
    user_input = st.text_input("메시지를 입력하세요:", key="input_message")
    col1, col2 = st.columns([1, 1])
    with col1:
        send = st.form_submit_button("전송")
    with col2:
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
    assistant_text = completion_executor.execute(req)

    def _norm(text):
        return re.sub(r"\s+", " ", text.strip())
    last_assistant = next(
        (m["content"] for m in reversed(st.session_state.chat_history[:-1]) if m["role"] == "assistant"),
        "",
    )
    if assistant_text and _norm(assistant_text) != _norm(last_assistant):
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_text})
    st.rerun()

# --------------------------------------------------
# '복사' 처리
# --------------------------------------------------
if copy:
    lines = st.session_state.chat_history[3:]
    st.session_state.copied_chat_history = "\n".join(f"{m['role']}: {m['content']}" for m in lines)

# --------------------------------------------------
# 복사된 대화 내용 표시
# --------------------------------------------------
if st.session_state.copied_chat_history:
    st.markdown("### 대화 내용 정리")
    st.text_area("", value=st.session_state.copied_chat_history, height=200)
