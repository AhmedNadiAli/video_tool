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
st.markdown("<p style='text-align: center; color: gray;'>يوتيوب • تيك توك • انستاجرام (مع اللصق التلقائي)</p>", unsafe_allow_html=True)

if 'playlist_entries' not in st.session_state:
    st.session_state.playlist_entries = None
if 'playlist_title' not in st.session_state:
    st.session_state.playlist_title = ""
if 'url_input' not in st.session_state:
    st.session_state.url_input = ""
if 'selection_mode' not in st.session_state:
    st.session_state.selection_mode = "all"

def reset_app():
    st.session_state.playlist_entries = None
    st.session_state.playlist_title = ""
    st.session_state.url_input = ""
    st.session_state.selection_mode = "all"
    st.rerun()

col_title, col_reset = st.columns([4, 1])
with col_reset:
    if st.button("🔄 إعادة ضبط"):
        reset_app()

platform = st.selectbox(
    "اختر المنصة:",
    ["YouTube", "TikTok Reels", "Instagram Reels"]
)

# URL Input with Auto-Paste helper info
col_url, col_paste = st.columns([4, 1])
with col_url:
    url = st.text_input("ألصق الرابط هنا:", value=st.session_state.url_input, placeholder="https://...", key="url_input")

with col_paste:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    # JavaScript clipboard reader button
    st.components.v1.html("""
        <button onclick="navigator.clipboard.readText().then(text => {
            const input = parent.document.querySelector('input[aria-label*=\\'ألصق الرابط هنا\\']');
            if(input) {
                input.value = text;
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
        })" style="background-color: #2b313e; color: white; border: 1px solid #ff4b4b; padding: 10px 15px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%;">📋 لصق</button>
    """, height=45)

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

if st.button("🔍 فحص الرابط واكتشاف المحتوى"):
    if not url.strip():
        st.warning("⚠️ الرجاء إدخال الرابط أولاً!")
    else:
        with st.spinner("⏳ جاري فحص الرابط واستخراج تفاصيل الفيديوهات والـ Thumbnails..."):
            try:
                ydl_opts = {'extract_flat': True, 'quiet': True}
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    if info and 'entries' in info:
                        st.session_state.playlist_entries = list(info['entries'])
                        st.session_state.playlist_title = info.get('title', 'قائمة تشغيل يوتيوب')
                        st.session_state.selection_mode = "all"
                        st.success(f"✅ تم اكتشاف قائمة تشغيل: '{st.session_state.playlist_title}' (عدد الفيديوهات: {len(st.session_state.playlist_entries)})")
                    else:
                        st.session_state.playlist_entries = None
                        st.info("ℹ️ هذا فيديو فردي وليس قائمة تشغيل. يمكنك الضغط على زر التحميل أدناه مباشرة.")
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء الفحص: {str(e)}")

selected_videos = []
if st.session_state.playlist_entries:
    st.markdown(f"### 📋 الفيديوهات في قائمة: **{st.session_state.playlist_title}**")
    
    search_query = st.text_input("🔎 بحث سريع عن فيديو بالاسم داخل القائمة:", placeholder="اكتب للبحث...")
    
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("تحديد الكل"):
        st.session_state.selection_mode = "all"
        st.rerun()
    if c2.button("إلغاء الكل"):
        st.session_state.selection_mode = "none"
        st.rerun()
    if c3.button("أول 10"):
        st.session_state.selection_mode = "first_10"
        st.rerun()
    if c4.button("أول 20"):
        st.session_state.selection_mode = "first_20"
        st.rerun()
    
    for idx, entry in enumerate(st.session_state.playlist_entries):
        v_title = entry.get('title', f"فيديو #{idx+1}")
        
        if search_query and search_query.lower() not in v_title.lower():
            continue
            
        v_id = entry.get('id')
        v_url = entry.get('url') or entry.get('webpage_url') or f"https://www.youtube.com/watch?v={v_id}"
        
        thumbnail_url = entry.get('thumbnail')
        if not thumbnail_url and v_id:
            thumbnail_url = f"https://i.ytimg.com/vi/{v_id}/mqdefault.jpg"

        default_val = True
        if st.session_state.selection_mode == "none":
            default_val = False
        elif st.session_state.selection_mode == "first_10":
            default_val = (idx < 10)
        elif st.session_state.selection_mode == "first_20":
            default_val = (idx < 20)
        elif st.session_state.selection_mode == "all":
            default_val = True

        cols = st.columns([1, 3])
        with cols[0]:
            if thumbnail_url:
                st.image(thumbnail_url, use_container_width=True)
        with cols[1]:
            is_checked = st.checkbox(f"{idx+1}. {v_title}", value=default_val, key=f"vid_{idx}")
            if is_checked:
                selected_videos.append(v_url)
        st.markdown("---")

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

                if st.session_state.playlist_entries and selected_videos:
                    with YoutubeDL(ydl_opts) as ydl:
                        ydl.download(selected_videos)
                    st.success(f"✅ تم بنجاح تحميل {len(selected_videos)} فيديو من القائمة!")
                else:
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
