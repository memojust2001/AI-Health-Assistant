import streamlit as st
import json
import hashlib
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum
import re

# =============================================================================
# CONFIGURATION & CONSTANTS
# =============================================================================

st.set_page_config(
    page_title="Clinical Decision Support System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clinical styling
st.markdown("""
<style>
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
        border-left: 4px solid #2e86ab;
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
    .severity-high { color: #dc2626; font-weight: 700; }
    .severity-moderate { color: #f59e0b; font-weight: 700; }
    .severity-low { color: #16a34a; font-weight: 700; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.1rem;
        font-weight: 600;
        padding: 1rem 2rem;
    }
    .drug-interaction-major {
        background: #fef2f2;
        border-left: 4px solid #dc2626;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    .drug-interaction-moderate {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    .drug-interaction-minor {
        background: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
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
# DATA MODELS & ENUMS
# =============================================================================

class TriageLevel(Enum):
    EMERGENCY = 5      # Immediate 911/ER
    URGENT = 4         # Same-day medical care
    PROMPT = 3         # Within 24-48 hours
    ROUTINE = 2        # Primary care appointment
    SELF_CARE = 1      # Home management acceptable


class InteractionSeverity(Enum):
    MAJOR = "major"
    MODERATE = "moderate"
    MINOR = "minor"


@dataclass
class Symptom:
    name: str
    snomed_ct_id: str
    body_system: str
    is_red_flag: bool = False
    severity_weight: float = 1.0


@dataclass
class Medication:
    name: str
    rxcui: str
    drugbank_id: str
    common_dosage: str
    category: str


@dataclass
class DrugInteraction:
    drug1: str
    drug2: str
    severity: InteractionSeverity
    mechanism: str
    clinical_effect: str
    management: str
    evidence_level: str


@dataclass
class TriageResult:
    level: TriageLevel
    triggered_symptoms: List[str]
    recommendation: str
    action_required: str
    confidence: float


# =============================================================================
# KNOWLEDGE BASE (Simulated - In production, connect to SNOMED CT/DrugBank)
# =============================================================================

# Red flag symptoms requiring immediate emergency attention
RED_FLAG_SYMPTOMS = {
    "chest_pain": Symptom("Chest Pain", "29857009", "Cardiovascular", True, 10.0),
    "severe_chest_pain": Symptom("Severe Chest Pain", "29857009", "Cardiovascular", True, 10.0),
    "difficulty_breathing": Symptom("Difficulty Breathing", "267036007", "Respiratory", True, 10.0),
    "shortness_of_breath": Symptom("Shortness of Breath", "267036007", "Respiratory", True, 9.5),
    "altered_consciousness": Symptom("Altered Consciousness", "419284004", "Neurological", True, 10.0),
    "unconscious": Symptom("Loss of Consciousness", "419284004", "Neurological", True, 10.0),
    "severe_bleeding": Symptom("Severe Bleeding", "131148009", "Hematological", True, 10.0),
    "stroke_symptoms": Symptom("Stroke Symptoms (FAST)", "230690007", "Neurological", True, 10.0),
    "severe_abdominal_pain": Symptom("Severe Abdominal Pain", "21522001", "Gastrointestinal", True, 9.0),
    "suicidal_ideation": Symptom("Suicidal Thoughts", "6471006", "Psychiatric", True, 10.0),
    "anaphylaxis": Symptom("Anaphylaxis/Allergic Reaction", "39579001", "Immunological", True, 10.0),
    "seizure": Symptom("Seizure", "91175000", "Neurological", True, 9.5),
    "severe_headache": Symptom("Thunderclap Headache", "25064002", "Neurological", True, 9.0),
    "vision_loss": Symptom("Sudden Vision Loss", "7973008", "Ophthalmological", True, 9.0),
}

# Common symptoms database
COMMON_SYMPTOMS = {
    **RED_FLAG_SYMPTOMS,
    "fever": Symptom("Fever", "386661006", "General", False, 3.0),
    "cough": Symptom("Cough", "49727002", "Respiratory", False, 2.0),
    "fatigue": Symptom("Fatigue", "84229001", "General", False, 1.5),
    "headache": Symptom("Headache", "25064002", "Neurological", False, 2.5),
    "nausea": Symptom("Nausea", "422587007", "Gastrointestinal", False, 2.0),
    "vomiting": Symptom("Vomiting", "422400008", "Gastrointestinal", False, 2.5),
    "diarrhea": Symptom("Diarrhea", "62315008", "Gastrointestinal", False, 2.0),
    "sore_throat": Symptom("Sore Throat", "162397003", "ENT", False, 1.5),
    "runny_nose": Symptom("Runny Nose", "64531003", "ENT", False, 1.0),
    "body_aches": Symptom("Body Aches", "68962001", "Musculoskeletal", False, 1.5),
    "dizziness": Symptom("Dizziness", "404640003", "Neurological", False, 2.5),
    "rash": Symptom("Skin Rash", "271807003", "Dermatological", False, 1.5),
    "joint_pain": Symptom("Joint Pain", "57676002", "Musculoskeletal", False, 2.0),
    "back_pain": Symptom("Back Pain", "161891005", "Musculoskeletal", False, 2.0),
    "abdominal_pain": Symptom("Abdominal Pain", "21522001", "Gastrointestinal", False, 2.5),
    "urinary_pain": Symptom("Painful Urination", "49650001", "Urological", False, 2.5),
    "anxiety": Symptom("Anxiety", "48694002", "Psychiatric", False, 2.0),
    "depression": Symptom("Depression", "35489007", "Psychiatric", False, 2.5),
    "insomnia": Symptom("Insomnia", "193462001", "Psychiatric", False, 1.5),
}

# Medication database (simplified)
MEDICATION_DB = {
    "aspirin": Medication("Aspirin", "1191", "DB00945", "81-325mg daily", "NSAID"),
    "ibuprofen": Medication("Ibuprofen", "5640", "DB01050", "200-800mg q6-8h", "NSAID"),
    "acetaminophen": Medication("Acetaminophen/Paracetamol", "161", "DB00316", "500-1000mg q6h", "Analgesic"),
    "warfarin": Medication("Warfarin", "11289", "DB00682", "2-10mg daily", "Anticoagulant"),
    "metformin": Medication("Metformin", "6809", "DB00331", "500-2000mg daily", "Antidiabetic"),
    "lisinopril": Medication("Lisinopril", "29046", "DB00722", "5-40mg daily", "ACE Inhibitor"),
    "atorvastatin": Medication("Atorvastatin", "83367", "DB01076", "10-80mg daily", "Statin"),
    "amlodipine": Medication("Amlodipine", "17767", "DB00381", "2.5-10mg daily", "Calcium Channel Blocker"),
    "omeprazole": Medication("Omeprazole", "7646", "DB00338", "20-40mg daily", "PPI"),
    "sertraline": Medication("Sertraline", "36437", "DB01104", "25-200mg daily", "SSRI"),
    "albuterol": Medication("Albuterol/Salbutamol", "435", "DB01001", "90mcg inhaler", "Bronchodilator"),
    "insulin_glargine": Medication("Insulin Glargine", "274783", "DB00047", "Units varies", "Insulin"),
    "prednisone": Medication("Prednisone", "8638", "DB00635", "5-60mg daily", "Corticosteroid"),
    "amoxicillin": Medication("Amoxicillin", "723", "DB01060", "250-875mg q8-12h", "Antibiotic"),
    "clopidogrel": Medication("Clopidogrel", "32968", "DB00758", "75mg daily", "Antiplatelet"),
}

# Drug interaction knowledge base
DRUG_INTERACTIONS = [
    DrugInteraction(
        "warfarin", "aspirin",
        InteractionSeverity.MAJOR,
        "Additive anticoagulant effect via inhibition of platelet aggregation and interference with vitamin K-dependent clotting factors",
        "Significantly increased risk of gastrointestinal and intracranial bleeding",
        "Avoid combination unless specifically indicated; if unavoidable, monitor INR closely and consider gastroprotection",
        "A"
    ),
    DrugInteraction(
        "warfarin", "ibuprofen",
        InteractionSeverity.MAJOR,
        "NSAIDs inhibit platelet function and may cause gastric ulceration; displacement from protein binding sites",
        "Increased bleeding risk; potential for GI hemorrhage",
        "Avoid NSAIDs in patients on warfarin; use acetaminophen for pain when possible",
        "A"
    ),
    DrugInteraction(
        "lisinopril", "amlodipine",
        InteractionSeverity.MINOR,
        "Additive antihypertensive effect via complementary mechanisms (ACE inhibition + calcium channel blockade)",
        "Enhanced blood pressure reduction; possible hypotension",
        "Monitor BP; combination often therapeutic and beneficial for cardiovascular outcomes",
        "B"
    ),
    DrugInteraction(
        "metformin", "omeprazole",
        InteractionSeverity.MINOR,
        "PPIs may alter gut microbiome and potentially affect vitamin B12 absorption",
        "Long-term: possible decreased B12 levels; minimal acute clinical significance",
        "Monitor B12 levels annually if long-term combination therapy",
        "C"
    ),
    DrugInteraction(
        "sertraline", "ibuprofen",
        InteractionSeverity.MODERATE,
        "SSRIs impair platelet serotonin uptake, reducing platelet aggregation; additive effect with NSAIDs",
        "Increased risk of upper GI bleeding",
        "Use lowest effective NSAID dose; consider PPI prophylaxis; monitor for bleeding signs",
        "B"
    ),
    DrugInteraction(
        "aspirin", "clopidogrel",
        InteractionSeverity.MAJOR,
        "Dual antiplatelet therapy (DAPT) - additive inhibition of platelet aggregation pathways",
        "Significantly increased bleeding risk; used therapeutically post-PCI",
        "Only combine when clinically indicated (e.g., post-stent); limit duration per guidelines",
        "A"
    ),
    DrugInteraction(
        "prednisone", "ibuprofen",
        InteractionSeverity.MODERATE,
        "Corticosteroids increase gastric ulcer risk; NSAIDs further impair gastric mucosal defense",
        "High risk of GI ulceration and bleeding",
        "Avoid combination if possible; if necessary, add PPI and monitor closely",
        "A"
    ),
    DrugInteraction(
        "insulin_glargine", "metformin",
        InteractionSeverity.MINOR,
        "Complementary mechanisms for glucose lowering; no direct pharmacokinetic interaction",
        "Additive hypoglycemic effect; improved glycemic control",
        "Monitor blood glucose; dose adjustments may be needed to prevent hypoglycemia",
        "B"
    ),
    DrugInteraction(
        "albuterol", "sertraline",
        InteractionSeverity.MINOR,
        "Beta-agonists may cause transient hypokalemia; SSRIs may have minimal QT effects",
        "Theoretical increased arrhythmia risk in susceptible patients",
        "Generally safe; monitor in patients with known cardiac disease or electrolyte abnormalities",
        "C"
    ),
    DrugInteraction(
        "atorvastatin", "omeprazole",
        InteractionSeverity.MINOR,
        "Omeprazole may inhibit CYP2C19-mediated metabolism of certain statins",
        "Minimal effect on atorvastatin (primarily CYP3A4); no clinically significant interaction expected",
        "No dose adjustment typically needed; monitor lipid panel",
        "C"
    ),
]

# Body systems for categorization
BODY_SYSTEMS = {
    "Cardiovascular": ["chest_pain", "severe_chest_pain", "shortness of breath"],
    "Respiratory": ["difficulty_breathing", "shortness_of_breath", "cough"],
    "Neurological": ["altered_consciousness", "unconscious", "stroke_symptoms", "severe_headache", "dizziness", "headache"],
    "Gastrointestinal": ["severe_abdominal_pain", "abdominal_pain", "nausea", "vomiting", "diarrhea"],
    "ENT": ["sore_throat", "runny_nose"],
    "Musculoskeletal": ["body_aches", "joint_pain", "back_pain"],
    "Dermatological": ["rash"],
    "Urological": ["urinary_pain"],
    "Psychiatric": ["suicidal_ideation", "anxiety", "depression", "insomnia"],
    "General": ["fever", "fatigue"],
    "Hematological": ["severe_bleeding"],
    "Immunological": ["anaphylaxis"],
    "Ophthalmological": ["vision_loss"],
}


# =============================================================================
# CORE LOGIC CLASSES
# =============================================================================

class TriageEngine:
    """
    Clinical Triage Engine implementing multi-layer safety assessment.
    Combines rule-based red flag detection with severity scoring.
    """
    
    def __init__(self):
        self.red_flags = RED_FLAG_SYMPTOMS
        self.emergency_keywords = [
            "can't breathe", "cannot breathe", "choking", "not breathing",
            "heart attack", "cardiac arrest", "unresponsive", "not responding",
            "seizing", "convulsing", "passed out", "fainted", "unconscious",
            "severe bleeding", "gushing blood", "bleeding out",
            "suicide", "kill myself", "end my life", "want to die"
        ]
    
    def analyze(self, selected_symptoms: List[str], free_text: str, 
                duration: str, severity: int, age: int) -> TriageResult:
        """
        Main triage analysis pipeline.
        """
        triggered_red_flags = []
        total_risk_score = 0.0
        
        # Layer 1: Structured red flag detection
        for symptom_key in selected_symptoms:
            if symptom_key in self.red_flags:
                triggered_red_flags.append(self.red_flags[symptom_key].name)
                total_risk_score += self.red_flags[symptom_key].severity_weight
        
        # Layer 2: Free-text emergency keyword detection
        text_lower = free_text.lower()
        for keyword in self.emergency_keywords:
            if keyword in text_lower:
                # Extract context around keyword
                idx = text_lower.find(keyword)
                context = free_text[max(0, idx-30):min(len(free_text), idx+len(keyword)+30)]
                triggered_red_flags.append(f"Emergency phrase detected: '...{context}...'")
                total_risk_score += 10.0
        
        # Layer 3: Age and severity modifiers
        if age > 65:
            total_risk_score *= 1.2  # Elderly multiplier
        if age < 5:
            total_risk_score *= 1.3  # Pediatric multiplier
        
        severity_multiplier = severity / 5.0  # Normalize 1-10 to 0.2-2.0
        total_risk_score *= severity_multiplier
        
        # Duration modifier
        duration_risk = {
            "Sudden (minutes)": 1.5,
            "Hours": 1.2,
            "Days": 1.0,
            "Weeks": 0.8,
            "Months": 0.6
        }
        total_risk_score *= duration_risk.get(duration, 1.0)
        
        # Determine triage level
        if total_risk_score >= 15.0 or len(triggered_red_flags) > 0:
            level = TriageLevel.EMERGENCY
            recommendation = "🚨 EMERGENCY: Call emergency services (911/112) immediately"
            action = "Do not drive yourself. If alone, unlock your door and stay on the line with dispatch."
            confidence = min(0.99, 0.85 + (len(triggered_red_flags) * 0.05))
        elif total_risk_score >= 10.0:
            level = TriageLevel.URGENT
            recommendation = "⚠️ URGENT: Seek same-day medical care at urgent care or ER"
            action = "Contact your healthcare provider immediately or proceed to nearest urgent care facility."
            confidence = 0.80
        elif total_risk_score >= 6.0:
            level = TriageLevel.PROMPT
            recommendation = "📋 PROMPT: Schedule medical appointment within 24-48 hours"
            action = "Contact your primary care provider for an appointment within the next 1-2 days."
            confidence = 0.75
        elif total_risk_score >= 3.0:
            level = TriageLevel.ROUTINE
            recommendation = "🏥 ROUTINE: Schedule a routine primary care visit"
            action = "Make an appointment with your primary care provider at your earliest convenience."
            confidence = 0.70
        else:
            level = TriageLevel.SELF_CARE
            recommendation = "🏠 SELF-CARE: Monitor symptoms at home"
            action = "Rest, hydrate, and monitor symptoms. Seek care if symptoms worsen or persist beyond 3-5 days."
            confidence = 0.65
        
        return TriageResult(
            level=level,
            triggered_symptoms=triggered_red_flags,
            recommendation=recommendation,
            action_required=action,
            confidence=confidence
        )


class PharmacovigilanceEngine:
    """
    Drug interaction analysis engine.
    In production, connects to DrugBank/RxNorm APIs.
    """
    
    def __init__(self):
        self.medications = MEDICATION_DB
        self.interactions = DRUG_INTERACTIONS
    
    def get_medication_list(self) -> List[str]:
        return sorted(list(self.medications.keys()))
    
    def check_interactions(self, selected_meds: List[str]) -> Dict:
        """
        Check for drug-drug interactions among selected medications.
        """
        results = {
            "interactions": [],
            "contraindications": [],
            "summary": {}
        }
        
        # Pairwise interaction check
        for i, med1_key in enumerate(selected_meds):
            for med2_key in selected_meds[i+1:]:
                med1_name = self.medications[med1_key].name.lower()
                med2_name = self.medications[med2_key].name.lower()
                
                for interaction in self.interactions:
                    # Check both orderings
                    if ((interaction.drug1.lower() in med1_name and 
                         interaction.drug2.lower() in med2_name) or
                        (interaction.drug1.lower() in med2_name and 
                         interaction.drug2.lower() in med1_name)):
                        results["interactions"].append(interaction)
        
        # Categorize by severity
        major = [i for i in results["interactions"] if i.severity == InteractionSeverity.MAJOR]
        moderate = [i for i in results["interactions"] if i.severity == InteractionSeverity.MODERATE]
        minor = [i for i in results["interactions"] if i.severity == InteractionSeverity.MINOR]
        
        results["summary"] = {
            "total": len(results["interactions"]),
            "major": len(major),
            "moderate": len(moderate),
            "minor": len(minor),
            "risk_level": "HIGH" if major else ("MODERATE" if moderate else ("LOW" if minor else "NONE"))
        }
        
        return results
    
    def get_medication_info(self, med_key: str) -> Optional[Medication]:
        return self.medications.get(med_key)


class SymptomAnalyzer:
    """
    Symptom analysis and differential generation (simplified).
    In production, integrates with SNOMED CT and clinical knowledge graphs.
    """
    
    def __init__(self):
        self.symptoms = COMMON_SYMPTOMS
        self.body_systems = BODY_SYSTEMS
    
    def get_symptoms_by_system(self) -> Dict[str, List[Tuple[str, str]]]:
        """Return symptoms organized by body system."""
        organized = {}
        for system, symptom_keys in self.body_systems.items():
            organized[system] = [(k, self.symptoms[k].name) for k in symptom_keys if k in self.symptoms]
        # Add any remaining symptoms not in body systems
        other_symptoms = [(k, v.name) for k, v in self.symptoms.items() 
                         if not any(k in syms for syms in self.body_systems.values())]
        if other_symptoms:
            organized["Other"] = other_symptoms
        return organized
    
    def generate_differential(self, selected_symptoms: List[str], 
                             free_text: str, age: int, sex: str) -> List[Dict]:
        """
        Generate a simplified differential diagnosis based on symptom patterns.
        This is a simulation - production would use ML models + knowledge graphs.
        """
        differentials = []
        
        # Simple pattern matching for demonstration
        symptom_set = set(selected_symptoms)
        
        # COVID-19 pattern
        if {"fever", "cough", "fatigue"}.intersection(symptom_set) and len(symptom_set) >= 2:
            differentials.append({
                "condition": "Viral Respiratory Infection (e.g., COVID-19, Influenza)",
                "probability": "High" if len({"fever", "cough", "fatigue", "body_aches"}.intersection(symptom_set)) >= 3 else "Moderate",
                "key_features": ["Fever", "Respiratory symptoms", "Systemic symptoms"],
                "recommended_tests": ["Rapid antigen test", "PCR if available"],
                "confidence": 0.75
            })
        
        # Migraine pattern
        if "headache" in symptom_set and any(s in symptom_set for s in ["nausea", "vomiting", "vision_loss"]):
            differentials.append({
                "condition": "Migraine or Primary Headache Disorder",
                "probability": "High",
                "key_features": ["Headache", "Nausea/photophobia", "Possible aura"],
                "recommended_tests": ["Clinical diagnosis", "Neuroimaging if red flags"],
                "confidence": 0.70
            })
        
        # GI infection
        if {"nausea", "vomiting", "diarrhea"}.intersection(symptom_set):
            differentials.append({
                "condition": "Gastroenteritis",
                "probability": "Moderate",
                "key_features": ["GI symptoms", "Possible infectious etiology"],
                "recommended_tests": ["Stool culture if severe", "Electrolytes"],
                "confidence": 0.65
            })
        
        # Anxiety/depression
        if {"anxiety", "insomnia"}.intersection(symptom_set):
            differentials.append({
                "condition": "Anxiety Disorder / Adjustment Disorder",
                "probability": "Moderate",
                "key_features": ["Psychological symptoms", "Sleep disturbance"],
                "recommended_tests": ["PHQ-9", "GAD-7 screening", "Thyroid panel"],
                "confidence": 0.60
            })
        
        # Hypertension/Cardiovascular (if chest pain or related)
        if any(s in symptom_set for s in ["chest_pain", "shortness_of_breath", "dizziness"]):
            differentials.append({
                "condition": "Cardiovascular Evaluation Needed",
                "probability": "High" if "chest_pain" in symptom_set else "Moderate",
                "key_features": ["Cardiopulmonary symptoms", "Requires ECG/workup"],
                "recommended_tests": ["ECG", "Troponins", "Chest X-ray"],
                "confidence": 0.80 if "chest_pain" in symptom_set else 0.55
            })
        
        # Default: Non-specific viral illness
        if not differentials:
            differentials.append({
                "condition": "Non-specific Viral Illness",
                "probability": "Moderate",
                "key_features": ["Mild systemic symptoms", "Self-limited course"],
                "recommended_tests": ["Supportive care", "Reassessment if worsening"],
                "confidence": 0.50
            })
        
        # Sort by confidence
        differentials.sort(key=lambda x: x["confidence"], reverse=True)
        return differentials


# =============================================================================
# SESSION STATE MANAGEMENT
# =============================================================================

def init_session_state():
    """Initialize session state variables."""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = hashlib.sha256(
            f"{datetime.now().isoformat()}{hash(datetime.now())}".encode()
        ).hexdigest()[:16]
    
    if 'triage_history' not in st.session_state:
        st.session_state.triage_history = []
    
    if 'medication_history' not in st.session_state:
        st.session_state.medication_history = []


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_header():
    """Render the application header."""
    st.markdown('<div class="main-header">🏥 AI Clinical Decision Support System</div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; color: #64748b; margin-bottom: 2rem;">
        <em>PhD Research Prototype • Not for clinical use without physician oversight</em>
    </div>
    """, unsafe_allow_html=True)


def render_emergency_banner(result: TriageResult):
    """Render emergency or warning banners based on triage level."""
    if result.level == TriageLevel.EMERGENCY:
        st.markdown(f"""
        <div class="emergency-banner">
            🚨 CRITICAL EMERGENCY DETECTED 🚨<br>
            {result.recommendation}<br>
            <small>{result.action_required}</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Emergency action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            st.link_button("📞 Call 911 (US)", "tel:911", use_container_width=True)
        with col2:
            st.link_button("🚑 Find Nearest ER", "https://www.google.com/search?q=emergency+room+near+me", 
                          use_container_width=True)
        with col3:
            st.link_button("❤️ CPR Instructions", "https://cpr.heart.org/en/cpr-courses-and-kits", 
                          use_container_width=True)
        
    elif result.level == TriageLevel.URGENT:
        st.markdown(f"""
        <div class="warning-banner">
            ⚠️ URGENT MEDICAL ATTENTION REQUIRED<br>
            {result.recommendation}<br>
            <small>{result.action_required}</small>
        </div>
        """, unsafe_allow_html=True)


def render_triage_result(result: TriageResult):
    """Render the complete triage result card."""
    level_colors = {
        TriageLevel.EMERGENCY: "🔴",
        TriageLevel.URGENT: "🟠", 
        TriageLevel.PROMPT: "🟡",
        TriageLevel.ROUTINE: "🔵",
        TriageLevel.SELF_CARE: "🟢"
    }
    
    with st.container():
        st.markdown(f"""
        <div class="result-card">
            <h3>{level_colors[result.level]} Triage Assessment: {result.level.name}</h3>
            <hr>
            <p><strong>Recommendation:</strong> {result.recommendation}</p>
            <p><strong>Action Required:</strong> {result.action_required}</p>
            <p><strong>Confidence:</strong> {result.confidence:.0%}</p>
            {f'<p class="severity-high"><strong>Red Flags Detected:</strong> {", ".join(result.triggered_symptoms)}</p>' if result.triggered_symptoms else ''}
        </div>
        """, unsafe_allow_html=True)


def render_differential(differentials: List[Dict]):
    """Render differential diagnosis results."""
    st.subheader("📋 Differential Analysis")
    st.markdown("*Based on symptom pattern matching (simulated for prototype)*")
    
    for i, dx in enumerate(differentials, 1):
        prob_color = "severity-high" if dx["probability"] == "High" else \
                     "severity-moderate" if dx["probability"] == "Moderate" else "severity-low"
        
        with st.expander(f"{i}. {dx['condition']} — Probability: {dx['probability']}", expanded=i==1):
            st.markdown(f"""
            <div class="info-card">
                <p><strong>Key Features:</strong> {', '.join(dx['key_features'])}</p>
                <p><strong>Recommended Evaluation:</strong> {', '.join(dx['recommended_tests'])}</p>
                <p class="{prob_color}"><strong>System Confidence:</strong> {dx['confidence']:.0%}</p>
            </div>
            """, unsafe_allow_html=True)


def render_disclaimer():
    """Render the medical disclaimer."""
    st.markdown("""
    <div class="disclaimer">
        <strong>⚠️ IMPORTANT MEDICAL DISCLAIMER</strong><br>
        This system is a <strong>research prototype</strong> for PhD thesis development only. 
        It is <strong>NOT</strong> intended for actual clinical use without physician oversight.<br><br>
        • Never disregard professional medical advice because of information from this system<br>
        • In case of emergency, always call your local emergency number (911/112)<br>
        • This tool does not diagnose conditions—it provides information to discuss with your doctor<br>
        • All data is processed locally and not stored on external servers
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# TAB 1: SYMPTOM CHECKER
# =============================================================================

def symptom_checker_tab():
    """Render the Symptom Checker interface."""
    st.header("🔍 Symptom Checker")
    st.markdown("Describe your symptoms for AI-assisted triage and differential analysis.")
    
    # Initialize engines
    triage_engine = TriageEngine()
    symptom_analyzer = SymptomAnalyzer()
    
    with st.form("symptom_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Demographics")
            age = st.number_input("Age", min_value=0, max_value=120, value=35, step=1)
            sex = st.selectbox("Biological Sex", ["Male", "Female", "Other", "Prefer not to say"])
        
        with col2:
            st.subheader("Symptom Details")
            duration = st.selectbox(
                "How long have symptoms been present?",
                ["Sudden (minutes)", "Hours", "Days", "Weeks", "Months"]
            )
            severity = st.slider("Overall Severity (1=Mild, 10=Severe)", 1, 10, 5)
        
        st.divider()
        
        # Structured symptom selection
        st.subheader("Select Symptoms")
        symptoms_by_system = symptom_analyzer.get_symptoms_by_system()
        
        selected_symptoms = []
        cols = st.columns(3)
        for idx, (system, symptoms) in enumerate(symptoms_by_system.items()):
            with cols[idx % 3]:
                st.markdown(f"**{system}**")
                for key, name in symptoms:
                    is_red = key in RED_FLAG_SYMPTOMS
                    label = f"🚨 {name}" if is_red else name
                    if st.checkbox(label, key=f"symptom_{key}"):
                        selected_symptoms.append(key)
        
        st.divider()
        
        # Free text input
        st.subheader("Additional Details (Free Text)")
        free_text = st.text_area(
            "Describe your symptoms in your own words",
            placeholder="Example: 'I have a sharp pain in my chest that started 2 hours ago and radiates to my left arm...'",
            height=100
        )
        
        # Submit button
        submitted = st.form_submit_button("🔬 Analyze Symptoms", use_container_width=True, type="primary")
    
    # Process submission
    if submitted:
        if not selected_symptoms and not free_text.strip():
            st.warning("Please select at least one symptom or describe your condition.")
            return
        
        with st.spinner("Running clinical analysis..."):
            # Perform triage
            triage_result = triage_engine.analyze(
                selected_symptoms, free_text, duration, severity, age
            )
            
            # Generate differential (if not emergency)
            if triage_result.level != TriageLevel.EMERGENCY:
                differentials = symptom_analyzer.generate_differential(
                    selected_symptoms, free_text, age, sex
                )
            else:
                differentials = []
            
            # Store in history
            st.session_state.triage_history.append({
                "timestamp": datetime.now().isoformat(),
                "triage_level": triage_result.level.name,
                "symptoms": selected_symptoms
            })
        
        # Display results
        st.divider()
        render_emergency_banner(triage_result)
        render_triage_result(triage_result)
        
        if differentials:
            render_differential(differentials)
        
        # Show raw analysis data (for research/debugging)
        with st.expander("🔧 Technical Analysis Details (Research View)"):
            st.json({
                "session_id": st.session_state.session_id,
                "timestamp": datetime.now().isoformat(),
                "inputs": {
                    "age": age,
                    "sex": sex,
                    "duration": duration,
                    "severity": severity,
                    "selected_symptoms": selected_symptoms,
                    "free_text": free_text[:200] + "..." if len(free_text) > 200 else free_text
                },
                "triage_result": {
                    "level": triage_result.level.name,
                    "risk_score": "Calculated via multi-layer algorithm",
                    "triggered_flags": triage_result.triggered_symptoms,
                    "confidence": triage_result.confidence
                }
            })


# =============================================================================
# TAB 2: MEDICATION INQUIRY
# =============================================================================

def medication_inquiry_tab():
    """Render the Medication Inquiry interface."""
    st.header("💊 Medication Inquiry")
    st.markdown("Check for drug interactions and pharmacovigilance concerns.")
    
    # Initialize engine
    pharm_engine = PharmacovigilanceEngine()
    
    with st.form("medication_form"):
        st.subheader("Select Current Medications")
        st.markdown("Choose all medications you are currently taking:")
        
        med_list = pharm_engine.get_medication_list()
        
        # Organize medications by category
        meds_by_category = {}
        for key in med_list:
            med = pharm_engine.get_medication_info(key)
            cat = med.category if med else "Other"
            if cat not in meds_by_category:
                meds_by_category[cat] = []
            meds_by_category[cat].append((key, med))
        
        selected_meds = []
        cols = st.columns(2)
        for idx, (category, medications) in enumerate(sorted(meds_by_category.items())):
            with cols[idx % 2]:
                st.markdown(f"**{category}**")
                for key, med in medications:
                    if st.checkbox(f"{med.name} ({med.common_dosage})", key=f"med_{key}"):
                        selected_meds.append(key)
        
        st.divider()
        
        # Additional context
        st.subheader("Clinical Context")
        has_allergies = st.text_input("Known Drug Allergies (comma-separated)", 
                                      placeholder="e.g., penicillin, sulfa")
        kidney_disease = st.checkbox("Chronic Kidney Disease")
        liver_disease = st.checkbox("Liver Disease")
        pregnancy = st.checkbox("Pregnancy/Breastfeeding")
        
        submitted = st.form_submit_button("🔍 Check Interactions", use_container_width=True, type="primary")
    
    # Process submission
    if submitted:
        if len(selected_meds) < 1:
            st.warning("Please select at least one medication.")
            return
        
        with st.spinner("Analyzing drug interactions..."):
            results = pharm_engine.check_interactions(selected_meds)
            
            # Store in history
            st.session_state.medication_history.append({
                "timestamp": datetime.now().isoformat(),
                "medications": selected_meds,
                "interactions_found": results["summary"]["total"]
            })
        
        # Display results
        st.divider()
        st.subheader("📊 Interaction Analysis Results")
        
        # Summary card
        risk_level = results["summary"]["risk_level"]
        risk_color = {
            "HIGH": "severity-high",
            "MODERATE": "severity-moderate", 
            "LOW": "severity-low",
            "NONE": "severity-low"
        }[risk_level]
        
        st.markdown(f"""
        <div class="result-card">
            <h3>Interaction Risk Level: <span class="{risk_color}">{risk_level}</span></h3>
            <p>Total Interactions Found: <strong>{results['summary']['total']}</strong></p>
            <p>🔴 Major: {results['summary']['major']} | 
               🟠 Moderate: {results['summary']['moderate']} | 
               🟢 Minor: {results['summary']['minor']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Detailed interactions
        if results["interactions"]:
            st.subheader("Detailed Interaction Reports")
            for interaction in results["interactions"]:
                severity_class = f"drug-interaction-{interaction.severity.value}"
                severity_emoji = {"major": "🔴", "moderate": "🟠", "minor": "🟢"}[interaction.severity.value]
                
                st.markdown(f"""
                <div class="{severity_class}">
                    <strong>{severity_emoji} {interaction.severity.value.upper()} INTERACTION</strong><br>
                    <strong>Between:</strong> {interaction.drug1.title()} + {interaction.drug2.title()}<br>
                    <strong>Mechanism:</strong> {interaction.mechanism}<br>
                    <strong>Clinical Effect:</strong> {interaction.clinical_effect}<br>
                    <strong>Management:</strong> {interaction.management}<br>
                    <small><strong>Evidence Level:</strong> {interaction.evidence_level}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No known interactions found between selected medications.")
        
        # Contextual warnings
        if pregnancy and any(m in selected_meds for m in ["warfarin", "sertraline"]):
            st.warning("⚠️ **Pregnancy Alert:** Some selected medications may require special consideration during pregnancy. Consult your obstetrician.")
        
        if kidney_disease and any(m in selected_meds for m in ["metformin", "ibuprofen"]):
            st.warning("⚠️ **Renal Alert:** Selected medications may require dose adjustment in kidney disease.")
        
        # Medication information cards
        with st.expander("📖 Medication Reference Information"):
            for med_key in selected_meds:
                med = pharm_engine.get_medication_info(med_key)
                if med:
                    st.markdown(f"""
                    **{med.name}** (RxCUI: {med.rxcui})
                    - Category: {med.category}
                    - Typical Dosage: {med.common_dosage}
                    - DrugBank ID: {med.drugbank_id}
                    """)
                    st.divider()


# =============================================================================
# SIDEBAR & MAIN APPLICATION
# =============================================================================

def render_sidebar():
    """Render the application sidebar."""
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/health-checkup.png", width=80)
        st.title("CDSS Dashboard")
        
        st.markdown("---")
        st.subheader("📊 Session Statistics")
        st.metric("Triage Checks", len(st.session_state.triage_history))
        st.metric("Medication Checks", len(st.session_state.medication_history))
        st.metric("Session ID", st.session_state.session_id[:8] + "...")
        
        st.markdown("---")
        st.subheader("🚨 Emergency Resources")
        st.markdown("""
        - **911** (US Emergency)
        - **988** Suicide & Crisis Lifeline
        - **Poison Control:** 1-800-222-1222
        """)
        
        st.markdown("---")
        st.subheader("📚 About This System")
        st.markdown("""
        This is a **PhD research prototype** demonstrating:
        - Multimodal symptom input processing
        - Rule-based clinical triage
        - Drug interaction pharmacovigilance
        - Evidence-based AI safety constraints
        
        **Version:** 0.1.0-alpha  
        **Last Updated:** 2026-05-10
        """)
        
        # Session management
        if st.button("🗑️ Clear Session History", use_container_width=True):
            st.session_state.triage_history = []
            st.session_state.medication_history = []
            st.rerun()


def main():
    """Main application entry point."""
    init_session_state()
    render_header()
    render_sidebar()
    
    # Create tabs
    tab1, tab2 = st.tabs(["🔍 Symptom Checker", "💊 Medication Inquiry"])
    
    with tab1:
        symptom_checker_tab()
    
    with tab2:
        medication_inquiry_tab()
    
    # Global disclaimer
    st.divider()
    render_disclaimer()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()