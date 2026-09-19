import os
import tempfile
import streamlit as st
from yt_dlp import YoutubeDL

st.set_page_config(
    page_title="Multi-Platform Downloader Pro",
    page_icon="📥",
    layout="centered"
)

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 50px;
        font-weight: bold;
        font-size: 16px;
        background-color: #FF4B4B;
        color: white;
    }
    .stButton>button:hover {
        background-color: #ff2b2b;
    }
    h1 {
        text-align: center;
        font-size: 22px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📥 أداة تحميل الفيديوهات والريلز السحابية")
st.markdown("<p style='text-align: center; color: gray;'>يوتيوب • تيك توك • انستاجرام (يعمل من أي هاتفك في أي وقت)</p>", unsafe_allow_html=True)

platform = st.selectbox(
    "اختر المنصة:",
    ["YouTube", "TikTok Reels", "Instagram Reels"]
)

url = st.text_input("ألصق الرابط هنا:", placeholder="https://...")

if platform == "YouTube":
    quality = st.selectbox(
        "اختر الجودة أو الصيغة:",
        [
            "أفضل جودة أصلية (مع أعلى فريمات)",
            "1080p MP4",
            "720p MP4",
            "صوت فقط (MP3)"
        ]
    )
else:
    quality = st.selectbox(
        "اختر الصيغة:",
        [
            "أفضل جودة أصلية (بدون علامة مائية)",
            "صوت فقط (MP3)"
        ]
    )

if st.button("🚀 معالجة وتجهيز التحميل"):
    if not url.strip():
        st.warning("⚠️ الرجاء إدخال الرابط أولاً!")
    else:
        with st.spinner("⏳ جاري التحميل والمعالجة من السحابة..."):
            try:
                # Create a temporary directory for downloading
                temp_dir = tempfile.mkdtemp()
                
                ydl_opts = {
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    'noplaylist': True,
                }

                if platform == "YouTube":
                    if "1080p" in quality:
                        ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best'
                    elif "720p" in quality:
                        ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'
                    elif "صوت فقط" in quality:
                        ydl_opts['format'] = 'bestaudio/best'
                        ydl_opts['postprocessors'] = [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }]
                    else:
                        ydl_opts['format'] = 'bestvideo+bestaudio/best'
                else:
                    if "صوت فقط" in quality:
                        ydl_opts['format'] = 'bestaudio/best'
                        ydl_opts['postprocessors'] = [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }]
                    else:
                        ydl_opts['format'] = 'best/bestvideo+bestaudio'

                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    
                    # If converted to mp3
                    if "صوت فقط" in quality or "MP3" in quality:
                        base, _ = os.path.splitext(filename)
                        filename = base + ".mp3"

                if os.path.exists(filename):
                    file_size_mb = os.path.getsize(filename) / (1024 * 1024)
                    st.success(f"✅ تم تجهيز الملف بنجاح! (الحجم: {file_size_mb:.1f} MB)")
                    
                    with open(filename, "rb") as f:
                        file_bytes = f.read()
                    
                    file_name_download = os.path.basename(filename)
                    st.download_button(
                        label="📥 اضغط هنا لتنزيل الملف على هاتفك",
                        data=file_bytes,
                        file_name=file_name_download,
                        mime="audio/mpeg" if filename.endswith(".mp3") else "video/mp4"
                    )
                else:
                    st.error("❌ لم يتم العثور على الملف بعد التحميل.")

            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء التحميل: {str(e)}")

st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 12px; color: gray;'>يعمل على Streamlit Community Cloud</p>", unsafe_allow_html=True)
