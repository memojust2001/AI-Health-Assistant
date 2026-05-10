import streamlit as st
import pandas as pd

# --- 1. إعدادات الصفحة الفنية ---
st.set_page_config(page_title="AI Medical Hub | PhD Project", layout="wide", initial_sidebar_state="expanded")

# --- 2. محرك التنسيق المطور (Professional CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f8fafb; }
    .marquee { width: 100%; line-height: 45px; background-color: #1a5276; color: white; white-space: nowrap; overflow: hidden; position: relative; border-bottom: 3px solid #d4ac0d; }
    .marquee p { display: inline-block; padding-left: 100%; animation: marquee 25s linear infinite; font-size: 17px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #2874a6; color: white; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #e0f2f1; border-radius: 5px; padding: 10px; font-weight: bold; }
    .card { background-color: white; padding: 20px; border-radius: 12px; border-right: 8px solid #1a5276; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; direction: rtl; text-align: right; }
    </style>
    <div class="marquee"><p>🌐 منصة المساعد الطبي الذكي - نسخة الدكتوراه المحدثة 2026 | فحص الأعراض مقسم حسب الأجهزة | موسوعة الأدوية والتحاليل متوفرة الآن 🩺</p></div>
    """, unsafe_allow_html=True)

# --- 3. إدارة اللغة ---
if 'lang' not in st.session_state: st.session_state.lang = 'ar'
def switch_l(): st.session_state.lang = 'en' if st.session_state.lang == 'ar' else 'ar'

# --- 4. الهيدر العلوي ---
col_h1, col_h2 = st.columns([0.8, 0.2])
with col_h1:
    st.title("🏥 نظام التحليل الطبي والدوائي المتكامل")
with col_h2:
    st.button("🌐 Switch Language", on_click=switch_l)

# --- 5. الشريط الجانبي (البيانات + المساعد الذكي) ---
with st.sidebar:
    st.header("👤 ملف المريض")
    st.text_input("الاسم بالكامل")
    st.number_input("العمر", 1, 110)
    st.selectbox("فصيلة الدم", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
    
    st.divider()
    st.subheader("📊 العلامات الحيوية")
    st.text_input("ضغط الدم (Systolic/Diastolic)")
    st.text_input("مستوى السكر (mg/dL)")
    st.text_input("درجة الحرارة (C°)")
    
    st.divider()
    st.header("🤖 المساعد الذكي")
    st.info("تحدث مع AI Assistant")
    ai_q = st.text_area("اسألني أي سؤال طبي...")
    if st.button("إرسال للمساعد"):
        st.success("💬 جاري تحليل سؤالك برمجياً...")

# --- 6. فحص الأعراض (تبويبات أجهزة الجسم) ---
st.header("📋 محرك فحص الأعراض الشامل")
tabs = st.tabs(["❤️ الدوري", "🫁 التنفسي", "🤢 الهضمي", "🧠 العصبي", "🦴 الحركي"])

with tabs[0]:
    st.subheader("أعراض الجهاز الدوري")
    cv_s = st.multiselect("ماذا تشعر؟", ["نهجان سريع", "ألم في الصدر", "ضربات قلب غير منتظمة", "تورم القدمين"])
    st.button("التالي ➡️", key="c_next")

with tabs[1]:
    st.subheader("أعراض الجهاز التنفسي")
    resp_s = st.multiselect("ماذا تشعر؟", ["كحة جافة", "بلغم"، "ضيق تنفس", "تزييق صدر"])
    st.button("التالي ➡️", key="r_next")

# زر استخراج التشخيص (المنطق المدمج)
if st.button("🔍 تحليل الحالة واستخراج التوصيات"):
    st.divider()
    st.subheader("🩺 نتائج التحليل السريري المبدئي")
    c1, c2 = st.columns(2)
    with c1:
        st.warning("**التشخيص المتوقع:**")
        st.write("1. اشتباه في إجهاد عضلة القلب")
        st.info("**طرق الوقاية:** الراحة، تقليل الصوديوم، متابعة الضغط.")
    with c2:
        st.success("**الأدوية والتحاليل:**")
        st.write("- أدوية مقترحة: Aspirin 81mg")
        st.write("- تحاليل مطلوبة: ECG / CBC / Lipid Profile")

# --- 7. موسوعة الأدوية (نظام DwaPrices المطور) ---
st.divider()
st.header("💊 دليل الأدوية والبدائل")
drug_search = st.text_input("🔍 ابحث عن دواء (الاسم أو المادة الفعالة):")

# قاعدة بيانات مصغرة (أمثلة)
meds = [
    {"n": "Augmentin", "a": "Amoxicillin", "u": "مضاد حيوي", "alt": "Hibiotic, Curam"},
    {"n": "Panadol", "a": "Paracetamol", "u": "مسكن"، "alt": "Adol, Abimol"}
]

if drug_search:
    results = [m for m in meds if drug_search.lower() in m['n'].lower() or drug_search.lower() in m['a'].lower()]
    for r in results:
        st.markdown(f"""
        <div class="card">
            <h3 style="color: #1a5276;">{r['n']}</h3>
            <p><b>المادة الفعالة:</b> {r['a']} | <b>الاستخدام:</b> {r['u']}</p>
            <p style="color: #d35400;"><b>🔄 البدائل المتاحة:</b> {r['alt']}</p>
        </div>
        """, unsafe_allow_html=True)

# --- 8. وحدة التحاليل الطبية (نظام علمي) ---
st.divider()
st.header("🔬 وحدة التحاليل المختبرية")
lab_search = st.text_input("🔍 ابحث عن تحليل معين:")

labs = [
    {"n": "صورة دم (CBC)", "f": "خلايا الدم والأنيميا", "t": "لا يشترط الصيام"},
    {"n": "سكر تراكمي (HbA1c)", "f": "معدل السكر في 3 شهور", "t": "لا يشترط الصيام"}
]

if lab_search:
    res_l = [l for l in labs if lab_search.lower() in l['n'].lower()]
    for l in res_l:
        st.markdown(f"""
        <div class="card" style="border-right-color: #008080;">
            <h3 style="color: #004d40;">{l['n']}</h3>
            <p><b>🎯 الهدف:</b> {l['f']}</p>
            <p style="color: #00695c;"><b>⚠️ التعليمات:</b> {l['t']}</p>
        </div>
        """, unsafe_allow_html=True)
