import streamlit as st
import hashlib
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum

# =============================================================================
# إعدادات الصفحة والستايل الاحترافي (RTL)
# =============================================================================

st.set_page_config(
    page_title="نظام دعم القرار الطبي الذكي",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تصميم واجهة المستخدم (CSS)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* جعل الموقع بالكامل يدعم العربية */
    html, body, [data-testid="stSidebar"], .main {
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', sans-serif;
    }
    
    /* الهيدر الرئيسي */
    .main-header {
        background: linear-gradient(90deg, #1e3a5f 0%, #2e86ab 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* كروت النتائج */
    .result-card {
        background: #ffffff;
        border-right: 5px solid #2e86ab;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin: 1rem 0;
    }
    
    /* تنبيهات الطوارئ */
    .emergency-banner {
        background-color: #ff4b4b;
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.8; }
        100% { opacity: 1; }
    }
    
    /* تنسيق القوائم الجانبية */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-left: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# المنطق البرمجي وقاعدة البيانات (مترجمة ومحدثة)
# =============================================================================

class TriageLevel(Enum):
    EMERGENCY = "🚨 طوارئ فورية"
    URGENT = "⚠️ عاجل (خلال ساعات)"
    PROMPT = "📋 موعد قريب (24-48 ساعة)"
    ROUTINE = "🏥 مراجعة روتينية"
    SELF_CARE = "🏠 رعاية منزلية"

@dataclass
class Symptom:
    name: str
    is_red_flag: bool = False
    weight: float = 1.0

# قاعدة بيانات الأعراض (لحل مشكلة التكرار)
SYMPTOMS_DB = {
    "أعراض الجهاز الدوري": {
        "chest_pain": Symptom("ألم في الصدر", True, 10.0),
        "palpitations": Symptom("خفقان سريع للقلب", False, 4.0),
    },
    "أعراض الجهاز التنفسي": {
        "diff_breathing": Symptom("صعوبة شديدة في التنفس", True, 10.0),
        "short_breath": Symptom("ضيق تنفس بسيط", False, 5.0),
        "cough": Symptom("سعال مستمر", False, 2.0),
    },
    "أعراض الجهاز العصبي": {
        "unconscious": Symptom("فقدان أو اضطراب الوعي", True, 10.0),
        "stroke_symp": Symptom("ثقل في الكلام أو ضعف في الأطراف", True, 10.0),
        "headache": Symptom("صداع حاد ومفاجئ", False, 3.0),
    },
    "أعراض عامة": {
        "fever": Symptom("حمى (ارتفاع حرارة)", False, 3.0),
        "fatigue": Symptom("إرهاق شديد", False, 1.5),
        "bleeding": Symptom("نزيف حاد غير متحكم به", True, 10.0),
    }
}

# =============================================================================
# واجهة التطبيق
# =============================================================================

def main():
    # 1. الهيدر الرئيسي (أول ما يراه المستخدم)
    st.markdown("""
        <div class="main-header">
            <h1>🏥 نظام المساعد الطبي الذكي</h1>
            <p>مشروع دكتوراه: تحليل الأعراض ودعم القرار الطبي باستخدام الذكاء الاصطناعي</p>
        </div>
    """, unsafe_allow_html=True)

    # 2. القائمة الجانبية
    with st.sidebar:
        st.header("📊 إحصائيات الجلسة")
        st.info(f"معرف الجلسة: {hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}")
        st.write("---")
        st.subheader("☎️ أرقام الطوارئ (مصر)")
        st.error("الإسعاف: 123")
        st.warning("النجدة: 122")

    # 3. التبويبات الرئيسية
    tab1, tab2, tab3 = st.tabs(["🔍 فحص الأعراض", "💊 الاستعلام الدوائي", "📜 عن الدراسة"])

    with tab1:
        st.subheader("خطوة 1: إدخال البيانات الأساسية")
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.number_input("العمر", 1, 120, 30)
        with c2:
            sex = st.selectbox("الجنس", ["ذكر", "أنثى"])
        with c3:
            duration = st.selectbox("مدة الأعراض", ["دقائق/ساعات", "أيام", "أسبوع فأكثر"])

        st.write("---")
        st.subheader("خطوة 2: تحديد الأعراض")
        
        selected_keys = []
        cols = st.columns(2)
        for i, (category, symptoms) in enumerate(SYMPTOMS_DB.items()):
            with cols[i % 2]:
                st.markdown(f"**{category}**")
                for key, data in symptoms.items():
                    if st.checkbox(data.name, key=key):
                        selected_keys.append(key)

        st.write("---")
        st.subheader("خطوة 3: وصف إضافي")
        free_text = st.text_area("اشرح حالتك بكلماتك الخاصة:", placeholder="مثال: أشعر بثقل في الكتف الأيسر منذ ساعتين...")

        # زر التحليل (حل مشكلة Missing Submit Button)
        if st.button("🔬 بدء التحليل السريري", use_container_width=True, type="primary"):
            if not selected_keys and not free_text:
                st.warning("يرجى اختيار عرض واحد على الأقل أو كتابة وصف للحالة.")
            else:
                st.write("### 📋 نتيجة التقييم")
                
                # منطق الترياج البسيط
                has_red_flag = any(any(s.is_red_flag for k, s in cat.items() if k in selected_keys) 
                                   for cat in SYMPTOMS_DB.values())
                
                if has_red_flag:
                    st.markdown("""
                        <div class="emergency-banner">
                            🚨 تنبيه: حالة طارئة خطيرة!<br>
                            الأعراض المختارة تشير لضرورة التدخل الطبي الفوري. اتصل بالاسعاف الآن.
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("بناءً على الأعراض المدخلة، ننصح بحجز موعد مع طبيب مختص في أقرب وقت.")

    with tab2:
        st.header("💊 قاعدة بيانات الأدوية")
        st.write("هذا القسم مخصص للتحقق من التداخلات الدوائية (تحت التحديث برمجياً).")

    with tab3:
        st.markdown(f"""
            ### عن مشروع الدكتوراه
            هذا النظام يهدف إلى تقليل الضغط على غرف الطوارئ من خلال تصنيف الحالات طبياً (Triage) بدقة.
            * **الباحث:** دكتوراه في العلوم الطبية / المعلوماتية الصحية.
            * **الإصدار:** 1.5 (عربي بالكامل).
        """)

    # 4. إخلاء المسؤولية الثابت
    st.markdown("---")
    st.markdown("""
        <div style="background-color: #fff3cd; padding: 10px; border-radius: 5px; font-size: 0.8rem; color: #856404; text-align: center;">
            ⚠️ <strong>تنبيه طبي:</strong> هذا نموذج بحثي وليس تشخيصاً نهائياً. دائماً استشر الطبيب في الحالات الصحية.
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()