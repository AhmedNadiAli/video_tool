import os
import re
import io
import time
import shutil
import zipfile
import tempfile
import urllib.request
from datetime import datetime
import streamlit as st
from yt_dlp import YoutubeDL

# ---------------------------------------------------------
# 1. إعدادات الصفحة الأساسية (Page Configuration)
# ---------------------------------------------------------
st.set_page_config(
    page_title="MediaMaster Pro | محمل الفيديوهات الشامل",
    page_icon="📥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# 2. نظام التصميم والأنماط (Modern Glassmorphism UI)
# متوافق 100% مع جميع إصدارات Streamlit المحلية و Streamlit Cloud
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&family=Plus+Jakarta+Sans:wght@500;700;800&display=swap');
    
    :root {
        --primary: #00E676;
        --primary-hover: #00C853;
        --accent-blue: #1877F2;
        --accent-cyan: #00F2FE;
        --bg-dark: #080B11;
        --card-bg: rgba(17, 24, 39, 0.75);
        --card-border: rgba(255, 255, 255, 0.08);
        --text-main: #F8FAFC;
        --text-muted: #94A3B8;
    }
    
    html, body, [class*="css"] {
        font-family: 'Cairo', 'Plus Jakarta Sans', sans-serif !important;
        background-color: var(--bg-dark);
        color: var(--text-main);
        direction: rtl;
        text-align: right;
    }
    
    /* خلفية متدرجة عصرية مع إضاءات ناعمة */
    .stApp {
        background: radial-gradient(circle at 50% 0%, rgba(0, 230, 118, 0.08) 0%, transparent 50%),
                    radial-gradient(circle at 90% 15%, rgba(24, 119, 242, 0.08) 0%, transparent 40%),
                    radial-gradient(circle at 10% 25%, rgba(254, 44, 85, 0.07) 0%, transparent 40%),
                    var(--bg-dark);
        background-attachment: fixed;
    }
    
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 3rem !important;
        max-width: 780px !important;
    }
    
    /* شارة الترويسة */
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 5px 14px;
        border-radius: 999px;
        background: rgba(0, 230, 118, 0.12);
        border: 1px solid rgba(0, 230, 118, 0.35);
        color: var(--primary);
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 12px;
        box-shadow: 0 0 15px rgba(0, 230, 118, 0.15);
    }
    
    /* العناوين */
    .hero-title {
        font-size: 32px;
        font-weight: 900;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #FFFFFF 30%, #CBD5E1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.3;
    }
    
    .hero-desc {
        color: var(--text-muted);
        font-size: 14px;
        font-weight: 600;
        margin-top: 6px;
        margin-bottom: 20px;
    }
    
    /* شارات المنصات */
    .platforms-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 22px;
    }
    .p-tag {
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 700;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .p-yt { color: #FF4D4D; border-color: rgba(255, 77, 77, 0.3); }
    .p-fb { color: #38BDF8; border-color: rgba(56, 189, 248, 0.3); }
    .p-ig { color: #F472B6; border-color: rgba(244, 114, 182, 0.3); }
    .p-tt { color: #00F2FE; border-color: rgba(0, 242, 254, 0.3); }
    
    /* بطاقة زجاجية */
    .glass-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        margin-bottom: 20px;
        transition: border 0.3s ease;
    }
    .glass-card:hover {
        border-color: rgba(255, 255, 255, 0.16);
    }
    
    /* حقول الإدخال */
    .stTextInput>div>div>input {
        border-radius: 12px !important;
        border: 1.5px solid rgba(255, 255, 255, 0.1) !important;
        background: rgba(15, 23, 42, 0.75) !important;
        color: #F8FAFC !important;
        padding: 12px 16px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        direction: ltr !important;
        text-align: left !important;
        transition: all 0.25s ease !important;
    }
    .stTextInput>div>div>input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 15px rgba(0, 230, 118, 0.3) !important;
    }
    
    .stSelectbox>div>div {
        border-radius: 12px !important;
        border: 1.5px solid rgba(255, 255, 255, 0.1) !important;
        background: rgba(15, 23, 42, 0.75) !important;
        font-weight: 700 !important;
        color: #F8FAFC !important;
    }
    
    /* الأزرار العصرية */
    .stButton>button {
        width: 100%;
        border-radius: 12px !important;
        height: 50px !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        background: rgba(255, 255, 255, 0.06) !important;
        color: #F8FAFC !important;
        transition: all 0.25s ease !important;
    }
    .stButton>button:hover {
        background: rgba(255, 255, 255, 0.12) !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
        transform: translateY(-1px) !important;
    }
    
    /* زر التحميل الأساسي */
    .stButton>button[kind="primary"], .stButton>button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #00E676 0%, #00B0FF 100%) !important;
        color: #050B14 !important;
        border: none !important;
        box-shadow: 0 4px 20px rgba(0, 230, 118, 0.35) !important;
    }
    .stButton>button[kind="primary"]:hover, .stButton>button[data-testid="stBaseButton-primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(0, 230, 118, 0.55) !important;
        filter: brightness(1.08) !important;
    }
    
    /* زر تنزيل الملف النهائي */
    .stDownloadButton>button {
        width: 100%;
        border-radius: 12px !important;
        height: 52px !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.45) !important;
        transition: all 0.25s ease !important;
    }
    .stDownloadButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.65) !important;
    }
    
    /* شريط التقدم */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00E676 0%, #00B0FF 100%) !important;
        border-radius: 999px !important;
    }
    
    .badge-info {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
        background: rgba(255, 255, 255, 0.06);
        color: #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. الدوال المساعدة وتتبع الروابط (Helper Functions)
# ---------------------------------------------------------
def resolve_url(url: str) -> str:
    """تتبع الروابط المختصرة وروابط المشاركة لاستخراج الرابط الأصلي المباشر."""
    u = url.strip()
    if not u:
        return u
    short_domains = ["fb.watch", "/share/r/", "/share/v/", "fb.me", "vt.tiktok.com", "vm.tiktok.com", "youtu.be"]
    if any(k in u.lower() for k in short_domains):
        try:
            req = urllib.request.Request(
                u,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
                }
            )
            opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)
            with opener.open(req, timeout=8) as response:
                final_url = response.geturl()
                if final_url:
                    return final_url
        except Exception:
            return u
    return u


def detect_platform(url: str) -> str:
    """التعرف التلقائي على المنصة بناءً على الرابط."""
    u = url.lower().strip()
    if "tiktok.com" in u:
        return "TikTok Reels"
    elif "instagram.com" in u:
        return "Instagram Reels"
    elif any(fb in u for fb in ["facebook.com", "fb.watch", "fb.com", "fb.me"]):
        return "Facebook Reels"
    else:
        return "YouTube"


def format_duration(seconds: int) -> str:
    """تحويل الثواني إلى صيغة وقت مقروءة بالعربية."""
    if not seconds or seconds <= 0:
        return "غير محدد"
    mins, secs = divmod(int(seconds), 60)
    hrs, mins = divmod(mins, 60)
    if hrs > 0:
        return f"{hrs} ساعة و {mins} دقيقة"
    elif mins > 0:
        return f"{mins} دقيقة و {secs} ثانية"
    return f"{secs} ثانية"


def format_views(count: int) -> str:
    """تنسيق أرقام المشاهدات بصيغة K أو M."""
    if not count:
        return "غير متوفر"
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    if count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return f"{count:,}"


def sanitize_filename(name: str) -> str:
    """تنظيف اسم الملف من الحروف والرموز الممنوعة في نظام ويندوز."""
    clean = re.sub(r'[\\/*?:"<>|]', '', name)
    clean = clean.strip().strip('.')
    return clean[:90] if clean else "media_file"

# ---------------------------------------------------------
# 4. إدارة حالة الجلسة (Session State)
# ---------------------------------------------------------
if 'url_input' not in st.session_state:
    st.session_state.url_input = ""
if 'detected_platform' not in st.session_state:
    st.session_state.detected_platform = "YouTube"
if 'content_info' not in st.session_state:
    st.session_state.content_info = None
if 'download_ready' not in st.session_state:
    st.session_state.download_ready = None
if 'download_history' not in st.session_state:
    st.session_state.download_history = []

# ---------------------------------------------------------
# 5. الترويسة الرئيسية (Main Header)
# ---------------------------------------------------------
col_h1, col_h2 = st.columns([5, 1])
with col_h1:
    st.markdown("""
        <div>
            <div class="hero-badge">⚡ الجيل الثالث الذكي Pro V3</div>
            <h1 class="hero-title">أداة التحميل الشاملة للوسائط</h1>
            <p class="hero-desc">تحميل ريلز فيسبوك، انستغرام، يوتيوب، وتيك توك بأعلى جودة أصلية وبدون قيود</p>
        </div>
    """, unsafe_allow_html=True)
with col_h2:
    if st.button("🔄 تصفير", help="إعادة تعيين ومسح البيانات"):
        st.session_state.url_input = ""
        st.session_state.content_info = None
        st.session_state.download_ready = None
        st.rerun()

st.markdown("""
    <div class="platforms-row">
        <span class="p-tag p-yt">🔴 يوتيوب (4K / 60FPS)</span>
        <span class="p-tag p-fb">🔵 ريلز فيسبوك (HD)</span>
        <span class="p-tag p-ig">🟣 ريلز انستغرام (أصلي)</span>
        <span class="p-tag p-tt">⚫ تيك توك (بدون علامة مائية)</span>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. بطاقة إدخال الرابط وتحديد الجودة (Input Card)
# ---------------------------------------------------------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

current_url = st.text_input(
    "رابط الفيديو أو الريلز:",
    value=st.session_state.url_input,
    placeholder="ألصق الرابط هنا (https://www.facebook.com/reel/... أو يوتيوب / تيك توك)"
)

# التعرف التلقائي عند تغيير الرابط
if current_url != st.session_state.url_input:
    st.session_state.url_input = current_url
    if current_url.strip():
        st.session_state.detected_platform = detect_platform(current_url)

col_p, col_q = st.columns([1, 1])

platform_options = ["YouTube", "Facebook Reels", "Instagram Reels", "TikTok Reels"]
p_idx = platform_options.index(st.session_state.detected_platform) if st.session_state.detected_platform in platform_options else 0

with col_p:
    selected_platform = st.selectbox("المنصة المكتشفة:", platform_options, index=p_idx)
    if selected_platform != st.session_state.detected_platform:
        st.session_state.detected_platform = selected_platform

with col_q:
    if "YouTube" in selected_platform:
        quality_options = [
            "🎬 أفضل جودة فائقة (Best / 4K / 60fps)",
            "💎 دقة 1080p Full HD (MP4)",
            "⚡ دقة 720p HD (MP4)",
            "🎵 صوت فقط عالي النقاء (MP3 - 320kbps)"
        ]
    elif "Facebook" in selected_platform:
        quality_options = [
            "🎬 أفضل جودة أصلية للريلز (HD)",
            "⚡ جودة قياسية سريعة (SD)",
            "🎵 صوت الريلز فقط (MP3)"
        ]
    elif "TikTok" in selected_platform:
        quality_options = [
            "🎬 أفضل جودة أصلية (بدون علامة مائية)",
            "📸 صور المنشور كاملة (Slideshow Photos)",
            "🎵 صوت التيك توك فقط (MP3)"
        ]
    else:  # Instagram
        quality_options = [
            "🎬 أفضل جودة أصلية للريلز (Original HD)",
            "🎵 صوت الريلز فقط (MP3)"
        ]
        
    selected_quality = st.selectbox("الجودة / الصيغة المطلوبة:", quality_options)

col_b1, col_b2 = st.columns([3, 1])
with col_b1:
    analyze_btn = st.button("🔍 فحص وتحليل الرابط")
with col_b2:
    if st.button("🗑️ مسح الرابط"):
        st.session_state.url_input = ""
        st.session_state.content_info = None
        st.session_state.download_ready = None
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. فحص الرابط واستخراج المعلومات (Inspect URL)
# ---------------------------------------------------------
if analyze_btn:
    if not st.session_state.url_input.strip():
        st.warning("⚠️ الرجاء وضع الرابط أولاً ليتم تحليله!")
    else:
        with st.spinner("🔍 جاري فحص الرابط واستخراج بيانات المحتوى..."):
            try:
                clean_url = resolve_url(st.session_state.url_input)
                ydl_opts = {
                    'extract_flat': True,
                    'quiet': True,
                    'geo_bypass': True,
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
                    },
                    'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
                }
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(clean_url, download=False)
                    
                    if not info:
                        st.error("❌ تعذر العثور على محتوى متاح عبر هذا الرابط.")
                    else:
                        title = info.get('title') or (info.get('description', '').split('\n')[0] if info.get('description') else None) or 'ريلز / فيديو'
                        duration = int(info.get('duration') or 0)
                        views = info.get('view_count', 0)
                        uploader = info.get('uploader') or info.get('channel') or 'غير معروف'
                        thumbnail = info.get('thumbnail')
                        
                        st.session_state.content_info = {
                            'title': title[:110],
                            'duration': duration,
                            'views': views,
                            'uploader': uploader,
                            'thumbnail': thumbnail,
                            'clean_url': clean_url
                        }
                        st.success("✅ تم فحص المحتوى بنجاح! يمكنك الآن الضغط على زر التحميل أدناه.")
            except Exception as ex:
                err_msg = str(ex)
                if "Private" in err_msg or "login" in err_msg:
                    st.error("🔒 هذا الفيديو خاص أو يتطلب تسجيل دخول للوصول إليه.")
                elif "not found" in err_msg or "404" in err_msg:
                    st.error("❌ تم حذف هذا الفيديو أو أن الرابط غير صحيح.")
                else:
                    st.error(f"❌ حدث خطأ أثناء الفحص: {err_msg[:120]}")

# ---------------------------------------------------------
# 8. بطاقة المعاينة المرئية (Preview Card)
# ---------------------------------------------------------
if st.session_state.content_info:
    info = st.session_state.content_info
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1:
        if info.get('thumbnail'):
            st.image(info['thumbnail'], use_container_width=True)
        else:
            st.markdown("<div style='height:120px; background:#1e293b; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:32px;'>🎬</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"### {info['title']}")
        st.markdown(f"**👤 الناشر:** `{info['uploader']}`")
        st.markdown(f"""
            <div style="display:flex; gap:8px; margin-top:10px; flex-wrap:wrap;">
                <span class="badge-info">⏱️ المدة: {format_duration(info['duration'])}</span>
                <span class="badge-info">👁️ المشاهدات: {format_views(info['views'])}</span>
                <span class="badge-info">📌 المنصة: {st.session_state.detected_platform}</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 9. محرك التحميل المتطور (Download Engine with Live Telemetry)
# ---------------------------------------------------------
if st.button("🚀 بدء التحميل بأعلى جودة", type="primary"):
    if not st.session_state.url_input.strip():
        st.warning("⚠️ الرجاء إدخال الرابط أولاً!")
    else:
        p_bar = st.progress(0, text="⚡ جاري الاتصال بالخادم وتحضير التنزيل...")
        p_label = st.empty()
        
        def progress_callback(d):
            if d.get('status') == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0:
                    pct = min(downloaded / total, 1.0)
                    p_bar.progress(pct, text=f"⏳ جاري التحميل: {int(pct * 100)}%")
                speed = d.get('_speed_str', '')
                eta = d.get('_eta_str', '')
                p_label.caption(f"⚡ السرعة الحالية: {speed} | الوقت المقدر المتبقي: {eta}")
            elif d.get('status') == 'finished':
                p_bar.progress(1.0, text="✨ اكتمل التنزيل! جاري معالجة وتجهيز الملف...")
                p_label.caption("🛠️ جاري التحويل النهائي...")
                
        temp_dir = tempfile.mkdtemp()
        try:
            target_url = resolve_url(st.session_state.url_input)
            
            ydl_opts = {
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'geo_bypass': True,
                'windowsfilenames': True,
                'progress_hooks': [progress_callback],
                'writeimages': True, # يدعم صور منشورات تيك توك
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
                },
                'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
            }
            
            is_audio = "صوت" in selected_quality or "MP3" in selected_quality
            
            if "YouTube" in selected_platform:
                if "1080p" in selected_quality:
                    ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best'
                elif "720p" in selected_quality:
                    ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'
                elif is_audio:
                    ydl_opts['format'] = 'bestaudio/best'
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '320',
                    }]
                else:
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'
            elif "Facebook" in selected_platform:
                if is_audio:
                    ydl_opts['format'] = 'bestaudio/best'
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                elif "SD" in selected_quality:
                    ydl_opts['format'] = 'sd/worst[ext=mp4]/best'
                else:
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'
            else:
                # TikTok & Instagram
                if is_audio:
                    ydl_opts['format'] = 'bestaudio/best'
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                else:
                    ydl_opts['format'] = 'best/bestvideo+bestaudio'
                    
            ydl_opts['noplaylist'] = True
            
            with YoutubeDL(ydl_opts) as ydl:
                res = ydl.extract_info(target_url, download=True)
                title = res.get('title') if res else "download"
                
            files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
            
            if not files:
                st.error("❌ لم يتم العثور على الملف بعد التنزيل. تأكد من أن الرابط متاح للعامة.")
            else:
                if len(files) == 1:
                    filepath = files[0]
                    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
                    with open(filepath, "rb") as f:
                        file_bytes = f.read()
                        
                    dl_name = os.path.basename(filepath)
                    mime = "video/mp4"
                    if dl_name.endswith(".mp3"):
                        mime = "audio/mpeg"
                    elif dl_name.endswith((".jpg", ".jpeg", ".png", ".webp")):
                        mime = "image/jpeg"
                        
                    st.session_state.download_ready = {
                        'data': file_bytes,
                        'name': dl_name,
                        'mime': mime,
                        'size_mb': file_size_mb,
                        'title': title
                    }
                else:
                    # تجميع صور الألبوم المتعددة داخل ملف ZIP
                    buf = io.BytesIO()
                    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                        for f in files:
                            zf.write(f, os.path.basename(f))
                    zip_data = buf.getvalue()
                    file_size_mb = len(zip_data) / (1024 * 1024)
                    dl_name = f"{sanitize_filename(title)}_album.zip"
                    
                    st.session_state.download_ready = {
                        'data': zip_data,
                        'name': dl_name,
                        'mime': "application/zip",
                        'size_mb': file_size_mb,
                        'title': title
                    }
                    
                time_str = datetime.now().strftime("%I:%M %p")
                st.session_state.download_history.append({
                    'title': title[:50],
                    'platform': selected_platform,
                    'format': selected_quality,
                    'time': time_str,
                    'size': f"{file_size_mb:.1f} MB"
                })
                
                st.success("🎉 تم تجهيز الملف بنجاح! اضغط على زر الحفظ أدناه.")
                
        except Exception as e:
            err = str(e)
            if "Sign in" in err or "bot" in err.lower():
                st.error("⚠️ تطلب المنصة التحقق أو تسجيل الدخول للوصول إلى هذا المحتوى.")
            else:
                st.error(f"❌ حدث خطأ أثناء التحميل: {err[:140]}")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

# ---------------------------------------------------------
# 10. زر تسليم وحفظ الملف على جهاز المستخدم (Download Ready)
# ---------------------------------------------------------
if st.session_state.download_ready:
    r = st.session_state.download_ready
    st.markdown(f"""
        <div class="glass-card" style="border-color: rgba(0, 230, 118, 0.45); background: rgba(0, 230, 118, 0.06); margin-top: 15px;">
            <h3 style="margin:0; color:#00E676; font-size:18px;">✅ تم تجهيز الملف بنجاح!</h3>
            <p style="margin:4px 0 0 0; color:#94A3B8; font-size:13px;"><b>الملف:</b> {r['name']} | <b>الحجم:</b> {r['size_mb']:.1f} MB</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.download_button(
        label=f"💾 حفظ الملف الآن على جهازك ({r['size_mb']:.1f} MB)",
        data=r['data'],
        file_name=r['name'],
        mime=r['mime'],
        use_container_width=True
    )

# ---------------------------------------------------------
# 11. سجل التحميلات السابقة (History Section)
# ---------------------------------------------------------
if st.session_state.download_history:
    with st.expander(f"📜 سجل التحميلات السابقة ({len(st.session_state.download_history)} عمليات)"):
        for item in reversed(st.session_state.download_history):
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 14px; background:rgba(255,255,255,0.03); border-radius:10px; margin-bottom:8px; border:1px solid rgba(255,255,255,0.06);">
                    <div>
                        <b style="color:#F8FAFC;">{item['title']}</b>
                        <div style="font-size:12px; color:#94A3B8; margin-top:3px;">{item['platform']} • {item['format']}</div>
                    </div>
                    <div style="text-align:left;">
                        <span style="font-size:11px; background:rgba(0,230,118,0.12); color:#00E676; padding:3px 8px; border-radius:5px; font-weight:700;">{item['size']}</span>
                        <div style="font-size:11px; color:#64748B; margin-top:3px;">{item['time']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        if st.button("🗑️ مسح السجل"):
            st.session_state.download_history = []
            st.rerun()

# ---------------------------------------------------------
# 12. تذييل الصفحة (Footer)
# ---------------------------------------------------------
st.markdown("""
    <div style="text-align:center; margin-top:40px; padding-top:20px; border-top:1px solid rgba(255,255,255,0.05); color:#64748B; font-size:12px;">
        MediaMaster Pro V3.0 • سريع وخفيف • يدعم ريلز فيسبوك، انستغرام، يوتيوب، وتيك توك
    </div>
""", unsafe_allow_html=True)
