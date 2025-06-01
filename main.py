import streamlit as st
import requests
import json
import random

# 예시 프로필 이미지 URL 목록
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

# 앱 실행 시 처음 한 번만 프로필 이미지를 랜덤 선택
if "selected_image" not in st.session_state:
    st.session_state.selected_image = random.choice(image_urls)
bot_profile_url = st.session_state.selected_image

# 초기 채팅 히스토리 세팅 (예시)
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

if "copied_chat_history" not in st.session_state:
    st.session_state.copied_chat_history = ""

# CompletionExecutor 클래스(생략: 기존 코드 그대로)
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
                    next_line = lines[i + 1]
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

# CompletionExecutor 인스턴스 초기화 (기존 키 사용)
completion_executor = CompletionExecutor(
    host='https://clovastudio.stream.ntruss.com',
    api_key='NTA0MjU2MWZlZTcxNDJiY6Yo7+BLuaAQ2B5+PgEazGquXEqiIf8NRhOG34cVQNdq',
    api_key_primary_val='DilhGClorcZK5OTo1QgdfoDQnBNOkNaNksvlAVFE',
    request_id='d1950869-54c9-4bb8-988d-6967d113e03f'
)

# --- CSS 정의 시작 ---
st.markdown(f"""
    <style>
    /* 페이지 전체 배경색 */
    body, .main, .block-container {{
        background-color: #BACEE0 !important;
    }}

    /* 제목 스타일 */
    .title {{
        font-size: 28px !important;
        font-weight: bold;
        text-align: center;
        padding-top: 10px;
    }}

    /* 대화 출력 영역(chat-box) */
    .chat-box {{
        position: absolute;
        top: 60px;             /* 상단 제목 영역 밑에서 시작 */
        left: 20px;
        right: 20px;
        bottom: 80px;          /* 입력창 위치 위에서 끝나도록 여유 공간 */
        background-color: #BACEE0;
        overflow-y: auto;      /* 세로 스크롤 */
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }}

    /* 사용자 메시지(노란색) */
    .message-user {{
        background-color: #FFEB33 !important;
        color: black;
        text-align: right;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        margin-left: auto;
        max-width: 60%;
        box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
    }}

    /* 챗봇 메시지(흰색) */
    .message-assistant {{
        background-color: #FFFFFF !important;
        text-align: left;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        margin-right: auto;
        max-width: 60%;
        box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
    }}

    /* 프로필 이미지 스타일 */
    .profile-pic {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 10px;
    }}

    /* 입력창 영역(input-container)은 화면 하단에 고정 */
    .input-container {{
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #BACEE0;
        padding: 10px 20px;
        box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);
    }}

    /* 입력 필드 높이 조정 */
    .stTextInput > div > div > input {{
        height: 38px;
        width: 100%;
    }}

    /* 전송/복사 버튼 크기 조정 */
    .stButton button {{
        height: 38px !important;
        width: 70px !important;
        padding: 0px 10px;
        margin-right: 0px !important;
    }}
    </style>
""", unsafe_allow_html=True)
# --- CSS 정의 끝 ---

# 제목 표시
st.markdown('<h1 class="title">지렁이 챗봇</h1>', unsafe_allow_html=True)

# → chat-box 영역 시작 (HTML)
st.markdown('<div class="chat-box">', unsafe_allow_html=True)

# 실제 대화 내용 표시 (역할: user/assistant)
for message in st.session_state.chat_history[3:]:
    role = "User" if message["role"] == "user" else "Chatbot"
    message_class = 'message-user' if role == "User" else 'message-assistant'
    profile_html = ""
    if role == "Chatbot":
        profile_html = f'<img src="{bot_profile_url}" class="profile-pic" alt="프로필 이미지">'
        # 챗봇 메시지: 프로필 이미지와 함께
        st.markdown(f'''
            <div style="display:flex; align-items:flex-start;">
                {profile_html}
                <div class="{message_class}">
                    {message["content"]}
                </div>
            </div>
        ''', unsafe_allow_html=True)
    else:
        # 사용자 메시지: 오른쪽 정렬, 프로필 없음
        st.markdown(f'''
            <div class="message-container">
                <div class="{message_class}">
                    {message["content"]}
                </div>
            </div>
        ''', unsafe_allow_html=True)

# chat-box 영역 닫기
st.markdown('</div>', unsafe_allow_html=True)

# 입력창 영역(input-container): 화면 하단에 고정
st.markdown('<div class="input-container">', unsafe_allow_html=True)
with st.form(key="input_form", clear_on_submit=True):
    cols = st.columns([7.5, 1, 1])
    with cols[0]:
        user_message = st.text_input("메시지를 입력하세요:", key="input_message", placeholder="")
    with cols[1]:
        submit_button = st.form_submit_button(label="전송", on_click=lambda: send_message_callback())
    with cols[2]:
        def copy_chat_history():
            filtered = st.session_state.chat_history[3:]
            text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in filtered])
            st.session_state.copied_chat_history = text
        copy_button = st.form_submit_button(label="복사", on_click=lambda: copy_chat_history())
st.markdown('</div>', unsafe_allow_html=True)

# 복사된 대화 내역 표시 (필요 시)
if st.session_state.copied_chat_history:
    st.markdown("<h3>대화 내용 정리</h3>", unsafe_allow_html=True)
    st.text_area("", value=st.session_state.copied_chat_history, height=200, key="copied_chat_history_text_area")
    chat_history_escaped = st.session_state.copied_chat_history.replace("\n", "\\n").replace('"', '\\"')
    st.components.v1.html(f"""
        <textarea id="copied_chat_history_text_area" style="display:none;">{chat_history_escaped}</textarea>
        <button onclick="copyToClipboard()" class="copy-button">클립보드로 복사</button>
        <script>
        function copyToClipboard() {{
            var text = document.getElementById('copied_chat_history_text_area').value.replace(/\\\\n/g, '\\n');
            navigator.clipboard.writeText(text).then(function() {{
                alert('클립보드로 복사되었습니다!');
            }}, function(err) {{
                console.error('복사 실패: ', err);
            }});
        }}
        </script>
    """, height=100)

# --- send_message_callback 함수 정의 (마무리) ---
def send_message_callback():
    if st.session_state.input_message:
        um = st.session_state.input_message
        st.session_state.chat_history.append({"role": "user", "content": um})
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
        st.session_state.input_message = ""
