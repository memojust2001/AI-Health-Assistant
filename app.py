import streamlit as st
import pandas as pd

# --- 1. إعدادات الصفحة الفنية ---
st.set_page_config(page_title="AI Medical Hub | PhD Project", layout="wide", initial_sidebar_state="expanded")

# --- 2. محرك التنسيق المطور (Professional CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f8fafb; }
    .marquee { width: 100%; line-height: 45px; background-color: #1a5276; color: white; white-space: nowrap; overflow: hidden; border-bottom: 3px solid #d4ac0d; }
    .marquee p { display: inline-block; padding-left: 100%; animation: marquee 25s linear infinite; font-size: 17px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .card { background-color: white; padding: 20px; border-radius: 12px; border-right: 8px solid #1a5276; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; direction: rtl; text-align: right; }
    .price-tag { background-color: #fef5e7; color: #d35400; padding: 5px 15px; border-radius: 5px; font-weight: bold; float: left; }
    </style>
    <div class="marquee"><p>🌐 منصة المساعد الطبي الذكي - نسخة الدكتوراه 2026 | موسوعة الأدوية والتحاليل المحدثة طبقاً للدليل الطبي | فحص الأعراض الذكي متاح الآن 🩺</p></div>
    """, unsafe_allow_html=True)

# --- 3. الشريط الجانبي (بيانات المريض كاملة) ---
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
    ai_q = st.text_area("اسألني أي سؤال طبي...")
    if st.button("إرسال للمساعد"):
        st.info("💬 جاري التحليل برمجياً...")

# --- 4. الهيدر وفحص الأعراض ---
st.title("🏥 نظام التحليل الطبي والدوائي المتكامل")
tabs = st.tabs(["❤️ الجهاز الدوري", "🫁 الجهاز التنفسي", "🤢 الجهاز الهضمي", "🧠 الجهاز العصبي"])

with tabs[0]:
    st.subheader("أعراض الجهاز الدوري")
    cv_s = st.multiselect("اختر الأعراض:", ["نهجان", "ألم صدر", "ضربات سريعة", "تورم أطراف"])
    if st.button("تشخيص الحالة 🔍", key="diag_cv"):
        st.warning("التشخيص المبدئي: اشتباه إجهاد قلبي. | التحاليل: ECG | الوقاية: راحة تامة.")

# --- 5. موسوعة الأدوية الشاملة (طبقاً للصورة المرفقة) ---
st.divider()
st.header("💊 محرك بحث الأدوية (Drug Index)")

# قاعدة بيانات تجريبية (موسعة)
med_db = [
    {"name": "Augmentin 1g", "active": "Amoxicillin + Clavulanic Acid", "company": "GSK", "price": "100 EGP", "use": "Antibiotic"},
    {"name": "Panadol Advance", "active": "Paracetamol", "company": "Glaxo", "price": "30 EGP", "use": "Analgesic"},
    {"name": "Concor 5mg", "active": "Bisoprolol", "company": "Merck", "price": "50 EGP", "use": "Hypertension"},
    {"name": "Cataflam 50mg", "active": "Diclofenac Potassium", "company": "Novartis", "price": "65 EGP", "use": "Anti-inflammatory"},
    {"name": "Controloc 40mg", "active": "Pantoprazole", "company": "Takeda", "price": "95 EGP", "use": "Gastritis"}
]
df_meds = pd.DataFrame(med_db)

drug_input = st.text_input("🔍 ابحث عن الدواء (الاسم، المادة، الشركة، أو الاستخدام):")

if drug_input:
    results = df_meds[df_meds.apply(lambda row: drug_input.lower() in row.astype(str).str.lower().values, axis=1)]
    if not results.empty:
        for _, row in results.iterrows():
            st.markdown(f"""
            <div class="card">
                <span class="price-tag">{row['price']}</span>
                <h2 style="color: #1a5276; margin-top: 0;">{row['name']}</h2>
                <p style="margin: 5px 0;"><b>🧪 المادة الفعالة:</b> {row['active']}</p>
                <p style="margin: 5px 0;"><b>🏢 الشركة:</b> {row['company']}</p>
                <p style="margin: 5px 0;"><b>📝 الاستخدام:</b> {row['use']}</p>
                <hr>
                <p style="color: #008080; font-size: 0.9em;"><b>🔄 البدائل المتاحة:</b> تظهر هنا الأدوية التي تحتوي على {row['active']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("لم يتم العثور على نتائج.")

# --- 6. قسم التحاليل الطبية (بدون أسعار - علمي) ---
st.divider()
st.header("🔬 المختبر الطبي الذكي")
lab_input = st.text_input("🔍 ابحث عن التحليل والتعليمات:")

labs = [
    {"n": "صورة دم (CBC)", "f": "خلايا الدم والأنيميا", "t": "لا يشترط الصيام"},
    {"n": "سكر تراكمي (HbA1c)", "f": "معدل السكر في 3 شهور", "t": "لا يشترط الصيام"},
    {"n": "وظائف كبد (ALT/AST)", "f": "سلامة إنزيمات الكبد", "t": "يفضل الصيام 6 ساعات"}
]

if lab_input:
    res_l = [l for l in labs if lab_input.lower() in l['n'].lower()]
    for l in res_l:
        st.markdown(f"""
        <div class="card" style="border-right-color: #008080;">
            <h3 style="color: #004d40;">{l['n']}</h3>
            <p><b>🎯 الهدف:</b> {l['f']}</p>
            <div style="background-color:
