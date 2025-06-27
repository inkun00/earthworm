import streamlit as st
import requests
import json
import random

# Github RAW 이미지 사용
image_urls = [
    "https://raw.githubusercontent.com/inkun00/earthworm/main/image/image1.png",
    "https://raw.githubusercontent.com/inkun00/earthworm/main/image/image2.png",
    "https://raw.githubusercontent.com/inkun00/earthworm/main/image/image3.png",
    "https://raw.githubusercontent.com/inkun00/earthworm/main/image/image4.png",
    "https://raw.githubusercontent.com/inkun00/earthworm/main/image/image5.png",
    "https://raw.githubusercontent.com/inkun00/earthworm/main/image/image6.png",
    "https://raw.githubusercontent.com/inkun00/earthworm/main/image/image7.png",
    "https://raw.githubusercontent.com/inkun00/earthworm/main/image/image8.png",
    "https://raw.githubusercontent.com/inkun00/earthworm/main/image/image9.png"
]

# 처음 실행 시, 이미지 선택을 한 번만 실행하도록 설정
if "selected_image" not in st.session_state:
    st.session_state.selected_image = random.choice(image_urls)
selected_image = st.session_state.selected_image

# 대화 기록 초기화
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

        # 스트리밍 모드로 요청
        r = requests.post(
            self._host + '/testapp/v1/chat-completions/HCX-003',
            headers=headers,
            json=completion_request,
            stream=True
        )

        full_response = ""
        # 각 라인을 읽어서 data: 로 시작하는 JSON 덩어리를 누적
        for raw_line in r.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            line = raw_line.strip()
            if line.startswith("data:"):
                data_str = line[len("data:"):].strip()
                # 종료 시그널 처리
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    # 델타 형태로 들어오는 content를 누적
                    delta = chunk.get("message", {}).get("content", "")
                    full_response += delta
                except json.JSONDecodeError:
                    # JSON이 아니면 무시
                    continue

        return full_response


# 클로바 스튜디오 실행기 초기화
completion_executor = CompletionExecutor(
    host='https://clovastudio.stream.ntruss.com',
    api_key='NTA0MjU2MWZlZTcxNDJiY6Yo7+BLuaAQ2B5+PgEazGquXEqiIf8NRhOG34cVQNdq',
    api_key_primary_val='DilhGClorcZK5OTo1QgdfoDQnBNOkNaNksvlAVFE',
    request_id='d1950869-54c9-4bb8-988d-6967d113e03f'
)

# 페이지 타이틀
st.markdown('<h1 class="title">지렁이와 대화나누기</h1>', unsafe_allow_html=True)
bot_profile_url = selected_image

# 스타일 정의 (원본 그대로)
st.markdown(f"""
    <style>
    body, .main, .block-container {{ background-color: #BACEE0 !important; }}
    .title {{ font-size: 28px !important; font-weight: bold; text-align: center; padding-top: 10px; }}
    .message-container {{ display: flex; margin-bottom: 10px; align-items: center; }}
    .message-user {{ background-color: #FFEB33 !important; color: black; text-align: right;
        padding: 10px; border-radius: 10px; margin-left: auto; max-width: 60%;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1); }}
    .message-assistant {{ background-color: #FFFFFF !important; text-align: left;
        padding: 10px; border-radius: 10px; margin-right: auto; max-width: 60%;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1); }}
    .profile-pic {{ width: 40px; height: 40px; border-radius: 50%; margin-right: 10px; }}
    .chat-box {{ background-color: #BACEE0 !important; border: none; padding: 20px;
        border-radius: 10px; max-height: 400px; overflow-y: scroll; margin: 0 auto; width: 80%; }}
    .stTextInput > div > div > input {{ height: 38px; width: 100%; }}
    .stButton button {{ height: 38px !important; width: 70px !important;
        padding: 0px 10px; margin-right: 0px !important; }}
    .input-container {{ position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #BACEE0; padding: 10px; box-shadow: 0 -2px 5px rgba(0,0,0,0.1); }}
    </style>
""", unsafe_allow_html=True)

# 채팅 내역 표시
st.markdown('<div class="chat-box">', unsafe_allow_html=True)
for message in st.session_state.chat_history[3:]:
    if message["role"] == "user":
        st.markdown(f'''
            <div class="message-container">
                <div class="message-user">{message["content"]}</div>
            </div>''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
            <div class="message-container">
                <img src="{bot_profile_url}" class="profile-pic" alt="프로필">
                <div class="message-assistant">{message["content"]}</div>
            </div>''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 입력창 & 버튼
st.markdown('<div class="input-container">', unsafe_allow_html=True)
with st.form(key="input_form", clear_on_submit=True):
    cols = st.columns([7.5, 1, 1])
    with cols[0]:
        st.text_input("메시지를 입력하세요:", key="input_message", placeholder="")
    with cols[1]:
        def send_message():
            user_msg = st.session_state.input_message.strip()
            if user_msg:
                # 1) 유저 메시지 추가
                st.session_state.chat_history.append(
                    {"role": "user", "content": user_msg}
                )
                # 2) API 요청
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
                # 3) 응답 전체 수신
                assistant_text = completion_executor.execute(completion_request)
                # 4) 어시스턴트 메시지 추가
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": assistant_text}
                )
                # 5) 입력 초기화 및 다시 그리기
                st.session_state.input_message = ""
                st.rerun()

        st.form_submit_button(label="전송", on_click=send_message)
    with cols[2]:
        def copy_chat_history():
            filtered = st.session_state.chat_history[3:]
            text = "\n".join(f'{msg["role"]}: {msg["content"]}' for msg in filtered)
            st.session_state.copied_chat_history = text
        st.form_submit_button(label="복사", on_click=copy_chat_history)
st.markdown('</div>', unsafe_allow_html=True)

# 복사된 대화 내용 표시
if st.session_state.copied_chat_history:
    st.markdown("<h3>대화 내용 정리</h3>", unsafe_allow_html=True)
    st.text_area("", value=st.session_state.copied_chat_history, height=200)
