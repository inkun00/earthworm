import streamlit as st
import requests
import json
import random

# ------------------------------------------------------------
# 1) 이미지 URL 샘플 (프로필용으로 랜덤 선택)
# ------------------------------------------------------------
image_urls = [
    "https://th.bing.com/th/id/OIG4.sbvsXcpjpETlz2LO_4g6?w=1024&h=1024&rs=1&pid=ImgDetMain",
    "https://th.bing.com/th/id/OIG4.sbvsXcpjpETlz2LO_4g6?w=1024&h=1024&rs=1&pid=ImgDetMain",
    "https://th.bing.com/th/id/OIG4.fmafTjPZwEX17n9E4H49?pid=ImgGn",
    "https://th.bing.com/th/id/OIG4.fmafTjPZwEX17n9E4H49?pid=ImgGn",
    "https://th.bing.com/th/id/OIG4.0ugOUMKI2F1pZFRxpgfU?pid=ImgGn",
    "https://th.bing.com/th/id/OIG4.0ugOUMKI2F1pZFRxpgfU?pid=ImgGn",
    "https://th.bing.com/th/id/OIG4.fD.2uF_znryBJ9P_dlkH?pid=ImgGn",
    "https://th.bing.com/th/id/OIG4.fD.2uF_znryBJ9P_dlkH?pid=ImgGn",
    "https://th.bing.com/th/id/OIG3.fppMpx_V9bOB3msD.EbQ?w=1024&h=1024&rs=1&pid=ImgDetMain",
    "https://th.bing.com/th/id/OIG3.dMg4p1gEo.bpqfkgQyQr?w=1024&h=1024&rs=1&pid=ImgDetMain"
]

if "selected_image" not in st.session_state:
    st.session_state.selected_image = random.choice(image_urls)
selected_image = st.session_state.selected_image

# ------------------------------------------------------------
# 2) 세션에 대화 이력 초기화
# ------------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "user",
            "content": (
                "너는 지렁이야. 너의 이름은 너가 알아서 지어. "
                "너는 내 친구야. 다정한 말투로 대화해. 나에게 친한 말투로 반말을 사용해. "
                "대화는 2문장 이내로 간단하게 해. 지렁이는 습하고 기름진 땅을 좋아해. "
                "피부를 통해 산소를 빨아들여. 비가 오면 땅에 흙 속에 산소공급이 잘 이뤄지지 않아 "
                "숨을 쉬기 위해 땅 밖으로 나와. 하지만 헤매다 흙을 못찾으면 강한 햇볕에 말라 죽기도 해."
            )
        },
        {"role": "assistant", "content": "알겠어."},
        {"role": "assistant", "content": "안녕, 나는 지렁이야 나에 대해서 궁금한 것이 있니?"}
    ]

if "input_message" not in st.session_state:
    st.session_state.input_message = ""

# ------------------------------------------------------------
# 3) CompletionExecutor 정의 (외부 API 호출용)
# ------------------------------------------------------------
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
            "Accept": "text/event-stream"
        }

        with requests.post(
            self._host + "/testapp/v1/chat-completions/HCX-003",
            headers=headers,
            json=completion_request,
            stream=True
        ) as r:
            response_data = r.content.decode("utf-8")
            lines = response_data.split("\n")
            json_data = None
            for i, line in enumerate(lines):
                if line.startswith("event:result"):
                    next_line = lines[i + 1]  # "data:" 이후의 JSON 문자열
                    json_data = next_line[5:]
                    break

            if json_data:
                try:
                    chat_data = json.loads(json_data)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": chat_data["message"]["content"]}
                    )
                except json.JSONDecodeError as e:
                    print("JSONDecodeError:", e)
            else:
                print("JSON 데이터가 없습니다.")

# ------------------------------------------------------------
# 4) 챗봇 초기화
# ------------------------------------------------------------
completion_executor = CompletionExecutor(
    host="https://clovastudio.stream.ntruss.com",
    api_key="NTA0MjU2MWZlZTcxNDJiY6Yo7+BLuaAQ2B5+PgEazGquXEqiIf8NRhOG34cVQNdq",
    api_key_primary_val="DilhGClorcZK5OTo1QgdfoDQnBNOkNaNksvlAVFE",
    request_id="d1950869-54c9-4bb8-988d-6967d113e03f"
)

# ------------------------------------------------------------
# 5) 타이틀 및 전반적인 CSS 설정
# ------------------------------------------------------------
st.markdown('<h1 class="title">지렁이 챗봇</h1>', unsafe_allow_html=True)

st.markdown(f"""
    <style>
    /* ----------------------------------------
       전체 페이지 여백/패딩 제거
    ---------------------------------------- */
    body, .main, .block-container {{
        margin: 0;
        padding: 0;
    }}
    .stApp {{  /* Streamlit 전체 영역에서 스크롤 방지 */
        overflow: hidden;
    }}

    /* ----------------------------------------
       타이틀 (상단 고정, 높이 약 60px)
    ---------------------------------------- */
    .title {{
        font-size: 28px !important;
        font-weight: bold;
        text-align: center;
        line-height: 60px;   /* 세로 중앙 정렬 */
        height: 60px;        /* 딱 60px 높이 */
        background-color: #BACEE0;
        margin: 0;
        padding: 0;
    }}

    /* ----------------------------------------
       메시지 하나의 컨테이너
    ---------------------------------------- */
    .message-container {{
        display: flex;
        margin-bottom: 10px;
        align-items: center;
    }}
    .message-user {{
        background-color: #FFEB33 !important;
        color: #000;
        text-align: right;
        padding: 10px;
        border-radius: 10px;
        margin-left: auto;
        max-width: 60%;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }}
    .message-assistant {{
        background-color: #FFF !important;
        text-align: left;
        padding: 10px;
        border-radius: 10px;
        margin-right: auto;
        max-width: 60%;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }}
    .profile-pic {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 10px;
        flex-shrink: 0;
    }}

    /* ----------------------------------------
       채팅 영역 (chat-box)
       상단: 타이틀(60px) 바로 아래부터
       하단: 입력창(60px) 바로 위까지
       overflow-y: auto로 스크롤 처리
    ---------------------------------------- */
    .chat-box {{
        position: absolute;
        top: 60px;    /* 타이틀 높이 60px 만큼 내려옴 */
        bottom: 60px; /* 입력창 높이 60px 만큼 올라옴 */
        left: 0;
        right: 0;
        padding: 20px;
        overflow-y: auto; /* 내용이 넘칠 때만 세로 스크롤 */
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        background-color: #BACEE0;
    }}
    /* 스크롤바가 너무 두껍게 나오면, 아래 스타일을 조정하세요 */
    .chat-box::-webkit-scrollbar {{
        width: 6px;
    }}
    .chat-box::-webkit-scrollbar-thumb {{
        background-color: rgba(0,0,0,0.2);
        border-radius: 3px;
    }}
    .chat-box::-webkit-scrollbar-track {{
        background-color: rgba(255,255,255,0.1);
    }}

    /* ----------------------------------------
       입력창 (input-container)
       position: absolute; bottom: 0 으로 고정
       높이 60px, z-index: 10으로 채팅박스 위에 렌더링
    ---------------------------------------- */
    .input-container {{
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 60px;
        background-color: #BACEE0;
        padding: 10px 20px;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
        z-index: 10;  /* 채팅박스보다 위에 표시 */
    }}
    /* 입력창 안의 텍스트 필드 높이 맞추기 */
    .stTextInput > div > div > input {{
        height: 40px;
        width: 100%;
    }}
    /* 전송 버튼 높이/너비 맞추기 */
    .stButton button {{
        height: 40px !important;
        width: 70px !important;
        padding: 0 10px;
        margin-right: 0 !important;
    }}
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# 6) 채팅 메시지를 보여주는 영역 시작
# ------------------------------------------------------------
st.markdown('<div class="chat-box">', unsafe_allow_html=True)

def send_message():
    if st.session_state.input_message:
        user_message = st.session_state.input_message
        st.session_state.chat_history.append(
            {"role": "user", "content": user_message}
        )
        # 외부 API 호출
        completion_request = {
            "messages": st.session_state.chat_history,
            "topP": 0.8,
            "topK": 0,
            "maxTokens": 256,
            "temperature": 0.7,
            "repeatPenalty": 1.2,
            "stopBefore": [],
            "includeAiFilters": True,
            "seed": 0
        }
        completion_executor.execute(completion_request)
        st.session_state.input_message = ""

# 초기 3개 메시지 이후부터 화면에 렌더링
for message in st.session_state.chat_history[3:]:
    role = "User" if message["role"] == "user" else "Chatbot"
    profile_url = selected_image if role == "Chatbot" else None
    message_class = "message-user" if role == "User" else "message-assistant"

    if role == "Chatbot":
        st.markdown(f'''
            <div class="message-container">
                <img src="{profile_url}" class="profile-pic" alt="프로필 이미지" />
                <div class="{message_class}">
                    {message["content"]}
                </div>
            </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
            <div class="message-container">
                <div class="{message_class}">
                    {message["content"]}
                </div>
            </div>
        ''', unsafe_allow_html=True)

# 채팅박스 닫기
st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# 7) 입력창 및 전송 버튼 (항상 화면 맨 아래에 고정)
# ------------------------------------------------------------
st.markdown('<div class="input-container">', unsafe_allow_html=True)
with st.form(key="input_form", clear_on_submit=True):
    cols = st.columns([7.5, 1])
    with cols[0]:
        user_message = st.text_input("메시지를 입력하세요:", key="input_message", placeholder="")
    with cols[1]:
        submit_button = st.form_submit_button(label="전송", on_click=send_message)
st.markdown('</div>', unsafe_allow_html=True)
