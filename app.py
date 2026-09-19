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
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif !important;
        background-color: #050505;
        color: #f1f1f1;
    }
    
    .main {
        padding: 1.5rem;
        background: radial-gradient(circle at 50% 10%, rgba(0, 255, 102, 0.08) 0%, rgba(5, 5, 5, 1) 70%);
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 50px;
        font-weight: 700;
        font-size: 16px;
        background-color: #00E676;
        color: #000000;
        border: none;
        box-shadow: 0 0 15px rgba(0, 230, 118, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #00C853;
        box-shadow: 0 0 25px rgba(0, 230, 118, 0.8);
        transform: translateY(-2px);
    }
    
    h1, h2, h3 {
        font-weight: 900 !important;
        color: #ffffff;
        text-shadow: 0 0 10px rgba(0, 255, 102, 0.2);
    }
    
    p, label, span {
        font-weight: 600 !important;
    }
    
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        border-radius: 10px;
        border: 2px solid #222222;
        background-color: #121212;
        color: #ffffff;
        font-weight: 600;
    }
    .stTextInput>div>div>input:focus {
        border-color: #00E676;
        box-shadow: 0 0 10px rgba(0, 230, 118, 0.3);
    }

    @media (max-width: 768px) {
        .main {
            padding: 0.8rem;
        }
        h1 {
            font-size: 20px !important;
        }
        .stButton>button {
            height: 46px;
            font-size: 15px;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📥 أداة التحميل الذكية بالذكاء الاصطناعي")
st.markdown("<p style='color: #00E676; font-weight: 700;'>تحديد ذكي • تجاوز الحظر • تحميل مباشر</p>", unsafe_allow_html=True)

# Initialize session state
if 'playlist_entries' not in st.session_state:
    st.session_state.playlist_entries = None
if 'playlist_title' not in st.session_state:
    st.session_state.playlist_title = ""
if 'url_input' not in st.session_state:
    st.session_state.url_input = ""
if 'video_details' not in st.session_state:
    st.session_state.video_details = None
if 'download_history' not in st.session_state:
    st.session_state.download_history = []
if 'detected_platform' not in st.session_state:
    st.session_state.detected_platform = "YouTube"

def reset_app():
    st.session_state.playlist_entries = None
    st.session_state.playlist_title = ""
    st.session_state.url_input = ""
    st.session_state.video_details = None
    st.rerun()

def on_selection_change():
    mode = st.session_state.sel_mode
    if st.session_state.playlist_entries:
        for idx, entry in enumerate(st.session_state.playlist_entries):
            key = f"vid_{idx}"
            if mode == "تحديد الكل":
                st.session_state[key] = True
            elif mode == "إلغاء الكل":
                st.session_state[key] = False
            elif mode == "أول 10":
                st.session_state[key] = (idx < 10)
            elif mode == "أول 20":
                st.session_state[key] = (idx < 20)

col_title, col_reset = st.columns([4, 1])
with col_reset:
    if st.button("🔄 إعادة ضبط"):
        reset_app()

# Smart Auto-Paste Button
st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)
st.components.v1.html("""
    <button onclick="navigator.clipboard.readText().then(text => {
        const input = parent.document.querySelector('input[aria-label*=\\'ألصق الرابط هنا\\']');
        if(input) {
            input.value = text;
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
    })" style="background-color: #00E676; color: #000; border: none; padding: 12px 20px; border-radius: 12px; cursor: pointer; font-weight: bold; width: 100%; font-size: 16px; box-shadow: 0 0 15px rgba(0,230,118,0.4);">⚡ لصق تلقائي وتحليل فوري من الحافظة</button>
""", height=60)

url = st.text_input("ألصق الرابط هنا:", value=st.session_state.url_input, placeholder="https://...", key="url_input")

if url:
    url_lower = url.lower()
    if "tiktok.com" in url_lower:
        st.session_state.detected_platform = "TikTok Reels"
    elif "instagram.com" in url_lower:
        st.session_state.detected_platform = "Instagram Reels"
    else:
        st.session_state.detected_platform = "YouTube"

platform = st.selectbox(
    "المنصة المكتشفة:",
    ["YouTube", "TikTok Reels", "Instagram Reels"],
    index=["YouTube", "TikTok Reels", "Instagram Reels"].index(st.session_state.detected_platform)
)

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

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
if st.button("🔍 فحص الرابط واكتشاف المحتوى"):
    if not url.strip():
        st.warning("⚠️ الرجاء إدخال الرابط أولاً!")
    else:
        with st.spinner("⚡ جاري فحص الرابط بسرعة فائقة..."):
            try:
                ydl_opts = {
                    'extract_flat': True,
                    'quiet': True,
                    'geo_bypass': True,
                    'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
                }
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    if info and 'entries' in info:
                        st.session_state.playlist_entries = list(info['entries'])
                        st.session_state.playlist_title = info.get('title', 'قائمة تشغيل يوتيوب')
                        st.session_state.video_details = None
                        # Initialize default checkboxes in session state
                        for idx, _ in enumerate(st.session_state.playlist_entries):
                            st.session_state[f"vid_{idx}"] = True
                        st.success(f"✅ تم اكتشاف قائمة تشغيل: '{st.session_state.playlist_title}' (عدد الفيديوهات: {len(st.session_state.playlist_entries)})")
                    else:
                        st.session_state.playlist_entries = None
                        st.session_state.video_details = {
                            'title': info.get('title', 'غير معروف'),
                            'uploader': info.get('uploader') or info.get('channel', 'غير معروف'),
                            'duration': int(info.get('duration', 0)),
                            'views': info.get('view_count', 0),
                            'thumbnail': info.get('thumbnail')
                        }
                        st.success("✅ تم فحص الفيديو بنجاح! يمكنك الضغط على زر التحميل أدناه.")
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء الفحص: {str(e)}")

# Display Detailed Video Info if available
if st.session_state.video_details:
    v = st.session_state.video_details
    mins, secs = divmod(v['duration'], 60)
    duration_str = f"{mins} دقيقة و {secs} ثانية" if mins > 0 else f"{secs} ثانية"
    views_str = f"{v['views']:,}".replace(',', '.') if v['views'] else "غير متوفر"
    
    st.markdown(f"""
        <div style="background-color: #121212; border: 2px solid #00E676; padding: 15px; border-radius: 12px; margin-bottom: 15px; box-shadow: 0 0 10px rgba(0,230,118,0.2);">
            <h4 style="color: #00E676; margin-top:0;">📊 معلومات الفيديو:</h4>
            <p><b>📌 العنوان:</b> {v['title']}</p>
            <p><b>👤 القناة / الناشر:</b> {v['uploader']}</p>
            <p><b>⏱️ المدة:</b> {duration_str}</p>
            <p><b>👁️ عدد المشاهدات:</b> {views_str}</p>
        </div>
    """, unsafe_allow_html=True)
    if v['thumbnail']:
        st.image(v['thumbnail'], width=300)

selected_videos = []
if st.session_state.playlist_entries:
    st.markdown(f"### 📋 الفيديوهات في قائمة: **{st.session_state.playlist_title}**")
    
    search_query = st.text_input("🔎 بحث سريع عن فيديو بالاسم داخل القائمة:", placeholder="اكتب للبحث...")
    
    # Radio with on_change callback to instantly update all checkbox states in session_state
    st.radio(
        "طريقة التحديد السريع:",
        ["تحديد الكل", "إلغاء الكل", "أول 10", "أول 20"],
        horizontal=True,
        key="sel_mode",
        on_change=on_selection_change
    )
    
    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
    for idx, entry in enumerate(st.session_state.playlist_entries):
        v_title = entry.get('title', f"فيديو #{idx+1}")
        
        if search_query and search_query.lower() not in v_title.lower():
            continue
            
        v_id = entry.get('id')
        v_url = entry.get('url') or entry.get('webpage_url') or f"https://www.youtube.com/watch?v={v_id}"
        
        thumbnail_url = entry.get('thumbnail')
        if not thumbnail_url and v_id:
            thumbnail_url = f"https://i.ytimg.com/vi/{v_id}/mqdefault.jpg"

        key = f"vid_{idx}"
        if key not in st.session_state:
            st.session_state[key] = True

        cols = st.columns([1, 3])
        with cols[0]:
            if thumbnail_url:
                st.image(thumbnail_url, use_container_width=True)
        with cols[1]:
            is_checked = st.checkbox(f"{idx+1}. {v_title}", key=key)
            if is_checked:
                selected_videos.append(v_url)
        st.markdown("---")

st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
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
                    'geo_bypass': True,
                    'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
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

                if st.session_state.playlist_entries and selected_videos:
                    with YoutubeDL(ydl_opts) as ydl:
                        ydl.download(selected_videos)
                    st.success(f"✅ تم بنجاح تحميل {len(selected_videos)} فيديو من القائمة!")
                    st.session_state.download_history.append(f"قائمة تشغيل: {st.session_state.playlist_title} ({len(selected_videos)} فيديو)")
                else:
                    ydl_opts['noplaylist'] = True
                    with YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        filename = ydl.prepare_filename(info)
                        v_title = info.get('title', 'فيديو')
                        
                        if "صوت" in quality or "MP3" in quality:
                            base, _ = os.path.splitext(filename)
                            filename = base + ".mp3"

                    if os.path.exists(filename):
                        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
                        st.success(f"✅ تم تجهيز الفيديو بنجاح! (الحجم: {file_size_mb:.1f} MB)")
                        st.session_state.download_history.download_history.append(f"فردي: {v_title} [{quality}]") if hasattr(st.session_state.download_history, 'download_history') else st.session_state.download_history.append(f"فردي: {v_title} [{quality}]")
                        
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

# Download History Section
if st.session_state.download_history:
    with st.expander("📜 سجل التحميلات السابقة (History)"):
        for item in reversed(st.session_state.download_history):
            st.markdown(f"- {item}")

st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 11px; color: gray;'>يعمل على Streamlit Community Cloud (متوافق مع جميع الأجهزة)</p>", unsafe_allow_html=True)
