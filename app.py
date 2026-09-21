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
# Page Configuration & Metadata
# ---------------------------------------------------------
st.set_page_config(
    page_title="MediaMaster Pro | محمل الفيديوهات الذكي",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# Advanced Design & Styling System (Glassmorphism + Neon Dark)
# ---------------------------------------------------------
st.html("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&family=Plus+Jakarta+Sans:wght@500;700;800&display=swap');
    
    :root {
        --primary: #00E676;
        --primary-glow: rgba(0, 230, 118, 0.35);
        --accent-cyan: #00f2fe;
        --accent-blue: #1877F2;
        --accent-pink: #FE2C55;
        --accent-insta: #E1306C;
        --accent-yt: #FF0000;
        --bg-dark: #080B11;
        --card-bg: rgba(18, 24, 38, 0.75);
        --card-border: rgba(255, 255, 255, 0.08);
        --card-hover: rgba(255, 255, 255, 0.14);
        --text-muted: #94A3B8;
    }
    
    html, body, [class*="css"] {
        font-family: 'Cairo', 'Plus Jakarta Sans', sans-serif !important;
        background-color: var(--bg-dark);
        color: #F8FAFC;
        direction: rtl;
        text-align: right;
    }
    
    /* Background Ambience */
    .stApp {
        background: radial-gradient(circle at 50% 0%, rgba(0, 230, 118, 0.09) 0%, transparent 50%),
                    radial-gradient(circle at 85% 20%, rgba(24, 119, 242, 0.07) 0%, transparent 45%),
                    radial-gradient(circle at 15% 30%, rgba(254, 44, 85, 0.07) 0%, transparent 45%),
                    #080B11;
        background-attachment: fixed;
    }
    
    /* Container block */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 780px !important;
    }
    
    /* Top Header Badge */
    .header-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 16px;
        border-radius: 999px;
        background: rgba(0, 230, 118, 0.1);
        border: 1px solid rgba(0, 230, 118, 0.3);
        color: var(--primary);
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 12px;
        box-shadow: 0 0 15px rgba(0, 230, 118, 0.15);
    }
    
    /* Hero Title */
    .hero-title {
        font-size: 32px;
        font-weight: 900;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #FFFFFF 30%, #CBD5E1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.25;
    }
    
    .hero-subtitle {
        color: var(--text-muted);
        font-size: 15px;
        font-weight: 600;
        margin-top: 6px;
        margin-bottom: 20px;
    }
    
    /* Platform Badges Row */
    .platform-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 24px;
    }
    .chip {
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 700;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.07);
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .chip-yt { color: #FF4D4D; border-color: rgba(255, 77, 77, 0.3); }
    .chip-fb { color: #38BDF8; border-color: rgba(56, 189, 248, 0.3); }
    .chip-ig { color: #F472B6; border-color: rgba(244, 114, 182, 0.3); }
    .chip-tt { color: #00F2FE; border-color: rgba(0, 242, 254, 0.3); }
    
    /* Glass Cards */
    .glass-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .glass-card:hover {
        border-color: var(--card-hover);
        box-shadow: 0 14px 40px rgba(0, 0, 0, 0.5);
    }
    
    /* Form Inputs */
    .stTextInput>div>div>input {
        border-radius: 12px !important;
        border: 1.5px solid rgba(255, 255, 255, 0.1) !important;
        background: rgba(15, 23, 42, 0.7) !important;
        color: #F8FAFC !important;
        padding: 14px 16px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.25s ease !important;
        direction: ltr !important;
        text-align: left !important;
    }
    .stTextInput>div>div>input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 20px var(--primary-glow) !important;
    }
    
    .stSelectbox>div>div {
        border-radius: 12px !important;
        border: 1.5px solid rgba(255, 255, 255, 0.1) !important;
        background: rgba(15, 23, 42, 0.7) !important;
        font-weight: 700 !important;
        color: #F8FAFC !important;
    }
    
    /* Action Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 12px !important;
        height: 52px !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        border: none !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        letter-spacing: 0.2px !important;
    }
    
    /* Primary Download Button */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #00E676 0%, #00B0FF 100%) !important;
        color: #050B14 !important;
        box-shadow: 0 4px 20px rgba(0, 230, 118, 0.35) !important;
    }
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(0, 230, 118, 0.55) !important;
        filter: brightness(1.08) !important;
    }
    
    /* Secondary Action Button */
    .stButton>button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.06) !important;
        color: #E2E8F0 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
    }
    .stButton>button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.12) !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Download Result Card */
    .stDownloadButton>button {
        width: 100%;
        border-radius: 12px !important;
        height: 54px !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 25px rgba(16, 185, 129, 0.45) !important;
        border: none !important;
        animation: pulse-glow 2s infinite ease-in-out;
    }
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4); }
        50% { box-shadow: 0 6px 30px rgba(16, 185, 129, 0.7); }
    }
    
    /* Info Badges */
    .badge-pill {
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
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00E676 0%, #00B0FF 100%) !important;
        border-radius: 999px !important;
    }
    
    /* Mobile responsive tweaks */
    @media (max-width: 640px) {
        .hero-title { font-size: 24px; }
        .hero-subtitle { font-size: 13px; }
        .glass-card { padding: 14px; }
        .stButton>button { height: 48px !important; font-size: 15px !important; }
    }
    </style>
""")

# ---------------------------------------------------------
# Helper Functions: URL Resolution & Platform Detection
# ---------------------------------------------------------
def resolve_url(input_url: str) -> str:
    """Resolve Facebook share, short links, or redirects to direct URLs."""
    input_url = input_url.strip()
    if not input_url:
        return input_url
    
    # Check if this is a share/redirect link
    share_domains = ["fb.watch", "/share/r/", "/share/v/", "fb.me", "vt.tiktok.com", "vm.tiktok.com", "youtu.be"]
    if any(k in input_url.lower() for k in share_domains):
        try:
            req = urllib.request.Request(
                input_url,
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
            return input_url
    return input_url


def detect_platform_from_url(url: str) -> str:
    """Intelligently detects social media platform from URL string."""
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
    """Format duration in seconds into human-readable Arabic string."""
    if not seconds or seconds <= 0:
        return "غير محدد"
    mins, secs = divmod(int(seconds), 60)
    hrs, mins = divmod(mins, 60)
    if hrs > 0:
        return f"{hrs} ساعة و {mins} دقيقة"
    elif mins > 0:
        return f"{mins} دقيقة و {secs} ثانية"
    return f"{secs} ثانية"


def format_number(num: int) -> str:
    """Format counts with K, M abbreviations."""
    if not num:
        return "غير متوفر"
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    if num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return f"{num:,}"


def sanitize_filename(name: str) -> str:
    """Sanitize filename to avoid Windows filesystem character errors."""
    clean = re.sub(r'[\\/*?:"<>|]', '', name)
    clean = clean.strip().strip('.')
    return clean[:120] if clean else "download"


# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if 'url_input' not in st.session_state:
    st.session_state.url_input = ""
if 'last_analyzed_url' not in st.session_state:
    st.session_state.last_analyzed_url = ""
if 'detected_platform' not in st.session_state:
    st.session_state.detected_platform = "YouTube"
if 'content_info' not in st.session_state:
    st.session_state.content_info = None
if 'playlist_entries' not in st.session_state:
    st.session_state.playlist_entries = None
if 'download_history' not in st.session_state:
    st.session_state.download_history = []
if 'download_ready' not in st.session_state:
    st.session_state.download_ready = None

# ---------------------------------------------------------
# UI Header Section
# ---------------------------------------------------------
col_h1, col_h2 = st.columns([5, 1])
with col_h1:
    st.html("""
        <div>
            <div class="header-badge">⚡ الجيل الثالث الذكي Pro V3</div>
            <h1 class="hero-title">أداة التحميل الشاملة للوسائط</h1>
            <p class="hero-subtitle">تحميل الفيديوهات، الريلز، الصوتيات بجودتها الأصلية بدون أي قيود</p>
        </div>
    """)
with col_h2:
    if st.button("🔄 تصفير", help="إعادة تعيين التطبيق ومسح البيانات المؤقتة", kind="secondary"):
        st.session_state.url_input = ""
        st.session_state.last_analyzed_url = ""
        st.session_state.content_info = None
        st.session_state.playlist_entries = None
        st.session_state.download_ready = None
        st.rerun()

# Platform Chips
st.html("""
    <div class="platform-chips">
        <span class="chip chip-yt">🔴 يوتيوب (4K / 60FPS)</span>
        <span class="chip chip-fb">🔵 ريلز فيسبوك (HD)</span>
        <span class="chip chip-ig">🟣 ريلز انستغرام (أصلي)</span>
        <span class="chip chip-tt">⚫ تيك توك (بدون علامة مائية)</span>
    </div>
""")

# ---------------------------------------------------------
# Input & Configuration Card
# ---------------------------------------------------------
with st.container():
    st.html("<div class='glass-card'>")
    
    # URL Input
    current_url = st.text_input(
        "رابط المحتوى أو الفيديو:",
        value=st.session_state.url_input,
        placeholder="https://www.facebook.com/reel/... أو https://youtube.com/...",
        help="انسخ الرابط من التطبيق أو المتصفح وضعه هنا"
    )
    
    # Update state if URL changed
    if current_url != st.session_state.url_input:
        st.session_state.url_input = current_url
        if current_url.strip():
            auto_plat = detect_platform_from_url(current_url)
            st.session_state.detected_platform = auto_plat
    
    # Platform & Quality Selectors
    col_p, col_q = st.columns([1, 1])
    
    platforms = ["YouTube", "Facebook Reels", "Instagram Reels", "TikTok Reels"]
    curr_idx = platforms.index(st.session_state.detected_platform) if st.session_state.detected_platform in platforms else 0
    
    with col_p:
        selected_platform = st.selectbox(
            "المنصة المحددة:",
            platforms,
            index=curr_idx,
            help="يتم التعرف عليها تلقائياً ويمكنك التغيير يدوياً"
        )
        if selected_platform != st.session_state.detected_platform:
            st.session_state.detected_platform = selected_platform
            
    with col_q:
        if "YouTube" in selected_platform:
            quality_options = [
                "🎬 أفضل جودة فائقة (Best / 4K / 60fps)",
                "💎 دقة 1080p Full HD (MP4)",
                "⚡ دقة 720p HD (MP4)",
                "🎵 صوت فقط فائق النقاء (MP3 - 320kbps)"
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
        else:  # Instagram Reels
            quality_options = [
                "🎬 أفضل جودة أصلية للريلز (Original HD)",
                "🎵 صوت الريلز فقط (MP3)"
            ]
            
        selected_quality = st.selectbox("الجودة / الصيغة المطلوبة:", quality_options)

    # Action Buttons Row (Analyze & Quick Actions)
    btn_col1, btn_col2 = st.columns([3, 1])
    with btn_col1:
        analyze_clicked = st.button("🔍 فحص وتحليل الرابط", kind="secondary")
    with btn_col2:
        clear_clicked = st.button("🗑️ مسح الرابط", kind="secondary")
        if clear_clicked:
            st.session_state.url_input = ""
            st.session_state.content_info = None
            st.session_state.download_ready = None
            st.rerun()

    st.html("</div>")

# ---------------------------------------------------------
# Processing: Link Inspection Logic
# ---------------------------------------------------------
if analyze_clicked:
    if not st.session_state.url_input.strip():
        st.warning("⚠️ الرجاء وضع الرابط أولاً ليتم تحليله!")
    else:
        with st.status("🔍 جاري فحص الرابط وفك التوجيه...", expanded=True) as status_box:
            try:
                resolved_url = resolve_url(st.session_state.url_input)
                status_box.write("⚡ جاري استخراج معلومات الفيديو المباشرة...")
                
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
                    info = ydl.extract_info(resolved_url, download=False)
                    
                    if not info:
                        status_box.update(label="❌ تعذر العثور على محتوى في هذا الرابط", state="error")
                    elif 'entries' in info and info['entries']:
                        # Playlist or Multi-item detected
                        st.session_state.playlist_entries = list(info['entries'])
                        st.session_state.content_info = {
                            'is_playlist': True,
                            'title': info.get('title', 'قائمة تشغيل'),
                            'count': len(st.session_state.playlist_entries)
                        }
                        status_box.update(label=f"✅ تم اكتشاف قائمة تشغيل تضم {len(st.session_state.playlist_entries)} فيديو!", state="complete")
                    else:
                        # Single Video / Reel
                        st.session_state.playlist_entries = None
                        title = info.get('title') or (info.get('description', '').split('\n')[0] if info.get('description') else None) or 'ريلز / فيديو'
                        duration = int(info.get('duration') or 0)
                        views = info.get('view_count', 0)
                        uploader = info.get('uploader') or info.get('channel') or 'غير معروف'
                        thumbnail = info.get('thumbnail')
                        
                        st.session_state.content_info = {
                            'is_playlist': False,
                            'title': title[:120],
                            'duration': duration,
                            'views': views,
                            'uploader': uploader,
                            'thumbnail': thumbnail,
                            'resolved_url': resolved_url
                        }
                        status_box.update(label="✅ تم تحليل المحتوى بنجاح! جاهز للتحميل الآن.", state="complete")
                        st.toast("✅ تم استخراج بيانات الفيديو بنجاح!", icon="🎉")
                        
            except Exception as ex:
                status_box.update(label=f"❌ حدث خطأ أثناء الفحص: {str(ex)[:100]}", state="error")
                st.error(f"تفاصيل الخطأ: {str(ex)}")

# ---------------------------------------------------------
# Content Preview Card
# ---------------------------------------------------------
if st.session_state.content_info:
    info = st.session_state.content_info
    
    if not info.get('is_playlist'):
        st.html("<div class='glass-card'>")
        c1, c2 = st.columns([1, 2])
        with c1:
            if info.get('thumbnail'):
                st.image(info['thumbnail'], use_container_width=True)
            else:
                st.html("<div style='height:120px; background:#1e293b; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:30px;'>🎬</div>")
        with c2:
            st.markdown(f"### {info['title']}")
            st.markdown(f"**👤 الناشر:** `{info['uploader']}`")
            st.html(f"""
                <div style="display:flex; gap:8px; margin-top:10px; flex-wrap:wrap;">
                    <span class="badge-pill">⏱️ المدة: {format_duration(info['duration'])}</span>
                    <span class="badge-pill">👁️ المشاهدات: {format_number(info['views'])}</span>
                    <span class="badge-pill">📌 المنصة: {st.session_state.detected_platform}</span>
                </div>
            """)
        st.html("</div>")
    else:
        st.info(f"📋 **قائمة تشغيل:** {info['title']} (عدد العناصر: {info['count']})")

# ---------------------------------------------------------
# Download Execution Logic with Live Progress
# ---------------------------------------------------------
download_btn_text = "🚀 بدء تحميل الفيديوهات المحددة" if st.session_state.playlist_entries else "🚀 بدء التحميل بأعلى جودة"

if st.button(download_btn_text, kind="primary"):
    if not st.session_state.url_input.strip():
        st.warning("⚠️ الرجاء إدخال الرابط أولاً!")
    else:
        progress_bar = st.progress(0, text="⚡ تحضير بيئة التنزيل المسرّعة...")
        progress_status = st.empty()
        
        def yt_dlp_hook(d):
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0:
                    pct = min(downloaded / total, 1.0)
                    progress_bar.progress(pct, text=f"⏳ جاري التحميل: {int(pct * 100)}%")
                speed = d.get('_speed_str', '')
                eta = d.get('_eta_str', '')
                progress_status.caption(f"⚡ السرعة الحالية: {speed} | الوقت المتبقي المقدر: {eta}")
            elif d['status'] == 'finished':
                progress_bar.progress(1.0, text="✨ تم اكتمال التنزيل! جاري التحويل والمعالجة النهائية...")
                progress_status.caption("🛠️ جاري إعداد الملف بصيغته النهائية...")
        
        temp_dir = tempfile.mkdtemp()
        try:
            target_url = resolve_url(st.session_state.url_input)
            
            ydl_opts = {
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'geo_bypass': True,
                'windowsfilenames': True,
                'progress_hooks': [yt_dlp_hook],
                'writeimages': True, # For TikTok photo slideshows
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
                },
                'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
            }
            
            # Format Selection Mapping
            is_audio_only = "صوت" in selected_quality or "MP3" in selected_quality
            
            if "YouTube" in selected_platform:
                if "1080p" in selected_quality:
                    ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best'
                elif "720p" in selected_quality:
                    ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'
                elif is_audio_only:
                    ydl_opts['format'] = 'bestaudio/best'
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '320',
                    }]
                else:
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'
            elif "Facebook" in selected_platform:
                if is_audio_only:
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
                if is_audio_only:
                    ydl_opts['format'] = 'bestaudio/best'
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                else:
                    ydl_opts['format'] = 'best/bestvideo+bestaudio'
                    
            ydl_opts['noplaylist'] = not bool(st.session_state.playlist_entries)
            
            with YoutubeDL(ydl_opts) as ydl:
                extract_result = ydl.extract_info(target_url, download=True)
                item_title = extract_result.get('title') if extract_result else "download"
                
            # Collect files in temp_dir
            downloaded_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
            
            if not downloaded_files:
                st.error("❌ لم يتم العثور على أي ملفات تم تنزيلها. تأكد من أن الفيديو متاح للعامة.")
            else:
                # Single or Multiple Files Handling
                if len(downloaded_files) == 1:
                    filepath = downloaded_files[0]
                    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
                    with open(filepath, "rb") as fp:
                        file_data = fp.read()
                    
                    filename_download = os.path.basename(filepath)
                    mime_type = "video/mp4"
                    if filename_download.endswith(".mp3"):
                        mime_type = "audio/mpeg"
                    elif filename_download.endswith((".jpg", ".jpeg", ".png", ".webp")):
                        mime_type = "image/jpeg"
                        
                    st.session_state.download_ready = {
                        'data': file_data,
                        'name': filename_download,
                        'mime': mime_type,
                        'size_mb': file_size_mb,
                        'title': item_title
                    }
                else:
                    # Package multiple items into a ZIP archive
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                        for f in downloaded_files:
                            zip_file.write(f, os.path.basename(f))
                    zip_data = zip_buffer.getvalue()
                    file_size_mb = len(zip_data) / (1024 * 1024)
                    zip_name = f"{sanitize_filename(item_title)}_album.zip"
                    
                    st.session_state.download_ready = {
                        'data': zip_data,
                        'name': zip_name,
                        'mime': "application/zip",
                        'size_mb': file_size_mb,
                        'title': f"حزمة من {len(downloaded_files)} ملفات"
                    }
                
                # Add to History
                time_str = datetime.now().strftime("%I:%M %p")
                st.session_state.download_history.append({
                    'title': item_title[:50],
                    'platform': selected_platform,
                    'format': selected_quality,
                    'time': time_str,
                    'size': f"{file_size_mb:.1f} MB"
                })
                
                st.toast("🎉 تم تجهيز الملف بنجاح! اضغط على زر التحميل أدناه.", icon="📥")
                
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء التحميل: {str(e)}")
        finally:
            # Clean up temp folder safely
            shutil.rmtree(temp_dir, ignore_errors=True)

# ---------------------------------------------------------
# Download Ready Trigger Button
# ---------------------------------------------------------
if st.session_state.download_ready:
    res = st.session_state.download_ready
    st.html(f"""
        <div class="glass-card" style="border-color: rgba(0, 230, 118, 0.4); background: rgba(0, 230, 118, 0.05); margin-top: 15px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                <div>
                    <h3 style="margin:0; color:#00E676; font-size:18px;">✅ جاهز للحفظ على جهازك!</h3>
                    <p style="margin:4px 0 0 0; color:#94A3B8; font-size:13px;"><b>الملف:</b> {res['name']} | <b>الحجم:</b> {res['size_mb']:.1f} MB</p>
                </div>
            </div>
        </div>
    """)
    
    st.download_button(
        label=f"💾 حفظ الملف الآن على هاتفك أو حاسوبك ({res['size_mb']:.1f} MB)",
        data=res['data'],
        file_name=res['name'],
        mime=res['mime'],
        use_container_width=True
    )

# ---------------------------------------------------------
# Download History Section
# ---------------------------------------------------------
if st.session_state.download_history:
    with st.expander(f"📜 سجل التحميلات السابقة ({len(st.session_state.download_history)} عمليات)", expanded=False):
        for item in reversed(st.session_state.download_history):
            st.html(f"""
                <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 14px; background:rgba(255,255,255,0.03); border-radius:10px; margin-bottom:8px; border:1px solid rgba(255,255,255,0.06);">
                    <div>
                        <b style="color:#F8FAFC;">{item['title']}</b>
                        <div style="font-size:12px; color:#94A3B8; margin-top:3px;">
                            {item['platform']} • {item['format']}
                        </div>
                    </div>
                    <div style="text-align:left;">
                        <span style="font-size:11px; background:rgba(0,230,118,0.1); color:#00E676; padding:3px 8px; border-radius:5px; font-weight:700;">{item['size']}</span>
                        <div style="font-size:11px; color:#64748B; margin-top:3px;">{item['time']}</div>
                    </div>
                </div>
            """)
            
        if st.button("🗑️ مسح السجل", kind="secondary"):
            st.session_state.download_history = []
            st.rerun()

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.html("""
    <div style="text-align:center; margin-top:40px; padding-top:20px; border-top:1px solid rgba(255,255,255,0.05); color:#64748B; font-size:12px;">
        MediaMaster Pro V3.0 • فائق السرعة • يدعم يوتيوب، تيك توك، انستغرام، وفيسبوك ريلز
    </div>
""")
