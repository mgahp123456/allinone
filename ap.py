import streamlit as st
import asyncio
import os
import subprocess

st.set_page_config(page_title="ACT Movie Recap Studio", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #ffffff; }
    div.stButton > button { background-color: #3b82f6; color: white; border-radius: 8px; width: 100%; }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 ACT Movie Recap Studio")

with st.sidebar:
    st.header("⚙️ Settings")
    voice_choice = st.selectbox("Burmese Voice", ["Thiha (Male)", "Nilar (Female)"])
    voice_id = "my-MM-NyiNyiNeural" if "Thiha" in voice_choice else "my-MM-ThihaNeural"

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Source Video & Script")
    video_file = st.file_uploader("Upload MP4 Video", type=["mp4", "mkv", "mov"])
    script_notes = st.text_area("Script / Notes (မြန်မာဇာတ်လမ်းအကျဉ်း)", placeholder="ဒီနေရာမှာ ဇာတ်လမ်း ရေးပါ...")

with col2:
    st.subheader("2. Output Options")
    font_size = st.slider("Font Size", 14, 36, 22)
    font_color = st.color_picker("Font Color", "#FFFF00")

async def run_edge_tts(text, voice, out_file):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(out_file)

if st.button("🚀 Create Recap Video", use_container_width=True):
    if not video_file or not script_notes:
        st.error("ကျေးဇူးပြု၍ ဗီဒီယိုဖိုင်နှင့် ဇာတ်လမ်းစာသား ပြည့်စုံစွာ ထည့်ပါ။")
    else:
        with st.spinner("အသံဖိုင်နှင့် ဗီဒီယိုကို ဖန်တီးနေပါသည်..."):
            with open("input.mp4", "wb") as f:
                f.write(video_file.read())

            try:
                asyncio.run(run_edge_tts(script_notes, voice_id, "voice.mp3"))
            except Exception as e:
                st.error(f"အသံဖိုင်ထုတ်ရာတွင် အမှားရှိသည်: {e}")

            # Ultra-safe FFmpeg command
            cmd = [
                "ffmpeg", "-y", "-i", "input.mp4", "-i", "voice.mp3",
                "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", "output.mp4"
            ]
            
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if os.path.exists("output.mp4") and os.path.getsize("output.mp4") > 0:
                st.success("✅ ဗီဒီယို ထုတ်လုပ်ခြင်း အောင်မြင်ပါပြီ!")
                st.video("output.mp4")
                with open("output.mp4", "rb") as f:
                    st.download_button("📥 Download Video", f, file_name="recap_output.mp4", mime="video/mp4")
            else:
                st.error("ဗီဒီယို တည်းဖြတ်မှု မအောင်မြင်ပါ။ ဖိုင်အမျိုးအစားကို ပြောင်းလဲစမ်းသပ်ပါ။")
              
