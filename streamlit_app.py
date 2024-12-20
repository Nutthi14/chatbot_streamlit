import streamlit as st
from datetime import datetime

# ตั้งค่า session_state สำหรับเก็บประวัติการสนทนา
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []

if "current_session" not in st.session_state:
    st.session_state.current_session = None

# ฟังก์ชันเริ่มต้นเซสชันใหม่
def start_new_session():
    st.session_state.current_session = None

# ฟังก์ชันเพิ่มข้อความในเซสชันปัจจุบัน
def add_to_current_session(role, content):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if st.session_state.current_session is not None:
        st.session_state.chat_sessions[st.session_state.current_session]["history"].append(
            {"role": role, "content": content, "timestamp": timestamp}
        )
    
# Sidebar สำหรับการตั้งค่า
with st.sidebar.expander("⚙️ Settings", expanded=True):
    model_options = {
        "gpt-4o-mini": "GPT-4o Mini",
        "llama-3.1-405b": "Llama 3.1 405B",
        "llama-3.2-3b": "Llama 3.2 3B",
        "Gemini Pro 1.5": "Gemini Pro 1.5",
    }
    model = st.selectbox("Choose your AI Model:", options=list(model_options.keys()))
    temperature = st.slider("Set Temperature:", min_value=0.0, max_value=2.0, value=1.0)
    
    api_key = st.text_input("API Key", type="password")
    st.session_state["api_key"] = api_key

# ส่วนสำหรับอัปโหลดไฟล์ใน Sidebar
st.sidebar.markdown("### 📂 File Upload")
uploaded_files = st.sidebar.file_uploader("Choose files", accept_multiple_files=True)

# แสดงชื่อไฟล์ที่อัปโหลด
if uploaded_files:
    st.sidebar.markdown("#### Uploaded Files:")
    for file in uploaded_files:
        st.sidebar.write(f"- {file.name}")


# Sidebar สำหรับจัดการประวัติการสนทนา
st.sidebar.title("Chat History")

# ปุ่มเริ่มต้นเซสชันใหม่
if st.sidebar.button("Start New Chat"):
    if st.session_state.current_session is not None:
        # บันทึกเซสชันเก่าด้วย title จากข้อความแรก
        if len(st.session_state.chat_sessions[st.session_state.current_session]["history"]) > 0:
            first_message = st.session_state.chat_sessions[st.session_state.current_session]["history"][0]["content"]
            st.session_state.chat_sessions[st.session_state.current_session]["title"] = first_message
    start_new_session()

# แสดงรายการเซสชันใน Sidebar โดยแชทใหม่อยู่ข้างบน
if st.session_state.chat_sessions:
    for idx, session in reversed(list(enumerate(st.session_state.chat_sessions))):
        title = session.get("title", f"Session {idx + 1}")
        if st.sidebar.button(title, key=f"session_{idx}"):
            st.session_state.current_session = idx
  

st.title("Chat Application")

# Layout สำหรับการสนทนาและ Log
col1, col2 = st.columns([175, 100])  # เพิ่มสัดส่วนของคอลัมน์ด้านขวา


# คอลัมน์หลักสำหรับการสนทนา
with col1:
    chat_container = st.container()  # พื้นที่แสดงข้อความ
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # หากไม่มีเซสชัน เริ่มเซสชันใหม่
        if st.session_state.current_session is None:
            st.session_state.chat_sessions.append({"title": "", "history": []})
            st.session_state.current_session = len(st.session_state.chat_sessions) - 1

        # เพิ่มข้อความใหม่ในเซสชันปัจจุบัน
        add_to_current_session("user", user_input)

        # ตัวอย่างการตอบกลับ
        response = f"I received your message: {user_input}"
        add_to_current_session("assistant", response)

    # แสดงข้อความใน Chat
    with chat_container:
        if st.session_state.current_session is not None:
            session = st.session_state.chat_sessions[st.session_state.current_session]
            st.subheader(f"Session: {session.get('title', 'New Chat')}")
            for chat in (session["history"]):  # แสดงข้อความล่าสุดด้านบน
                role = "You" if chat["role"] == "user" else "Bot"
                st.markdown(f"**{role}:** {chat['content']}")

# คอลัมน์สำหรับ Log
with col2:
    with st.expander("📝 Chat Log", expanded=False):
        if st.session_state.chat_sessions:
            for idx, session in reversed(list(enumerate(st.session_state.chat_sessions))):
                title = session.get("title", f"Session {idx + 1}")
                st.markdown(f"**{title}**")
                for chat in session["history"]:
                    st.write(f"{chat['timestamp']} | {chat['role'].capitalize()}: {chat['content']}")
        else:
            st.write("No chat logs available.")

# ปุ่มอัปโหลดไฟล์ทางซ้ายล่างสุด
st.markdown(
    """
    <style>
        #file-upload {
            position: fixed;
            bottom: 10px;
            left: 10px;
            z-index: 1000;
            background-color: #000000;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 2px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
        }
    </style>
    <div id="file-upload">
        <input type="file">
    </div>
    """,
    unsafe_allow_html=True,
)



