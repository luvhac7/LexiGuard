"""
Case Comparison Agent - Juris-AI Elite Legal Strategist.
"""

import os
import json
import logging
from typing import List, Dict, Any
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
try:
    load_dotenv()
    this_dir = Path(__file__).parent
    project_root = this_dir.parent
    load_dotenv(project_root / '.env')
    load_dotenv(project_root / 'api_testing' / '.env')
except Exception as e:
    logger.warning(f"Error loading .env files: {e}")

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.error("GEMINI_API_KEY not found!")

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GENERATION_CONFIG = {
    "temperature": 0.2,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

JURIS_AI_PROMPT = """
You are *Juris-AI*, an Elite Legal Strategist and Case Comparison Engine.

*INPUT DATA:*
You will receive a JSON object (docs) containing metadata (Title, Date, Headline) for two legal cases.
*Note: The user provides metadata only. You must use the title and publishdate to RECALL the full facts, arguments, and judgments from your internal training data.*

*YOUR MISSION:*
Perform a "Super-Human" deep-dive analysis comparing these two cases. You must map your analysis strictly to the following *3-Phase Schema*.

---

### *PHASE 1: THE RADAR (Similarities)*
Analyze the overlap across 4 distinct dimensions. Score them (0-100) and provide reasoning.
1.  *Contextual:* Are the physical events similar? (e.g., For medical cases: Surgery type, patient demographics, outcome).
2.  *Procedural:* Do they rely on the same documents? (e.g., Post-Mortem Reports, Expert Opinions, Case Sheets).
3.  *Legal:* Is the charge/trial type the same? (e.g., Consumer Deficiency vs. Criminal Negligence vs. Civil Tort).
4.  *Real-World Impact:* Do they share societal costs? (e.g., Trust in doctors, Hospital liability, Victim trauma).

### *PHASE 2: THE ECOSYSTEM (The Narrative)*
Identify the "Shared Ecosystem" (e.g., "The Medical Liability System" or "The Indian Road Accident System").
* *The Chaos:* Compare the "Trigger Act" (e.g., The surgery gone wrong vs. The accident). Real vs. Alleged.
* *The Gatekeepers:* Compare the "Authority Figures" (e.g., Doctors/Police). Did they protect or perpetrate?
* *The Paper Truth:* Compare the role of documentation (e.g., Medical Records/FIRs). Did they reveal the truth or hide a lie?
* *The Mirror Effect:* Explain how one case is the "hack" or "inverse" of the other (e.g., One establishes duty, the other punishes breach).

### *PHASE 3: THE 12-POINT DEEP DIVE*
Compare granular details side-by-side:
1. Core Subject | 2. Trigger Event | 3. Key Statute | 4. Evidence Used
5. Defense Plea | 6. Role of Authority (Police/Doctor) | 7. Timeline
8. Judicial Logic | 9. Outcome | 10. Doctrinal Point | 11. Tone of Court | 12. Citable Utility

---

*OUTPUT FORMAT:*
Return *ONLY* a valid JSON object. Do not include markdown formatting.

json
{
  "meta": {
    "case_a_title": "string",
    "case_b_title": "string",
    "domain_detected": "string (e.g., Medical Negligence)"
  },
  "radar_analysis": {
    "contextual_score": 0, "contextual_reasoning": "string",
    "procedural_score": 0, "procedural_reasoning": "string",
    "legal_score": 0, "legal_reasoning": "string",
    "real_world_score": 0, "real_world_reasoning": "string"
  },
  "ecosystem_analysis": {
    "shared_ecosystem_name": "string",
    "the_chaos": "string",
    "the_gatekeepers": "string",
    "the_paper_truth": "string",
    "the_mirror_effect": "string"
  },
  "deep_dive_matrix": [
    { "dimension": "1. Core Subject", "case_a": "string", "case_b": "string", "insight": "string" },
    { "dimension": "2. Trigger Event", "case_a": "string", "case_b": "string", "insight": "string" },
    { "dimension": "3. Key Statute", "case_a": "string", "case_b": "string", "insight": "string" },
    { "dimension": "4. Evidence Used", "case_a": "string", "case_b": "string", "insight": "string" },
    { "dimension": "5. Defense Plea", "case_a": "string", "case_b": "string", "insight": "string" },
    { "dimension": "6. Role of Authority", "case_a": "string", "case_b": "string", "insight": "string" },
    { "dimension": "7. Timeline", "case_a": "string", "case_b": "string", "insight": "string" },
    { "dimension": "8. Judicial Logic", "case_a": "string", "case_b": "string", "insight": "string" },
    { "dimension": "9. Outcome", "case_a": "string", "case_b": "string", "insight": "string" },
    { "dimension": "10. Doctrinal Point", "case_a": "string", "case_b": "string", "insight": "string" },
    { "dimension": "11. Tone of Court", "case_a": "string", "case_b": "string", "insight": "string" },
    { "dimension": "12. Citable Utility", "case_a": "string", "case_b": "string", "insight": "string" }
  ]
}

[USER INPUT]
{user_input_json}
"""

JURIS_AI_RADAR_ONLY_PROMPT = """
You are *Juris-AI*, an Elite Legal Strategist.

*INPUT DATA:*
You will receive a JSON object containing:
1. "primary_case": Metadata for the main case.
2. "comparison_cases": A list of metadata for other cases to compare against the primary case.

*YOUR MISSION:*
For EACH comparison case, perform *PHASE 1: THE RADAR (Similarities)* analysis against the primary case.
Analyze the overlap across 4 distinct dimensions. Score them (0-100).

1. *Contextual:* Are the physical events similar?
2. *Procedural:* Do they rely on the same documents?
3. *Legal:* Is the charge/trial type the same?
4. *Real-World Impact:* Do they share societal costs?

*OUTPUT FORMAT:*
Return *ONLY* a valid JSON object.
{
  "batch_results": [
    {
      "case_id": "string (tid or doc_id from input)",
      "case_title": "string",
      "radar": {
        "contextual_score": 0,
        "procedural_score": 0,
        "legal_score": 0,
        "real_world_score": 0
      }
    }
  ]
}

[USER INPUT]
{user_input_json}
"""

def call_gemini(prompt: str) -> Dict[str, Any]:
    """Call Gemini API."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set")
    
    try:
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        
        model = genai.GenerativeModel(MODEL)
        
        # Safety settings to allow legal content - using proper enums
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        response = model.generate_content(
            prompt,
            generation_config=GENERATION_CONFIG,
            safety_settings=safety_settings
        )
        
        # Check for safety blocks
        if response.candidates and response.candidates[0].finish_reason == 2:  # SAFETY
            logger.warning("Content was blocked by safety filters")
            raise ValueError("Content blocked by safety filters. Please try with different cases or contact support.")
        
        if not response.text:
            if response.candidates and response.candidates[0].finish_reason:
                raise ValueError(f"Empty response - finish_reason: {response.candidates[0].finish_reason}")
            raise ValueError("Empty response from Gemini")
        
        text = response.text.strip()
        # Clean markdown
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        # Fix common JSON issues
        text = text.replace('\n', ' ').replace('\r', ' ')
            
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        raise ValueError(f"Failed to parse Gemini response as JSON: {str(e)}")
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        raise

    return call_gemini(prompt)

def generate_radar_heatmap(radar_data: Dict[str, Any]) -> str:
    """
    Generates a heatmap for the radar analysis scores.
    radar_data: dict containing score keys (contextual_score, etc.)
    Returns: base64 encoded image string
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import seaborn as sns
        import pandas as pd
        import io
        import base64

        # Extract scores
        data = {
            'Contextual': radar_data.get('contextual_score', 0),
            'Procedural': radar_data.get('procedural_score', 0),
            'Legal': radar_data.get('legal_score', 0),
            'Real-World': radar_data.get('real_world_score', 0)
        }
        
        # Create DataFrame for Seaborn (1 row)
        df = pd.DataFrame([data])
        
        # Set up the plot
        plt.figure(figsize=(10, 2.5))
        sns.set_theme(style="white")
        
        # Create heatmap
        # Using a purple colormap to match the UI
        ax = sns.heatmap(df, annot=True, fmt="d", cmap="Purples", vmin=0, vmax=100, 
                         cbar=False, linewidths=1, square=False, annot_kws={"size": 14, "weight": "bold"})
        
        plt.title("Similarity Radar Heatmap", fontsize=14, pad=15, weight='bold', color='#4b5563')
        plt.yticks([]) # Hide y-axis labels
        plt.xticks(fontsize=11, weight='medium', color='#4b5563')
        plt.tight_layout()
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=150)
        buf.seek(0)
        
        # Encode
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        logger.error(f"Error generating heatmap: {e}")
        return None

def compare_cases_juris_ai(docs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare cases using Juris-AI logic.
    docs: List of dicts with 'title', 'date', etc.
    """
    user_input = {"docs": docs}
    # Use replace instead of format to avoid issues with curly braces in the prompt
    prompt = JURIS_AI_PROMPT.replace('{user_input_json}', json.dumps(user_input, indent=2))
    
    result = call_gemini(prompt)
    
    # Generate heatmap if radar analysis is present
    if result and 'radar_analysis' in result:
        heatmap = generate_radar_heatmap(result['radar_analysis'])
        if heatmap:
            result['radar_analysis']['heatmap_image'] = heatmap
            
    return result

def generate_batch_heatmap(batch_results: List[Dict[str, Any]]) -> str:
    """
    Generates a heatmap for batch radar analysis.
    Y-axis: Case # (1, 2, 3...)
    X-axis: Dimensions (Contextual, Procedural, Legal, Real-World)
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import seaborn as sns
        import pandas as pd
        import io
        import base64

        # Prepare data for DataFrame
        data = []
        rows = []
        for idx, res in enumerate(batch_results):
            radar = res.get('radar', {})
            row_label = f"Case #{idx + 1}"
            rows.append(row_label)
            data.append({
                'Contextual': radar.get('contextual_score', 0),
                'Procedural': radar.get('procedural_score', 0),
                'Legal': radar.get('legal_score', 0),
                'Real-World': radar.get('real_world_score', 0)
            })
        
        if not data:
            return None

        df = pd.DataFrame(data, index=rows)
        
        # Set up the plot
        # Height depends on number of cases
        plt.figure(figsize=(10, max(3, len(rows) * 0.8)))
        sns.set_theme(style="white")
        
        # Create heatmap
        ax = sns.heatmap(df, annot=True, fmt="d", cmap="Purples", vmin=0, vmax=100, 
                         cbar=False, linewidths=1, square=False, annot_kws={"size": 12, "weight": "bold"})
        
        plt.title("Batch Similarity Radar Heatmap", fontsize=14, pad=15, weight='bold', color='#4b5563')
        plt.yticks(rotation=0, fontsize=11, weight='medium', color='#4b5563')
        plt.xticks(fontsize=11, weight='medium', color='#4b5563')
        plt.tight_layout()
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=150)
        buf.seek(0)
        
        # Encode
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        logger.error(f"Error generating batch heatmap: {e}")
        return None

def compare_cases_radar_batch(primary_doc: Dict[str, Any], other_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare a primary case against a batch of other cases (Radar phase only).
    """
    user_input = {
        "primary_case": primary_doc,
        "comparison_cases": other_docs
    }
    prompt = JURIS_AI_RADAR_ONLY_PROMPT.replace('{user_input_json}', json.dumps(user_input, indent=2))
    
    result = call_gemini(prompt)
    
    if result and 'batch_results' in result:
        heatmap = generate_batch_heatmap(result['batch_results'])
        if heatmap:
            result['heatmap_image'] = heatmap
            
    return result

# ============================================================================
# BIAS DETECTION PROMPT AND FUNCTION
# ============================================================================

BIAS_DETECTION_PROMPT = """
You are *Juris-AI*, an Elite Judicial Bias Detection Engine.

*INPUT DATA:*
You will receive a JSON object (docs) containing metadata (Title, Date, Headline) for two legal cases.
*Note: The user provides metadata only. You must use the title and publishdate to RECALL the full facts, arguments, and judgments from your internal training data.*

*YOUR MISSION:*
Perform a comprehensive judicial bias analysis comparing these two cases using the 6-Part Judicial Bias Comparison Framework.

---

### 1️⃣ POWER DYNAMICS BIAS (Authority & Systemic Forces)

Analyze who holds institutional or social power and identify if the judge favors one side.

For each case, provide:
- **Power Dynamic**: Who is the powerful entity vs the weaker entity?
- **Analysis**: How does the judge treat each side?
- **Bias Verdict**: Authority Bias, Anti-Authority Bias, Pro-State Bias, etc.

### 2️⃣ EMOTIONAL TEMPERATURE (Linguistic Tone Analysis)

Detect the emotional tone of the judge's language.

For each case, provide:
- **Temperature**: COOL (clinical), WARM (sympathetic), HOT (moral outrage)
- **Keywords**: List emotionally charged or neutral words used by the judge
- **Insight**: What does the emotional tone reveal about the judge's mindset?

### 3️⃣ COGNITIVE BIAS CHECK (Psychological Biases)

Identify hidden cognitive biases affecting the judge's reasoning.

For each case, provide:
- **Observation**: What fact pattern or reasoning suggests bias?
- **Bias Type**: Outcome Bias, Hindsight Bias, Confirmation Bias, Anchoring, Severity Bias
- **Agent Alert**: How this bias may have influenced the final judgment

### 4️⃣ MISSING VOICE ANALYSIS (Justice-for-Who Test)

Identify whose perspective is ignored or minimized.

For each case, provide:
- **Affected Party**: Who should have been central to the judgment?
- **Status**: Silent Object / Financial Victim / Overlooked Stakeholder
- **Explanation**: How the court sidelines their role or experience

### 5️⃣ LEGAL REASONING STRUCTURE BIAS (Logic & Framing Analysis)

Detect selective use of precedent and inconsistent application of standards.

For each case, provide:
- **Reasoning Style**: Strict interpretation vs Purposive interpretation
- **Standard Application**: Consistent or selective?
- **Precedent Usage**: How precedents are cited and applied
- **Insight**: Whether reasoning style changes to achieve a preferred outcome

### 6️⃣ SENTENCING / REMEDY DISPARITY CHECK

Analyze punishment mismatch and disproportionate sentencing.

For each case, provide:
- **Punishment/Remedy**: What was awarded/imposed?
- **Proportionality**: Is it proportional to intent + context?
- **Comparison**: Are similar harms treated differently?
- **Insight**: Is one case punished for symbolism while another minimally?

---

*OUTPUT FORMAT:*
Return *ONLY* a valid JSON object. Do not include markdown formatting.

{
  "meta": {
    "case_a_title": "string",
    "case_b_title": "string",
    "domain_detected": "string (e.g., Medical Negligence, Constitutional Law)"
  },
  "power_dynamics": {
    "case_a": {
      "power_dynamic": "string",
      "analysis": "string",
      "bias_verdict": "string"
    },
    "case_b": {
      "power_dynamic": "string",
      "analysis": "string",
      "bias_verdict": "string"
    },
    "comparative_insight": "string"
  },
  "emotional_temperature": {
    "case_a": {
      "temperature": "COOL/WARM/HOT",
      "keywords": ["string"],
      "insight": "string"
    },
    "case_b": {
      "temperature": "COOL/WARM/HOT",
      "keywords": ["string"],
      "insight": "string"
    },
    "comparative_insight": "string"
  },
  "cognitive_bias": {
    "case_a": {
      "observation": "string",
      "bias_type": "string",
      "agent_alert": "string"
    },
    "case_b": {
      "observation": "string",
      "bias_type": "string",
      "agent_alert": "string"
    },
    "comparative_insight": "string"
  },
  "missing_voice": {
    "case_a": {
      "affected_party": "string",
      "status": "string",
      "explanation": "string"
    },
    "case_b": {
      "affected_party": "string",
      "status": "string",
      "explanation": "string"
    },
    "comparative_insight": "string"
  },
  "legal_reasoning": {
    "case_a": {
      "reasoning_style": "string",
      "standard_application": "string",
      "precedent_usage": "string",
      "insight": "string"
    },
    "case_b": {
      "reasoning_style": "string",
      "standard_application": "string",
      "precedent_usage": "string",
      "insight": "string"
    },
    "comparative_insight": "string"
  },
  "sentencing_disparity": {
    "case_a": {
      "punishment_remedy": "string",
      "proportionality": "string",
      "comparison": "string",
      "insight": "string"
    },
    "case_b": {
      "punishment_remedy": "string",
      "proportionality": "string",
      "comparison": "string",
      "insight": "string"
    },
    "comparative_insight": "string"
  }
}

[USER INPUT]
{user_input_json}
"""

def detect_bias_juris_ai(docs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Detect judicial bias using the 6-part framework.
    docs: List of dicts with 'title', 'date', etc.
    """
    user_input = {"docs": docs}
    prompt = BIAS_DETECTION_PROMPT.replace('{user_input_json}', json.dumps(user_input, indent=2))
    return call_gemini(prompt)
