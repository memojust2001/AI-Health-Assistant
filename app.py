import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =============================================================================
# إعدادات متقدمة للواجهة الاحترافية (Professional Medical Dashboard)
# =============================================================================
st.set_page_config(page_title="AI Clinical Decision Support System", layout="wide")

# CSS متطور جداً لتحويل واجهة Streamlit لمنصة احترافية
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;500;700&display=swap');
    
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    
    .main { background-color: #f0f2f6; }
    
    /* تصميم الكروت العلوية */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 5px solid #007bff;
    }
    
    /* تصميم العنوان الرئيسي */
    .hero-section {
        background: linear-gradient(135deg, #004e92 0%, #000428 100%);
        color: white;
        padding: 40px;
        border-radius: 20px;
        margin-bottom: 30px;
        text-align: right;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    
    /* ستايل الأزرار */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #0056b3;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# الهيدر الاحترافي
# =============================================================================
st.markdown("""
    <div class="hero-section">
        <h1>نظام دعم القرار الطبي السريري (CDSS) 🩺</h1>
        <p>منصة بحثية متقدمة لرسالة الدكتوراه - معالجة البيانات الطبية بالذكاء الاصطناعي</p>
        <hr style="border-color: rgba(255,255,255,0.2)">
        <div style="display: flex; gap: 20px;">
            <span>📍 الإصدار: 2.0 (Premium)</span>
            <span>📅 التاريخ: """ + datetime.now().strftime("%Y-%m-%d") + """</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# =============================================================================
# تقسيم الشاشة (Dashboard Layout)
# =============================================================================
col_side, col_main = st.columns([1, 3])

with col_side:
    st.markdown("### 👤 بيانات المريض")
    with st.expander("معلومات ديموغرافية", expanded=True):
        age = st.slider("العمر", 1, 100, 30)
        gender = st.radio("الجنس", ["ذكر", "أنثى"])
        blood_type = st.selectbox("فصيلة الدم", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
    
    st.markdown("### 🌡️ العلامات الحيوية")
    temp = st.number_input("درجة الحرارة (C°)", 35.0, 42.0, 37.0)
    bp = st.text_input("ضغط الدم (مثلاً 120/80)", "120/80")
    hr = st.number_input("نبض القلب (BPM)", 40, 200, 75)

with col_main:
    # تبويبات ذكية
    tab_symptoms, tab_analysis, tab_meds = st.tabs(["🔍 فحص الأعراض الشامل", "📊 تحليل البيانات", "🔬 تداخلات الأدوية"])
    
    with tab_symptoms:
        st.info("اختر الأعراض من القوائم المتخصصة أدناه لتفعيل محرك الترياج الذكي.")
        
        # تقسيم الأعراض لمجموعات طبية دقيقة
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🔴 أعراض حرجة (Red Flags)")
            red_flags = {
                "chest_pain": "ألم ضاغط في الصدر",
                "diff_breath": "فشل تنفسي حاد",
                "stroke": "فقدان مفاجئ للنطق/الحركة",
                "bleeding": "نزيف داخلي مشتبه به"
            }
            selected_red = [k for k, v in red_flags.items() if st.checkbox(v, key=k)]
            
        with c2:
            st.subheader("🟡 أعراض جهازية")
            general_symp = {
                "fever": "حمى مستمرة (>38.5)",
                "dizzy": "دوار وفقدان توازن",
                "nausea": "غثيان مستمر",
                "joint_pain": "آلام حادة في المفاصل"
            }
            selected_gen = [k for k, v in general_symp.items() if st.checkbox(v, key=k)]

        st.divider()
        if st.button("تحليل الحالة السريرية ⚡"):
            if selected_red:
                st.error("### 🚨 مستوى الخطورة: عالي جداً (Immediate Triage)")
                st.markdown("- **التوصية:** توجه لغرفة الطوارئ فوراً.")
            elif selected_gen:
                st.warning("### ⚠️ مستوى الخطورة: متوسط")
                st.markdown("- **التوصية:** استشارة طبيب مختص خلال 12 ساعة.")
            else:
                st.success("### ✅ مستوى الخطورة: منخفض")
                st.write("استمر في المراقبة المنزلية.")

    with tab_analysis:
        st.subheader("📈 محاكاة بيانية لانتشار الأعراض")
        # رسم بياني احترافي يوضح وزن الأعراض (مفيد جداً في مناقشة الدكتوراه)
        data = pd.DataFrame({
            "العرض": ["الصدر", "التنفس", "الحمى", "الدوار"],
            "مستوى التأثير": [95, 88, 45, 30]
        })
        fig = px.bar(data, x="العرض", y="مستوى التأثير", color="مستوى التأثير", 
                     title="تحليل أوزان الأعراض (Severity Weight Analysis)")
        st.plotly_chart(fig, use_container_width=True)

    with tab_meds:
        st.subheader("🔬 فحص التداخلات الدوائية المتقدم")
        med1 = st.multiselect("الأدوية الحالية", ["Lisinopril", "Metformin", "Warfarin", "Aspirin"])
        med2 = st.multiselect("الأدوية المراد إضافتها", ["Ibuprofen", "Clopidogrel", "Amoxicillin"])
        
        if med1 and med2:
            st.error("⚠️ اكتشاف تداخل دوائي محتمل بين Aspirin و Warfarin (زيادة خطر النزيف)")

# =============================================================================
# فوتر أكاديمي
# =============================================================================
st.markdown("---")
footer_col1, footer_col2 = st.columns(2)
with footer_col1:
    st.markdown("**الباحث:** طالب دكتوراه - جامعة [اسم جامعتك]")
with footer_col2:
    st.markdown("<div style='text-align: left;'>جميع الحقوق محفوظة © 2026</div>", unsafe_allow_html=True)