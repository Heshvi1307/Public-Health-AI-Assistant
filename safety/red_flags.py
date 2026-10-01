"""
safety/red_flags.py - Deterministic multilingual red-flag detection engine.
Bypasses LLM completely when acute emergencies or mental health crises are detected.
"""
import re
from typing import Optional, Tuple, Dict, Any

# English, Hindi, Gujarati, and Hinglish patterns
EMERGENCY_PATTERNS = [
    # Chest pain / Heart attack
    r"\b(chest\s+pain|heart\s+attack|crushing\s+chest|tightness\s+in\s+chest)\b",
    r"सीने\s*में\s*दर्द",
    r"છાતીમાં\s*દુખાવો",
    r"\b(chhati|seene|chhati\s*me|seene\s*me)\s*(dard|pain)\b",

    # Breathing difficulty / Shortness of breath
    r"\b(severe\s+difficulty\s+breathing|can'?t\s+breathe|shortness\s+of\s+breath|gasping\s+for\s+air|suffocating)\b",
    r"सांस\s*लेने\s*में\s*(दिक्कत|परेशानी|तकलीफ)",
    r"શ્વાસ\s*લેવામાં\s*તકલીફ",
    r"\b(saans|sans)\s*(nahi\s*aa\s*rahi|ruk\s*rahi|me\s*takleef|phool\s*rahi)\b",

    # Loss of consciousness / Fainting / Unresponsive
    r"\b(unconscious|fainted|blacked\s+out|passed\s+out|unresponsive|not\s+waking\s+up)\b",
    r"बेहोश",
    r"બેભાન",
    r"\b(behosh|chakkar\s*aake\s*gir\s*gaye|hosh\s*kho\s*diya)\b",

    # Seizure / Convulsions
    r"\b(seizure|convulsion|convulsions|fits|epileptic\s+fit)\b",
    r"दौरा\s*पड़ना|दौरे|मिरगी",
    r"દૌરો|આંચકી|ખેંચ",
    r"\b(daura|mirgi|fits\s*aana)\b",

    # Heavy / Uncontrolled Bleeding
    r"\b(heavy\s+bleeding|uncontrolled\s+bleeding|profuse\s+bleeding|bleeding\s+heavily)\b",
    r"बहुत\s*ज्यादा\s*खून|रक्तस्राव",
    r"વધારે\s*લોહી|પુષ્કળ\s*લોહી",
    r"\b(khoon\s*bahut\s*aa\s*raha|khoon\s*ruk\s*nahi\s*raha)\b",

    # Vomiting blood / Blood in stool
    r"\b(vomiting\s+blood|blood\s+in\s+(stool|vomit|urine)|coughing\s+up\s+blood|hemoptysis)\b",
    r"खून\s*की\s*उल्टी|मल\s*में\s*खून",
    r"લોહીની\s*ઉલટી|ઝાડામાં\s*લોહી",
    r"\b(khoon\s*ki\s*ulti|latrine\s*me\s*khoon)\b",

    # Stroke signs: face drooping, slurred speech, paralysis, weakness
    r"\b(face\s+drooping|slurred\s+speech|one[- ]sided\s+weakness|paralysis|sudden\s+numbness|stroke)\b",
    r"लकवा|चेहरा\s*लटक|बोलने\s*में\s*दिक्कत|पक्षाघात",
    r"લકવો|મોઢું\s*ત્રાંસુ|બોલવામાં\s*તકલીફ",
    r"\b(lakwa|faalij|ek\s*taraf\s*kamzori)\b",

    # Snake bite, poisoning, severe allergy / anaphylaxis
    r"\b(snake\s*bite|poisoning|swallowed\s*poison|consumed\s*poison|anaphylaxis|severe\s*allergic\s*reaction)\b",
    r"सांप\s*का\s*काटना|जहर\s*खा\s*लिया|जहर",
    r"સાપ\s*કરડ્યો|ઝેર",
    r"\b(saanp\s*ne\s*kaata|zehar|zahar|poison)\b",

    # Emergency combinations
    r"\b(stiff\s+neck\s+and\s+fever|fever\s+and\s+stiff\s+neck)\b",
    r"गर्दन\s*अकड़ना\s*और\s*बुखार",
    r"ગરદન\s*કડક\s*અને\s*તાવ",
]

MENTAL_HEALTH_PATTERNS = [
    r"\b(suicide|suicidal|kill\s+myself|end\s+my\s+life|want\s+to\s+die|self[- ]harm|hanging\s+myself|cutting\s+myself)\b",
    r"आत्महत्या|मरना\s*चाहता\s*हूँ|मरना\s*चाहती\s*हूँ|जान\s*देना",
    r"આત્મહત્યા|જીવવું\s*નથી|મરી\s*જવું\s*છે",
    r"\b(suicide\s*karna|jaan\s*dena|mar\s*jaana\s*chahta|marne\s*ka\s*man)\b",
]


class RedFlagResult:
    def __init__(
        self,
        is_red_flag: bool,
        flag_type: Optional[str] = None,  # "emergency" or "mental_health"
        matched_pattern: Optional[str] = None,
        category: Optional[str] = None,
        title: str = "",
        message: str = "",
        helpline_numbers: Optional[Dict[str, str]] = None,
    ):
        self.is_red_flag = is_red_flag
        self.flag_type = flag_type
        self.matched_pattern = matched_pattern
        self.category = category
        self.title = title
        self.message = message
        self.helpline_numbers = helpline_numbers or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_red_flag": self.is_red_flag,
            "flag_type": self.flag_type,
            "matched_pattern": self.matched_pattern,
            "category": self.category,
            "title": self.title,
            "message": self.message,
            "helpline_numbers": self.helpline_numbers,
        }


def scan_for_red_flags(text: str, language: str = "en") -> RedFlagResult:
    """
    Deterministic prefilter that scans normalized free text for critical emergency
    and mental health triggers BEFORE calling the LLM.
    """
    if not text:
        return RedFlagResult(is_red_flag=False)

    clean_text = text.lower().strip()

    # 1. First Priority: Check Mental Health Crisis triggers
    for pat in MENTAL_HEALTH_PATTERNS:
        match = re.search(pat, clean_text, re.IGNORECASE)
        if match:
            if language == "hi":
                title = "आप अकेले नहीं हैं"
                msg = "यदि आप संकट या अत्यधिक तनाव में हैं, तो कृपया तुरंत किसी विश्वसनीय व्यक्ति या आपातकालीन मानसिक स्वास्थ्य सेवा से संपर्क करें।"
            elif language == "gu":
                title = "તમે એકલા નથી"
                msg = "જો તમે સંકટમાં છો અથવા માનસિક તણાવ અનુભવો છો, તો કૃપા કરીને તાત્કાલિક વિશ્વાસુ વ્યક્તિ અથવા માનસિક સહાય સેવાનો સંપર્ક કરો."
            else:
                title = "You are not alone"
                msg = "Please seek immediate support from a trusted person, family member, or crisis support service."

            return RedFlagResult(
                is_red_flag=True,
                flag_type="mental_health",
                matched_pattern=match.group(0),
                category="Mental Health Crisis",
                title=title,
                message=msg,
                helpline_numbers={
                    "Tele-MANAS (Govt of India 24x7)": "14416",
                    "KIRAN Mental Health Helpline": "1800-599-0019",
                    "National Emergency Number": "112",
                },
            )

    # 2. Second Priority: Check Acute Physical Emergency triggers
    for pat in EMERGENCY_PATTERNS:
        match = re.search(pat, clean_text, re.IGNORECASE)
        if match:
            if language == "hi":
                title = "तत्काल आपातकालीन चिकित्सा सहायता प्राप्त करें"
                msg = "आपके विवरण में ऐसे चेतावनी संकेत शामिल हैं जिनके लिए तत्काल आपातकालीन चिकित्सा ध्यान की आवश्यकता हो सकती है। इस सहायक पर निर्भर न रहें।"
            elif language == "gu":
                title = "તાત્કાલિક ઈમરજન્સી સારવાર મેળવો"
                msg = "તમારા વર્ણનમાં એવા લક્ષણો છે જેને તાત્કાલિક ડૉક્ટરની કટોકટી સારવારની જરૂર પડી શકે છે. આ આસિસ્ટન્ટ પર આધાર રાખશો નહીં."
            else:
                title = "Seek emergency medical help now"
                msg = "Your message contains a warning sign that may require urgent emergency medical attention. Do not rely on this assistant for an emergency."

            return RedFlagResult(
                is_red_flag=True,
                flag_type="emergency",
                matched_pattern=match.group(0),
                category="Acute Medical Emergency",
                title=title,
                message=msg,
                helpline_numbers={
                    "Ambulance / Medical Emergency": "108",
                    "National Emergency Helpline": "112",
                },
            )

    return RedFlagResult(is_red_flag=False)
