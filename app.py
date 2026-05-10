import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Egypt Health Pro", layout="wide")

# --- محرك التنسيق (CSS) لضبط الاتجاه والعناصر ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 20px; font-weight: bold; transition: 0.3s; }
    .navbar { display: flex; justify-content: space-around; background: #1a5276; padding: 15px; border-radius: 10px; margin-bottom: 25px; }
    .nav-item { color: white; cursor: pointer; text-decoration: none; font-weight: bold; }
    .main-card { background: white; padding: 25px; border-radius: 15px; border-right: 5px solid #d4ac0d; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .marquee { background: #2c3e50; color: #f1c40f; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
    </style>
    <div class="marquee"><marquee direction="right">مرحباً بك في منصة مصر الطبية الذكية | تحديثات قاعدة بيانات الأدوية من مراجع روشتاتولوجي وامتيازولوجي 2026 | المساعد الذكي متاح الآن </marquee></div>
    """, unsafe_allow_html=True)

# --- إدارة الحالة (Session State) ---
if 'page' not in st.session_state: st.session_state.page = 'login'
if 'lang' not in st.session_state: st.session_state.lang = 'ar'

# دالة التنقل
def go_to(page_name): st.session_state.page = page_name

# --- 1. صفحة تسجيل الدخول ---
if st.session_state.page == 'login':
    st.markdown("<h2 style='text-align:center;'>🔐 تسجيل دخول المنصة</h2>", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.text_input("رقم التليفون أو الإيميل")
            st.text_input("كلمة المرور", type="password")
            if st.button("دخول"): go_to('home')
            st.button("إنشاء حساب جديد")

# --- الهيدر العام (يظهر بعد الدخول) ---
if st.session_state.page != 'login':
    # أزرار التنقل العلوية
    cols = st.columns([1,1,1,1,1,1])
    with cols[0]: st.button("🏠 الرئيسية", on_click=lambda: go_to('home'))
    with cols[1]: st.button("📋 فحص الأعراض", on_click=lambda: go_to('symptoms'))
    with cols[2]: st.button("💊 دليل الأدوية", on_click=lambda: go_to('drugs'))
    with cols[3]: st.button("🔬 المختبر", on_click=lambda: go_to('lab'))
    with cols[4]: st.button("🤖 المساعد الذكي", on_click=lambda: go_to('ai'))
    with cols[5]: st.button("🌐 English/عربي")

    st.divider()

    # --- 2. الصفحة الرئيسية ---
    if st.session_state.page == 'home':
        st.markdown("<div class='main-card'><h3>👋 مرحباً بك في لوحة التحكم الطبية</h3><p>اختر أحد الأقسام من الأعلى للبدء. الموقع مصمم لخدمة المرضى والأطباء بناءً على بروتوكولات وزارة الصحة المصرية.</p></div>", unsafe_allow_html=True)

    # --- 3. صفحة فحص الأعراض (مرصوصة للأجهزة) ---
    elif st.session_state.page == 'symptoms':
        st.header("📋 فحص الأعراض - أجهزة الجسم")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.subheader("❤️ الجهاز الدوري")
            st.checkbox("نهجان شديد")
            st.checkbox("ألم في منتصف الصدر")
            st.checkbox("خفقان (ضربات سريعة)")
            st.checkbox("تورم في القدمين")
            
        with col_s2:
            st.subheader("🫁 الجهاز التنفسي")
            st.checkbox("كحة ناشفة")
            st.checkbox("كحة ببلغم")
            st.checkbox("تزييق في الصدر")
            st.checkbox("نهجان مع الكلام")
        
        st.divider()
        if st.button("🔍 عرض التشخيص والتحاليل المطلوبة"):
            st.info("بناءً على مراجع (امتيازولوجي): الحالة تستدعي عمل رسم قلب وأشعة صدر.")

    # --- 4. صفحة الأدوية (البحث الشامل) ---
    elif st.session_state.page == 'drugs':
        st.header("💊 محرك بحث الأدوية (Drug Eye Style)")
        search = st.text_input("اكتب اسم الدواء (مثلاً: Adol, Aspirin, Augmentin)...")
        
        alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        st.write("أو اختر بالحرف:")
        st.radio("الحروف", alphabet, horizontal=True)
        
        if search:
            st.success(f"نتائج البحث عن: {search}")
            # مثال لبيانات
            st.markdown("""
            **تفاصيل الدواء:**
            * **المادة الفعالة:** Paracetamol
            * **التركيز:** 500mg
            * **دواعي الاستعمال:** خافض للحرارة ومسكن للآلام.
            * **موانع الاستعمال:** خلل وظائف الكبد.
            """)

    # --- 5. صفحة المختبر (خانات التحاليل) ---
    elif st.session_state.page == 'lab':
        st.header("🔬 المختبر الطبي الرقمي")
        analysis_type = st.selectbox("اختر نوع التحليل:", ["CBC (صورة دم كاملة)", "وظائف كبد", "وظائف كلى"])
        
        if analysis_type == "CBC (صورة دم كاملة)":
            st.write("أدخل القيم كما هي في ورقة التحليل:")
            c1, c2, c3 = st.columns(3)
            with c1: hb = st.number_input("Hemoglobin (Hb)", 0.0, 20.0)
            with c2: wbc = st.number_input("WBCs", 0, 50000)
            with c3: plt = st.number_input("Platelets", 0, 1000000)
            
            if st.button("تحليل النتائج"):
                if hb < 12: st.error("توجد أنيميا (فقر دم).")
                else: st.success("نسبة الهيموجلوبين طبيعية.")

    # --- 6. المساعد الذكي ---
    elif st.session_state.page == 'ai':
        st.header("🤖 المساعد الطبي الذكي (Gemini AI)")
        user_q = st.text_input("اسأل المساعد عن أي معلومة طبية:")
        if st.button("إرسال"):
            st.write("💬 المساعد: جاري تحليل سؤالك بناءً على الكتب الطبية المصرية...")