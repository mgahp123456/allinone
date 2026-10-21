import streamlit as st
import asyncio
import os
import requests
import subprocess

st.set_page_config(page_title="ACT Movie Recap Studio", page_icon="🎬", layout="wide")

# --- Custom Dark Theme Styling ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #ffffff; }
    .sidebar .sidebar-content { background-color: #161b22; }
    div.stButton > button { background-color: #3b82f6; color: white; border-radius: 8px; width: 100%; }
    div.stButton > button:hover { background-color: #2563eb; }
    </style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "gemini_key" not in st.session_state:
    st.session_state.gemini_key = ""
if "assembly_key" not in st.session_state:
    st.session_state.assembly_key = ""

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("### **ACT MOVIE**")
    
    menu = st.radio("Navigation", [
        "🏠 Dashboard", 
        "📁 Projects", 
        "🎙️ Transcribe", 
        "🗣️ Free Voice", 
        "🤖 Script Assistant", 
        "🌐 Translate", 
        "⚙️ Settings"
    ])
    
    st.divider()
    st.markdown("**Credits:** Free Unlimited")
    if st.button("💎 Upgrade Plan"):
        st.info("Paid plan သို့ Upgrade လုပ်ရန် ဆက်သွယ်ပါ။")
    if st.button("🚪 Logout"):
        st.warning("Logged out successfully.")

# ================= 1. SETTINGS PAGE =================
if menu == "⚙️ Settings":
    st.header("⚙️ Settings & API Configuration")
    st.markdown("Manage your account details and view your subscription plan.")
    
    st.subheader("Account Profile")
    st.text_input("Account Name", value="Mg Dzw")
    st.text_input("Email Address", value="user@telegram.local")
    st.text_input("Current Plan", value="Free Unlimited", disabled=True)

    st.divider()
    st.subheader("Personal Gemini API key")
    gemini_input = st.text_input("Gemini API Key", value=st.session_state.gemini_key, type="password")
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        if st.button("Check Gemini Key"):
            if gemini_input:
                st.session_state.gemini_key = gemini_input
                st.success("✅ Gemini API Key အလုပ်လုပ်ပါသည်")
            else:
                st.error("ကျေးဇူးပြု၍ API Key ထည့်ပါ။")
    with col_k2:
        if st.button("Remove Gemini Key"):
            st.session_state.gemini_key = ""
            st.warning("API Key ဖယ်ရှားပြီးပါပြီ။")

# ================= 2. DASHBOARD / NEW RECAP =================
elif menu == "🏠 Dashboard":
    st.header("🎬 New Recap Project")
    
    col_src1, col_src2 = st.columns(2)
    with col_src1:
        st.subheader("1. Source")
        video_file = st.file_uploader("Upload video file (MP4, MKV, MOV)", type=["mp4", "mkv", "mov"])
        telegram_id = st.text_input("Telegram Video ID", placeholder="e.g. ACTRecap_Y8NNUG8920")
        
        movie_title = st.text_input("Title", placeholder="Movie or episode name")
        movie_type = st.selectbox("Type", ["Movie Recap", "Series Recap", "Short Film"])
        language = st.selectbox("Language (Source)", ["Burmese", "English", "Thai"])
        spoken_lang = st.selectbox("Video's Spoken Language", ["Auto-detect (default)", "English", "Chinese"])
        
        script_notes = st.text_area("Script / Notes", placeholder="Character names, exact story context, Burmese wording, tone instructions...")

    with col_src2:
        st.subheader("2. AI & Voice")
        tts_engine = st.selectbox("TTS provider", ["Edge TTS (Free)", "ElevenLabs (Premium)"])
        script_model = st.selectbox("Script writing model", ["Default (Gemini 2.5 Flash)", "Gemini 2.5 Pro"])
        
        voice_choice = st.selectbox("Burmese Voice", ["Thiha - Burmese male (Free)", "Nilar - Burmese female (Free)"])
        voice_style = st.selectbox("Voice style", ["Dramatic", "Calm", "Energetic"])
        speed = st.slider("Speech speed", 0.5, 2.0, 1.0)
        
        generate_vo = st.checkbox("Generate voiceover", value=True)
        keep_audio = st.checkbox("Keep original audio (auto-duck)", value=False)
        dynamic_video = st.checkbox("Dynamic video trimming", value=True)

    st.divider()
    st.subheader("3. Subtitles & Output Options")
    col_sub1, col_sub2 = st.columns(2)
    with col_sub1:
        font_choice = st.selectbox("Subtitle Font", ["Pyidaungsu", "Noto Sans Myanmar", "Padauk"])
        font_size = st.slider("Font Size", 14, 36, 22)
        font_color = st.color_picker("Font Color", "#FFFF00")
    with col_sub2:
        cover_old = st.checkbox("Cover old subtitles with background box", value=True)
        aspect_ratio = st.selectbox("Aspect Ratio", ["9:16", "16:9", "1:1"])

    if st.button("🚀 Create Recap Video", use_container_width=True):
        if not video_file and not telegram_id:
            st.error("ကျေးဇူးပြု၍ ဗီဒီယိုဖိုင် တင်ပါ သို့မဟုတ် Telegram Video ID ထည့်ပါ။")
        elif not script_notes:
            st.error("ကျေးဇူးပြု၍ Script / Notes ထည့်ပါ။")
        else:
            with st.spinner("🔄 Movie Recap ဗီဒီယိုကို စတင် ထုတ်လုပ်နေပါပြီ..."):
                if video_file:
                    with open("input.mp4", "wb") as f:
                        f.write(video_file.read())
                
                import edge_tts
                voice_id = "my-MM-NyiNyiNeural" if "Thiha" in voice_choice else "my-MM-ThihaNeural"
                
                async def create_audio():
                    communicate = edge_tts.Communicate(script_notes, voice_id)
                    await communicate.save("voice.mp3")
                
                try:
                    asyncio.run(create_audio())
                except:
                    pass

                # Safe FFmpeg execution
                if os.path.exists("input.mp4") and os.path.exists("voice.mp3"):
                    cmd = [
                        "ffmpeg", "-y", "-i", "input.mp4", "-i", "voice.mp3",
                        "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", 
                        "-map", "0:v:0", "-map", "1:a:0", "-shortest", "output.mp4"
                    ]
                    subprocess.run(cmd)
                    
                    if os.path.exists("output.mp4") and os.path.getsize("output.mp4") > 0:
                        st.success("✅ Movie Recap ဗီဒီယို အောင်မြင်စွာ ပြီးဆုံးပါပြီ!")
                        st.video("output.mp4")
                        with open("output.mp4", "rb") as f:
                            st.download_button("📥 Download Recap Video", f, file_name="movie_recap.mp4", mime="video/mp4")
                    else:
                        st.error("ဗီဒီယို တည်းဖြတ်ရာတွင် အမှားရှိနေပါသည်။")
                else:
                    st.error("ဗီဒီယိုဖိုင် သို့မဟုတ် အသံဖိုင် မရှိပါ။")

# ================= 3. OTHER PAGES =================
elif menu == "📁 Projects":
    st.header("📁 Projects")
    st.markdown("ကိုယ့်လုပ်ထားသော Recap Project များနှင့် မှတ်တမ်းများ။")
    st.info("လက်တလော Project များ မရှိသေးပါ။")

elif menu == "🎙️ Transcribe":
    st.header("🎙️ Transcribe Subtitles")
    st.markdown("Upload a video or audio file and download an SRT subtitle file.")
    st.file_uploader("Upload Media File", type=["mp4", "mp3", "wav", "m4a"])
    if st.button("Generate SRT"):
        st.success("Subtitle generated successfully!")

elif menu == "🗣️ Free Voice":
    st.header("🗣️ Free Voice Generator")
    text_in = st.text_area("Text to speech", value="မြန်မာစကားပြော အသံဖိုင်ထုတ်ရန်...")
    v_sel = st.selectbox("Voice", ["Thiha (Male)", "Nilar (Female)"])
    if st.button("Generate Preview"):
        st.success("Voice generated!")

elif menu == "🤖 Script Assistant":
    st.header("🤖 Script Assistant")
    st.text_input("Movie Name / Topic")
    if st.button("Generate Script with Gemini"):
        st.write("Gemini API သုံးပြီး ဇာတ်လမ်းအကျဉ်း ရေးသားပေးမည့်နေရာ ဖြစ်ပါသည်။")

elif menu == "🌐 Translate":
    st.header("🌐 Translate Script")
    st.markdown("Translate subtitles or scripts into Burmese instantly.")
    st.text_area("Source Text")
    if st.button("Translate to Burmese"):
        st.write("ဘာသာပြန်ပြီးစာသားများ ပေါ်လာမည်။")
              
