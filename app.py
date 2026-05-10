import streamlit as st

# --- 1. إعدادات الصفحة الفنية ---
st.set_page_config(page_title="AI Medical Hub | PhD Project", layout="wide")

# --- 2. محرك التنسيق الاحترافي (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f0f4f8; }
    .marquee { width: 100%; line-height: 50px; background-color: #1a5276; color: white; white-space: nowrap; overflow: hidden; position: relative; border-bottom: 3px solid #d4ac0d; }
    .marquee p { display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite; font-size: 18px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #2874a6; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #1a5276; border: 1px solid #d4ac0d; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    </style>
    <div class="marquee"><p>🌐 منصة المساعد الطبي الذكي - تحديثات 2026: قسم الأدوية الشامل متاح الآن | فحص الأعراض مقسم حسب أجهزة الجسم | استشر طبيبك دائماً قبل أي إجراء 🩺</p></div>
    """, unsafe_allow_html=True)

# --- 3. الجلسة واللغة ---
if 'lang' not in st.session_state: st.session_state.lang = 'ar'
def switch_l(): st.session_state.lang = 'en' if st.session_state.lang == 'ar' else 'ar'

# --- 4. الهيدر ---
col_head1, col_head2 = st.columns([0.8, 0.2])
with col_head1:
    st.title("🏥 نظام التحليل الطبي والدوائي المتكامل")
with col_head2:
    st.button("🌐 Switch Language", on_click=switch_l)

# --- 5. الشريط الجانبي (المساعد الذكي والبيانات) ---
with st.sidebar:
    st.header("🤖 المساعد الذكي (AI)")
    st.info("دردشة مباشرة مع مساعد Gemini الطبي")
    ai_msg = st.text_area("كيف يمكنني مساعدتك؟", placeholder="مثلاً: ما هي أعراض نقص فيتامين د؟")
    if st.button("اسأل المساعد"):
        st.success("💬 جاري التحليل... (هنا يتم الربط مع Gemini API)")
    
    st.divider()
    st.header("👤 ملف المريض")
    st.text_input("الاسم")
    st.number_input("العمر", 1, 100)
    st.divider()
    st.subheader("📊 العلامات الحيوية")
    st.text_input("ضغط الدم (Systolic/Diastolic)")
    st.text_input("مستوى السكر (mg/dL)")
    st.file_uploader("📂 رفع سجلات طبية")

# --- 6. نظام فحص الأعراض (أجهزة الجسم) ---
st.header("📋 فحص الأعراض الشامل")
st.write("يرجى اختيار الجهاز المعني بالأعراض:")

# تبويبات الأجهزة
tab_cv, tab_resp, tab_digest, tab_neuro = st.tabs(["❤️ الجهاز الدوري", "🫁 الجهاز التنفسي", "🤢 الجهاز الهضمي", "🧠 الجهاز العصبي"])

with tab_cv:
    st.subheader("أعراض الجهاز الدوري (Cardiovascular)")
    cv_symp = st.multiselect("اختر كل ما تشعر به:", 
        ["سرعة ضربات القلب", "ألم حاد في الصدر", "نهجان مع المجهود", "دوخة عند الوقوف", "تورم في الكاحلين"])
    st.button("التالي (الجهاز التنفسي) ➡️")

with tab_resp:
    st.subheader("أعراض الجهاز التنفسي (Respiratory)")
    resp_symp = st.multiselect("اختر كل ما تشعر به:", 
        ["سعال جاف", "سعال ببلغم", "ضيق تنفس", "تزييق في الصدر", "آلام عند التنفس العميق"])
    st.button("التالي (الجهاز الهضمي) ➡️")

# زر التشخيص المبدئي
if st.button("🔍 تحليل الأعراض واستخراج التشخيص المبدئي"):
    st.divider()
    st.subheader("🩺 نتيجة التحليل السريري المبدئي")
    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        st.warning("**التشخيصات المحتملة:**")
        st.write("1. اشتباه في قصور بالشرايين التاجية")
        st.write("2. التهاب شعبي حاد")
        st.info("**طرق الوقاية:** الراحة التامة، تجنب المجهود البدني، الالتزام بنظام غذائي قليل الأملاح.")

    with col_res2:
        st.success("**العلاجات المتوقعة (بعد استشارة الطبيب):**")
        st.write("- موسعات للشعب الهوائية")
        st.write("- مسكنات آلام الصدر غير الستيرويدية")
        st.error("**التحاليل المطلوبة فوراً:**")
        st.write("- رسم قلب كهربائي (ECG)")
        st.write("- تحليل أنزيمات قلب")
        st.write("- أشعة سينية على الصدر")

# --- 7. قسم الأدوية المتطور (A-Z) ---
st.divider()
st.header("💊 دليل الأدوية والجرعات الشامل")
st.write("ابحث عن الدواء بالحرف الأول للحصول على التفاصيل الكاملة:")

letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
selected_letter = st.select_slider("اختر الحرف الأول من اسم الدواء:", options=letters)

# محاكاة قاعدة بيانات الأدوية
drugs_db = {
    'A': {"اسم الدواء": "Adol", "المادة": "Paracetamol", "الجرعة": "500mg كل 6 ساعات", "الموانع": "مرضى الفشل الكلوي", "التداخلات": "لا يؤخذ مع الكحول"},
    'S': {"اسم الدواء": "Solupred", "المادة": "Prednisolone", "الجرعة": "20mg مرة صباحاً", "الموانع": "قرحة المعدة النشطة", "التداخلات": "يتفاعل مع أدوية السكر"},
}

if selected_letter in drugs_db:
    drug = drugs_db[selected_letter]
    with st.expander(f"💊 عرض تفاصيل دواء: {drug['اسم الدواء']}"):
        st.write(f"**المادة الفعالة:** {drug['المادة']}")
        st.write(f"**الجرعة المقترحة:** {drug['الجرعة']}")
        st.write(f"**دواعي وموانع الاستعمال:** {drug['الموانع']}")
        st.error(f"**التداخلات الدوائية:** {drug['التداخلات']}")
else:
    st.info(f"جاري تحديث قاعدة بيانات الأدوية لحرف ({selected_letter})...")

# --- 8. قسم التحاليل الطبية ---
st.divider()
st.header("🔬 وحدة التحاليل الطبية")
col_lab1, col_lab2 = st.columns(2)
with col_lab1:
    st.subheader("تحليل النتائج")
    st.text_area("اكتب نتائج تحليلك هنا (مثلاً: Hemoglobin: 12)")
    if st.button("تحليل النتيجة"):
        st.write("النتيجة تظهر ضمن المعدل الطبيعي.")
with col_lab2:
    st.subheader("اقتراح تحاليل")
    if st.button("ما هي التحاليل المناسبة لحالتي؟"):
        st.info("بناءً على الأعراض المدخلة أعلاه، ننصح بعمل (صورة دم كاملة + وظائف كبد).")