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

st.title("📥 أداة تحميل الفيديوهات وقوائم التشغيل والريلز")
st.markdown("<p style='text-align: center; color: gray;'>يوتيوب (مع اختيار فيديوهات القائمة) • تيك توك • انستاجرام</p>", unsafe_allow_html=True)

platform = st.selectbox(
    "اختر المنصة:",
    ["YouTube", "TikTok Reels", "Instagram Reels"]
)

url = st.text_input("ألصق الرابط هنا:", placeholder="https://...")

if "YouTube" in platform:
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
            "أفضل جودة أصلية للريلز",
            "صوت الريلز فقط (MP3)"
        ]
    )

# Initialize session state for playlist
if 'playlist_entries' not in st.session_state:
    st.session_state.playlist_entries = None
if 'playlist_title' not in st.session_state:
    st.session_state.playlist_title = ""

# Button to analyze URL (especially for playlists)
if st.button("🔍 فحص الرابط واكتشاف المحتوى"):
    if not url.strip():
        st.warning("⚠️ الرجاء إدخال الرابط أولاً!")
    else:
        with st.spinner("⏳ جاري فحص الرابط واستخراج تفاصيل الفيديوهات..."):
            try:
                ydl_opts = {'extract_flat': True, 'quiet': True}
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    if info and 'entries' in info:
                        st.session_state.playlist_entries = list(info['entries'])
                        st.session_state.playlist_title = info.get('title', 'قائمة تشغيل يوتيوب')
                        st.success(f"✅ تم اكتشاف قائمة تشغيل: '{st.session_state.playlist_title}' (عدد الفيديوهات: {len(st.session_state.playlist_entries)})")
                    else:
                        st.session_state.playlist_entries = None
                        st.info("ℹ️ هذا فيديو فردي وليس قائمة تشغيل. يمكنك الضغط على زر التحميل أدناه مباشرة.")
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء الفحص: {str(e)}")

# If it's a playlist, show checkboxes for each video
selected_videos = []
if st.session_state.playlist_entries:
    st.markdown(f"### 📋 اختر الفيديوهات المطلوبة من قائمة: **{st.session_state.playlist_title}**")
    
    # Select all / Deselect all buttons
    col1, col2 = st.columns(2)
    select_all = col1.checkbox("تحديد الكل", value=True)
    
    for idx, entry in enumerate(st.session_state.playlist_entries):
        v_title = entry.get(title := 'title', f"فيديو #{idx+1}")
        v_url = entry.get('url') or entry.get('webpage_url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
        
        is_checked = st.checkbox(f"{idx+1}. {v_title}", value=select_all, key=f"vid_{idx}")
        if is_checked:
            selected_videos.append(v_url)

# Download button
download_label = "🚀 بدء تحميل الفيديوهات المحددة من القائمة" if st.session_state.playlist_entries else "🚀 بدء التحميل"

if st.button(download_label):
    if not url.strip():
        st.warning("⚠️ الرجاء إدخال الرابط أولاً!")
    else:
        with st.spinner("⏳ جاري التحميل والمعالجة..."):
            try:
                temp_dir = tempfile.mkdtemp()
                
                ydl_opts = {
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                }

                if "YouTube" in platform:
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
                    if "صوت" in quality:
                        ydl_opts['format'] = 'bestaudio/best'
                        ydl_opts['postprocessors'] = [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }]
                    else:
                        ydl_opts['format'] = 'best/bestvideo+bestaudio'

                # If playlist entries were selected, download only selected URLs
                if st.session_state.playlist_entries and selected_videos:
                    with YoutubeDL(ydl_opts) as ydl:
                        ydl.download(selected_videos)
                    st.success(f"✅ تم بنجاح تحميل {len(selected_videos)} فيديو من القائمة!")
                else:
                    # Single video download
                    ydl_opts['noplaylist'] = True
                    with YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        filename = ydl.prepare_filename(info)
                        
                        if "صوت" in quality or "MP3" in quality:
                            base, _ = os.path.splitext(filename)
                            filename = base + ".mp3"

                    if os.path.exists(filename):
                        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
                        st.success(f"✅ تم تجهيز الفيديو بنجاح! (الحجم: {file_size_mb:.1f} MB)")
                        
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
