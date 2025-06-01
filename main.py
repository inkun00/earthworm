import streamlit as st
import requests
import json
import random

# ─────────────────────────────────────────────────────────────────────────────
# 0) 이미지 리스트와 CompletionExecutor, 세션 상태 초기화 (원래 코드와 동일)
# ─────────────────────────────────────────────────────────────────────────────
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

# CompletionExecutor 클래스 정의 (원래 코드와 동일)
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

completion_executor = CompletionExecutor(
    host='https://clovastudio.stream.ntruss.com',
    api_key='YOUR_API_KEY_HERE',
    api_key_primary_val='YOUR_PRIMARY_KEY_HERE',
    request_id='d1950869-54c9-4bb8-988d-6967d113e03f'
)

# ─────────────────────────────────────────────────────────────────────────────
# 1) send_message 함수 정의를 폼 생성부보다 위로 옮깁니다.
# ─────────────────────────────────────────────────────────────────────────────
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
        st.session_state.input_message = ""

# ─────────────────────────────────────────────────────────────────────────────
# 2) Streamlit 앱 제목 및 CSS 삽입
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<h1 class='title'>지렁이 챗봇</h1>", unsafe_allow_html=True)
st.markdown("""
<style>
  /* ─────────────────────────────────────────────────────────────────────────────
     ─  전체 배경색 및 기본 여백 제거
     ───────────────────────────────────────────────────────────────────────────── */
  body, .main, .block-container {
      background-color: #BACEE0 !important;
      padding: 0;
      margin: 0;
  }
  .title {
      font-size: 28px !important;
      font-weight: bold;
      text-align: center;
      padding: 10px 0;
      margin: 0;
  }

  /* ─────────────────────────────────────────────────────────────────────────────
     ─  채팅 출력 영역(chat-box): 절대 위치 고정, 상단/하단 여백 조정, 스크롤 자동
     ───────────────────────────────────────────────────────────────────────────── */
  .chat-box {
      position: absolute;
      top: 60px;       /* 제목 아래부터 시작 */
      left: 0;
      right: 0;
      bottom: 80px;    /* 입력창 위까지 영역 확보 */
      padding: 20px;
      overflow-y: auto;         /* 길어지면 스크롤바 생김 */
      background-color: #BACEE0;
  }
  .message-container {
      display: flex;
      margin-bottom: 10px;
      align-items: flex-start;
  }
  .message-user {
      background-color: #FFEB33;
      color: black;
      text-align: right;
      padding: 10px;
      border-radius: 10px;
      margin-left: auto;
      max-width: 60%;
      box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
      word-wrap: break-word;
  }
  .message-assistant {
      background-color: #FFFFFF;
      text-align: left;
      padding: 10px;
      border-radius: 10px;
      margin-right: auto;
      max-width: 60%;
      box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
      word-wrap: break-word;
  }
  .profile-pic {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      margin-right: 10px;
  }

  /* ─────────────────────────────────────────────────────────────────────────────
     ─  채팅 입력 영역(input-container): 화면 하단에 고정
     ───────────────────────────────────────────────────────────────────────────── */
  .input-container {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      background-color: #BACEE0;
      padding: 10px 20px;
      box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);
      display: flex;
      align-items: center;
      height: 80px;    /* 바닥부터 80px 높이 차지 */
  }
  .input-container .stTextInput > div > div > input {
      height: 38px;
      width: 100%;
  }
  .input-container .stButton button {
      height: 38px !important;
      width: 70px !important;
      padding: 0px 10px;
      margin-left: 10px;
  }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 3) 채팅 출력 영역 (chat-box) 시작
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
for message in st.session_state.chat_history[3:]:
    is_user = (message["role"] == "user")
    css_class = "message-user" if is_user else "message-assistant"

    if is_user:
        st.markdown(f"""
            <div class="message-container">
                <div class="{css_class}">{message["content"]}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="message-container">
                <img src="{selected_image}" class="profile-pic" alt="프로필 이미지">
                <div class="{css_class}">{message["content"]}</div>
            </div>
        """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 4) 채팅 입력 영역 (input-container) – 화면 하단에 고정
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div class='input-container'>", unsafe_allow_html=True)
with st.form(key="input_form", clear_on_submit=True):
    cols = st.columns([7.5, 1, 1])
    with cols[0]:
        user_message = st.text_input("", key="input_message", placeholder="메시지를 입력하세요:")
    with cols[1]:
        # on_click에 호출할 함수가 이미 정의된 상태여야 하므로, 
        # lambda 없이 바로 함수 이름만 넘겨도 됩니다.
        submit_button = st.form_submit_button(label="전송", on_click=send_message)
    with cols[2]:
        def copy_chat_history():
            filtered = st.session_state.chat_history[3:]
            text = "\n".join([f"{x['role']}: {x['content']}" for x in filtered])
            st.session_state.copied_chat_history = text

        copy_button = st.form_submit_button(label="복사", on_click=copy_chat_history)
st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 5) (선택) 복사된 대화 내용을 표시하는 영역
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.copied_chat_history:
    st.markdown("<h3>대화 내용 정리</h3>", unsafe_allow_html=True)
    st.text_area("", value=st.session_state.copied_chat_history, height=200, key="copied_chat_history_text_area")
    chat_history = st.session_state.copied_chat_history.replace("\n", "\\n").replace('"', '\\"')
    st.components.v1.html(f"""
        <textarea id="copied_chat_history_text_area" style="display:none;">{chat_history}</textarea>
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
