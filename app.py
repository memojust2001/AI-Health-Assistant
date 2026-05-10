import streamlit as st
import json
import hashlib
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum
import re

# =============================================================================
# الإعدادات والثوابت - CONFIGURATION & CONSTANTS
# =============================================================================

st.set_page_config(
    page_title="نظام دعم القرار السريري الذكي",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تنسيق CSS لدعم اللغة العربية والاتجاه من اليمين لليسار (RTL)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [data-testid="stSidebar"], .main {
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', sans-serif;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a5f;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #2e86ab;
        margin-bottom: 2rem;
    }
    .emergency-banner {
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-size: 1.3rem;
        font-weight: 600;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    .warning-banner {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: 500;
        margin: 1rem 0;
    }
    .info-card {
        background: #f8fafc;
        border-right: 4px solid #2e86ab;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .result-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    /* تعديل اتجاه صناديق الاختيار والقوائم */
    .stCheckbox, .stMarkdown, .stSelectbox {
        direction: rtl !important;
        text-align: right !important;
    }
    .disclaimer {
        background: #f1f5f9;
        border: 1px dashed #94a3b8;
        padding: 1rem;
        border-radius: 8px;
        font-size: 0.9rem;
        color: #475569;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# نماذج البيانات - DATA MODELS
# =============================================================================

class TriageLevel(Enum):
    EMERGENCY = "حالة طوارئ"      # فوراً
    URGENT = "حالة عاجلة"         # نفس اليوم
    PROMPT = "حالة سريعة"         # 24-48 ساعة
    ROUTINE = "حالة روتينية"      # موعد عادي
    SELF_CARE = "رعاية ذاتية"      # منزلية


@dataclass
class Symptom:
    name: str
    snomed_ct_id: str
    body_system: str
    is_red_flag: bool = False
    severity_weight: float = 1.0

# =============================================================================
# قاعدة المعرفة (مترجمة للعربية)
# =============================================================================

# أعراض الخط الأحمر (الطوارئ)
RED_FLAG_SYMPTOMS = {
    "chest_pain": Symptom("ألم في الصدر", "29857009", "الجهاز الدوري", True, 10.0),
    "difficulty_breathing": Symptom("صعوبة شديدة في التنفس", "267036007", "الجهاز التنفسي", True, 10.0),
    "unconscious": Symptom("فقدان الوعي", "419284004", "الجهاز العصبي", True, 10.0),
    "severe_bleeding": Symptom("نزيف حاد", "131148009", "الدم", True, 10.0),
    "stroke_symptoms": Symptom("أعراض سكتة دماغية (شلل وجه/ضعف ذراع)", "230690007", "الجهاز العصبي", True, 10.0),
    "severe_abdominal_pain": Symptom("ألم حاد في البطن", "21522001", "الجهاز الهضمي", True, 9.0),
    "suicidal_ideation": Symptom("أفكار انتحارية", "6471006", "الصحة النفسية", True, 10.0),
}

# قاعدة الأعراض الشائعة
COMMON_SYMPTOMS = {
    **RED_FLAG_SYMPTOMS,
    "fever": Symptom("حمى (سخونية)", "386661006", "عام", False, 3.0),
    "cough": Symptom("سعال (كحة)", "49727002", "الجهاز التنفسي", False, 2.0),
    "fatigue": Symptom("إرهاق وتعب", "84229001", "عام", False, 1.5),
    "headache": Symptom("صداع", "25064002", "الجهاز العصبي", False, 2.5),
    "nausea": Symptom("غثيان", "422587007", "الجهاز الهضمي", False, 2.0),
    "vomiting": Symptom("قيء", "422400008", "الجهاز الهضمي", False, 2.5),
    "dizziness": Symptom("دوخة", "404640003", "الجهاز العصبي", False, 2.5),
}

# تصنيفات أجهزة الجسم للعرض
BODY_SYSTEMS = {
    "الجهاز الدوري والتنفسي": ["chest_pain", "difficulty_breathing", "cough"],
    "الجهاز العصبي": ["unconscious", "stroke_symptoms", "headache", "dizziness"],
    "الجهاز الهضمي": ["severe_abdominal_pain", "nausea", "vomiting"],
    "أعراض عامة ونفسية": ["fever", "fatigue", "suicidal_ideation"],
}

# =============================================================================
# واجهة المستخدم الرئيسية
# =============================================================================

def main():
    # الهيدر
    st.markdown('<div class="main-header">🏥 نظام الذكاء الاصطناعي لدعم القرار الطبي</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; color: #64748b; margin-bottom: 2rem;">نموذج بحث دكتوراه • الإصدار العربي</div>', unsafe_allow_html=True)

    # التبويبات
    tab1, tab2 = st.tabs(["🔍 فحص الأعراض", "💊 الأدوية والتفاعلات"])

    with tab1:
        st.header("فحص الأعراض")
        
        with st.form("symptom_form"):
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("العمر", 0, 120, 30)
                sex = st.selectbox("الجنس", ["ذكر", "أنثى"])
            with col2:
                duration = st.selectbox("مدة الأعراض", ["دقائق (مفاجئ)", "ساعات", "أيام", "أسابيع"])
                severity = st.slider("شدة الألم (1 هادئ - 10 حاد)", 1, 10, 5)

            st.write("### اختر الأعراض التي تشعر بها:")
            cols = st.columns(2)
            selected_symptoms = []
            
            for i, (system, symptoms) in enumerate(BODY_SYSTEMS.items()):
                with cols[i % 2]:
                    st.markdown(f"**{system}**")
                    for s_key in symptoms:
                        s_data = COMMON_SYMPTOMS[s_key]
                        label = f"🚨 {s_data.name}" if s_data.is_red_flag else s_data.name
                        if st.checkbox(label, key=s_key):
                            selected_symptoms.append(s_key)

            free_text = st.text_area("اشرح حالتك بالتفصيل (اختياري):", placeholder="مثال: أشعر بضيق في التنفس مع تعرق بارد...")
            
            submitted = st.form_submit_button("تحليل الحالة الآن")

        if submitted:
            if not selected_symptoms:
                st.warning("يرجى اختيار عرض واحد على الأقل.")
            else:
                st.subheader("النتيجة المبدئية:")
                # تحليل بسيط كمثال للبحث
                has_red_flag = any(COMMON_SYMPTOMS[s].is_red_flag for s in selected_symptoms)
                
                if has_red_flag:
                    st.markdown("""
                    <div class="emergency-banner">
                        🚨 تنبيه حالة طارئة 🚨<br>
                        يرجى التوجه لأقرب مستشفى أو الاتصال بالإسعاف فوراً.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.success("تم تحليل الأعراض. ننصح بمراجعة الطبيب في أقرب موعد روتيني.")

    with tab2:
        st.header("الاستعلام عن الأدوية")
        st.info("هذا القسم مخصص للتحقق من تداخلات الأدوية (قيد التطوير في البحث).")

    # التذييل والقانون
    st.markdown("""
    <div class="disclaimer">
        <strong>⚠️ إخلاء مسؤولية طبي</strong><br>
        هذا النظام هو <strong>نموذج بحثي لرسالة دكتوراه</strong> فقط. 
        لا يمكن استخدامه كبديل للتشخيص الطبي المهني. في حالات الطوارئ، اتصل دائماً بالإسعاف (123 في مصر).
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()