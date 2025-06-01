import streamlit as st
import requests
import json
import random

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

# 처음 실행 시, 이미지 선택을 한 번만 실행하도록 설정
if "selected_image" not in st.session_state:
    st.session_state.selected_image = random.choice(image_urls)

selected_image = st.session_state.selected_image

# Streamlit의 세션 상태를 사용하여 대화 내용을 저장
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            'role': 'user',
            'content': (
                '너는 지렁이야. 너의 이름은 너가 알아서 지어. '
                '너는 내 친구야. 다정한 말투로 대화해. 나에게 친한 말투로 반말을 사용해. '
                '대화는 2문장 이내로 간단하게 해. 지렁이는 습하고 기름진 땅을 좋아해. '
                '피부를 통해 산소를 빨아들여. 비가 오면 땅에 흙 속에 산소공급이 잘 이뤄지지 않아 '
                '숨을 쉬기 위해 땅 밖으로 나와. 하지만 헤매다 흙을 못찾으면 강한 햇볕에 말라 죽기도 해.'
            )
        },
        {'role': 'assistant', 'content': '알겠어.'},
        {'role': 'assistant', 'content': '안녕, 나는 지렁이야 나에 대해서 궁금한 것이 있니?'}
    ]

if "input_message" not in st.session_state:
    st.session_state.input_message = ""

class CompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val, request_id):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id

    def execute(self, completion_request):
        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }

        with requests.post(
            self._host + '/testapp/v1/chat-completions/HCX-003',
            headers=headers,
            json=completion_request,
            stream=True
        ) as r:
            response_data = r.content.decode('utf-8')
            lines = response_data.split("\n")
            json_data = None
            for i, line in enumerate(lines):
                if line.startswith("event:result"):
                    next_line = lines[i + 1]  # "data:" 이후의 문자열
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


# Initialize the chat bot
completion_executor = CompletionExecutor(
    host='https://clovastudio.stream.ntruss.com',
    api_key='NTA0MjU2MWZlZTcxNDJiY6Yo7+BLuaAQ2B5+PgEazGquXEqiIf8NRhOG34cVQNdq',
    api_key_primary_val='DilhGClorcZK5OTo1QgdfoDQnBNOkNaNksvlAVFE',
    request_id='d1950869-54c9-4bb8-988d-6967d113e03f'
)

# 제목 표시
st.markdown('<h1 class="title">지렁이 챗봇</h1>', unsafe_allow_html=True)

# 프로필 이미지 URL 정의
bot_profile_url = selected_image

# 스타일 정의: 채팅박스가 flex container가 되어 위쪽부터 메시지가 쌓이도록 설정
st.markdown(f"""
    <style>
    body, .main, .block-container {{
        background-color: #BACEE0 !important;
    }}
    .title {{
        font-size: 28px !important;
        font-weight: bold;
        text-align: center;
        margin-top: 10px;
    }}
    .message-container {{
        display: flex;
        margin-bottom: 10px;
        align-items: center;
    }}
    .message-user {{
        background-color: #FFEB33 !important;
        color: black;
        text-align: right;
        padding: 10px;
        border-radius: 10px;
        margin-left: auto;
        max-width: 60%;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
    }}
    .message-assistant {{
        background-color: #FFFFFF !important;
        text-align: left;
        padding: 10px;
        border-radius: 10px;
        margin-right: auto;
        max-width: 60%;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
    }}
    .profile-pic {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 10px;
    }}
    .chat-box {{
        /* flex container로 만들어서 위쪽부터 쌓이도록 처리 */
        display: flex;
        flex-direction: column;
        justify-content: flex-start;

        background-color: #BACEE0 !important;
        border: none;
        padding: 20px;
        border-radius: 10px;

        width: 80%;
        margin: 20px auto;

        height: 400px;        /* 원하는 높이(px)로 조절하세요 */
        overflow-y: auto;     /* 내용이 넘치면 세로 스크롤바 표시 */
    }}
    .stTextInput > div > div > input {{
        height: 38px;
        width: 100%;
    }}
    .stButton button {{
        height: 38px !important;
        width: 70px !important;
        padding: 0px 10px;
        margin-right: 0px !important;
    }}
    /* 입력창을 하단에 고정 */
    .input-container {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #BACEE0;
        padding: 10px;
        box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);
    }}
    </style>
""", unsafe_allow_html=True)

# → 채팅 메시지를 담을 박스 시작
st.markdown('<div class="chat-box">', unsafe_allow_html=True)

def send_message():
    if st.session_state.input_message:
        user_message = st.session_state.input_message
        st.session_state.chat_history.append({"role": "user", "content": user_message})

        completion_request = {
            'messages': st.session_state.chat_history,
            'topP': 0.8,
            'topK': 0,
            'maxTokens': 256,
            'temperature': 0.7,
            'repeatPenalty': 1.2,
            'stopBefore': [],
            'includeAiFilters': True,
            'seed': 0
        }
        completion_executor.execute(completion_request)
        st.session_state.input_message = ""  # 입력 필드 비우기

# 대화 내용 표시 (초기 3개 메시지 이후부터)
for message in st.session_state.chat_history[3:]:
    role = "User" if message["role"] == "user" else "Chatbot"
    profile_url = bot_profile_url if role == "Chatbot" else None
    message_class = 'message-user' if role == "User" else 'message-assistant'

    if role == "Chatbot":
        st.markdown(f'''
            <div class="message-container">
                <img src="{profile_url}" class="profile-pic" alt="프로필 이미지">
                <div class="{message_class}">
                    {message["content"]}
                </div>
            </div>''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
            <div class="message-container">
                <div class="{message_class}">
                    {message["content"]}
                </div>
            </div>''', unsafe_allow_html=True)

# 채팅 박스 닫기
st.markdown('</div>', unsafe_allow_html=True)

# 입력창 및 전송 버튼
st.markdown('<div class="input-container">', unsafe_allow_html=True)
with st.form(key="input_form", clear_on_submit=True):
    cols = st.columns([7.5, 1])
    with cols[0]:
        user_message = st.text_input("메시지를 입력하세요:", key="input_message", placeholder="")
    with cols[1]:
        submit_button = st.form_submit_button(label="전송", on_click=send_message)
st.markdown('</div>', unsafe_allow_html=True)
