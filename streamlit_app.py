import streamlit as st
from datetime import datetime

# ตั้งค่า session_state สำหรับเก็บประวัติการสนทนา
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []  # เก็บในรูปแบบ [{"title": "ข้อความแรก", "history": [{"role": "user/assistant", "content": "ข้อความ", "timestamp": datetime}]}]

if "current_session" not in st.session_state:
    st.session_state.current_session = None  # เก็บ index ของ session ที่กำลังแสดงอยู่

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

# Sidebar สำหรับจัดการเซสชัน
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

# ส่วนหลักของแอปพลิเคชัน
st.title("Chat Application")

# รับข้อความจากผู้ใช้
user_input = st.chat_input("Type your message here...")  # กล่องข้อความสำหรับผู้ใช้

if user_input:
    # หากยังไม่มีเซสชัน เริ่มเซสชันใหม่
    if st.session_state.current_session is None:
        st.session_state.chat_sessions.append({"title": "", "history": []})
        st.session_state.current_session = len(st.session_state.chat_sessions) - 1

    # เพิ่มข้อความใหม่ในเซสชันปัจจุบัน
    add_to_current_session("user", user_input)
    
    # ตอบกลับข้อความ (ตัวอย่างคำตอบ)
    response = f"I received your message: {user_input}"
    add_to_current_session("assistant", response)

# แสดงประวัติการสนทนาในหน้าหลัก
if st.session_state.current_session is not None:
    session = st.session_state.chat_sessions[st.session_state.current_session]
    st.subheader(f"Session: {session.get('title', 'New Chat')}")
    for chat in session["history"]:
        role = "You" if chat["role"] == "user" else "Bot"
        st.write(f"**{role} :** {chat['content']}")
else:
    st.write("No chat selected. Start a new chat!")
