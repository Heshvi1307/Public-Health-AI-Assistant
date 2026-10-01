"""
app/chat_handler.py - Conversational AI Health Assistant (Swasthya Saarthi).
Provides empathetic, multilingual, multi-turn health guidance inside deterministic safety guardrails.
"""
import re
from typing import List, Dict, Any, Optional

from safety.red_flags import scan_for_red_flags
from safety.output_filter import scan_text_for_violations, validate_llm_output_safety
from knowledge.retriever import retrieve_relevant_knowledge
from safety.safety_floor import calculate_safety_floor, enforce_safety_floor
from validators.input_validator import ValidatedIntake


SYSTEM_CHAT_PROMPT = """You are Swasthya Saarthi (स्वास्थ्य सारथी), a compassionate and helpful Public Health Information Assistant for India.
You provide clear, supportive, and accessible health guidance in simple everyday language.

CORE RESPONSIBILITIES:
1. Warmly listen to the user's symptoms and acknowledge how they are feeling with genuine empathy.
2. Ask clear, targeted clarifying questions if critical context is missing (duration, severity, breathing difficulty).
3. Offer supportive, non-pharmacological self-care measures (hydration, rest, steam inhalation, warm salt gargle).
4. Highlight important warning signs to watch out for.
5. Clearly tell the user when they should consult a doctor in person.

STRICT MEDICAL & SAFETY CONSTRAINTS:
- NEVER diagnose any condition (do not say "You have malaria" or "You have COVID"). Say "These symptoms can have several common causes."
- NEVER prescribe medication, antibiotics, or exact drug dosages (NO milligrams, NO "take 500mg paracetamol", NO tablets).
- NEVER tell a patient to stop any prescribed treatments.
- Always include a gentle reminder that you are an informational assistant and not a replacement for a doctor.
- Answer in the same language as the user (English, Hindi, or Gujarati).
"""


def get_saarthi_welcome_message(language: str = "en") -> Dict[str, Any]:
    """Returns the introductory greeting from Saarthi."""
    if language == "hi":
        return {
            "text": "नमस्ते! मैं आपका स्वास्थ्य सारथी (Swasthya Saarthi) हूँ। 🙏\n\nमैं आपको और आपके परिवार को लक्षणों को समझने, सुरक्षित घरेलू देखभाल के उपाय जानने और यह तय करने में मदद करूँगा कि डॉक्टर को कब दिखाना चाहिए।\n\nआप आज कैसा महसूस कर रहे हैं? कृपया अपने लक्षण बताएं।",
            "quick_replies": [
                "बुखार और कंपकंपी 🌡️",
                "सर्दी और खांसी 🤧",
                "सिरदर्द और भारीपन 🤕",
                "पेट खराब या दस्त 🤢",
                "स्वास्थ्य जांच (Guided Test) 📋"
            ]
        }
    elif language == "gu":
        return {
            "text": "નમસ્તે! હું તમારો સ્વાસ્થ્ય સારથી (Swasthya Saarthi) છું. 🙏\n\nહું તમને તમારા લક્ષણો સમજવામાં, સામાન્ય ઘરેલું સંભાળના ઉપાયો જાણવામાં અને ડૉક્ટરની સલાહ ક્યારે લેવી તે નક્કી કરવામાં મદદ કરીશ.\n\nતમે આજે કેવું અનુભવો છો? કૃપા કરીને જણાવો.",
            "quick_replies": [
                "તાવ અને શરદી 🌡️",
                "ખાંસી અને કફ 🤧",
                "માથાનો દુખાવો 🤕",
                "ઝાડા કે ઉલટી 🤢",
                "હેલ્થ ટેસ્ટ (Guided Test) 📋"
            ]
        }
    else:
        return {
            "text": "Namaste! I am Swasthya Saarthi, your Public Health Information Assistant. 🙏\n\nI am here to help you understand your symptoms, share safe self-care guidance, and let you know when it is important to see a healthcare professional.\n\nHow are you feeling today? You can describe your symptoms below or pick a common topic.",
            "quick_replies": [
                "Fever & Chills 🌡️",
                "Cough & Cold 🤧",
                "Headache 🤕",
                "Stomach Upset / Loose Motions 🤢",
                "Start Guided Health Check 📋"
            ]
        }


def process_chat_message(
    user_message: str,
    conversation_history: List[Dict[str, str]],
    language: str = "en",
    context_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Processes incoming user message through deterministic safety and empathetic assistant reasoning.
    """
    clean_text = (user_message or "").strip()
    lang = language.lower()
    if lang not in ["en", "hi", "gu"]:
        lang = "en"

    context = context_data or {}
    user_name = context.get("user_name", "").strip()
    name_salutation = ""
    if user_name and user_name.lower() != "user":
        first_name = user_name.split()[0]
        if lang == "hi":
            name_salutation = f"{first_name} जी, "
        elif lang == "gu":
            name_salutation = f"{first_name}, "
        else:
            name_salutation = f"{first_name}, "


    # 1. IMMEDIATE RED-FLAG CHECK (Pre-LLM deterministic intercept)
    red_flag = scan_for_red_flags(clean_text, language=lang)
    if red_flag.is_red_flag:
        # Build immediate emergency response card
        if red_flag.flag_type == "mental_health":
            if lang == "hi":
                reply = (
                    "**आप अकेले नहीं हैं। कृपया तुरंत सहायता लें।** 💜\n\n"
                    "आप जो महसूस कर रहे हैं वह बहुत महत्वपूर्ण है। कृपया तुरंत अपने किसी करीबी या मानसिक स्वास्थ्य हेल्पलाइन से संपर्क करें।"
                )
            elif lang == "gu":
                reply = (
                    "**તમે એકલા નથી. કૃપા કરીને તાત્કાલિક સહાય મેળવો.** 💜\n\n"
                    "તમારી ભાવનાઓ ખૂબ મહત્વપૂર્ણ છે. કૃપા કરીને તરત જ વિશ્વાસુ વ્યક્તિ અથવા હેલ્પલાઈનનો સંપર્ક કરો."
                )
            else:
                reply = (
                    "**You are not alone. Please reach out for immediate support.** 💜\n\n"
                    "What you are experiencing matters. Please speak with someone you trust or connect with a 24x7 crisis counselor immediately."
                )
            return {
                "reply": reply,
                "is_emergency": True,
                "flag_type": "mental_health",
                "alert_card": {
                    "type": "crisis",
                    "title": red_flag.title,
                    "message": red_flag.message,
                    "actions": [
                        {"label": "Call Tele-MANAS (14416)", "phone": "14416", "primary": True},
                        {"label": "National Helpline (112)", "phone": "112"},
                    ]
                },
                "quick_replies": []
            }
        else:
            # Physical Medical Emergency
            if lang == "hi":
                reply = (
                    "**🚨 आपातकालीन चेतावनी संकेत! तुरंत चिकित्सा सहायता प्राप्त करें।**\n\n"
                    "आपके विवरण में ऐसे लक्षण हैं जिन्हें तुरंत आपातकालीन डॉक्टर की आवश्यकता हो सकती है। कृपया इस चैट पर निर्भर न रहें और तुरंत एम्बुलेंस को कॉल करें।"
                )
            elif lang == "gu":
                reply = (
                    "**🚨 કટોકટી ચેતવણી! તાત્કાલિક સારવાર મેળવો.**\n\n"
                    "તમારા લક્ષણોને તાત્કાલિક હોસ્પિટલની કટોકટી સારવારની જરૂર હોઈ શકે છે. કૃપા કરીને તરત જ એમ્બ્યુલન્સ બોલાવો."
                )
            else:
                reply = (
                    "**🚨 Emergency Warning Sign Detected! Seek Immediate Medical Help.**\n\n"
                    "Your message describes warning signs that may require urgent medical care. Please do not wait or rely solely on this assistant. Call emergency services right now."
                )
            return {
                "reply": reply,
                "is_emergency": True,
                "flag_type": "emergency",
                "alert_card": {
                    "type": "emergency",
                    "title": red_flag.title,
                    "message": red_flag.message,
                    "actions": [
                        {"label": "Call 108 (Ambulance)", "phone": "108", "primary": True},
                        {"label": "Call 112 (National Emergency)", "phone": "112"},
                    ]
                },
                "quick_replies": []
            }

    # 2. ADVERSARIAL INJECTION & DOSAGE DEFENSE
    lower_input = clean_text.lower()
    if any(kw in lower_input for kw in ["ignore previous", "ignore instructions", "diagnose me", "tell me what disease"]):
        if lang == "hi":
            reply = "मैं एक सार्वजनिक स्वास्थ्य सूचना सहायक हूँ। सुरक्षा और नैतिक कारणों से, मैं बीमारियों का निश्चित चिकित्सीय निदान नहीं कर सकता। हालांकि, मैं आपके लक्षणों के आधार पर सुरक्षित प्राथमिक देखभाल और सामान्य जानकारी साझा कर सकता हूँ। क्या आप बता सकते हैं कि ये लक्षण कितने समय से हैं?"
        elif lang == "gu":
            reply = "હું એક જાહેર આરોગ્ય સહાયક છું. સુરક્ષા નિયમો મુજબ હું રોગનું ચોક્કસ નિદાન કરી શકતો નથી. પરંતુ હું તમારા લક્ષણો અનુસાર ઘરેલું સંભાળ અને સામાન્ય માર્ગદર્શન આપી શકું છું."
        else:
            reply = "I am an informational public health assistant. For clinical safety, I cannot provide medical diagnoses or identify specific diseases. However, I can help you understand your symptoms, safe supportive self-care, and when to see a physician. How many days have you had these symptoms?"
        return {
            "reply": reply,
            "is_emergency": False,
            "quick_replies": ["<24 hours", "1-3 days", "4-7 days", "More than a week"]
        }

    if any(kw in lower_input for kw in ["how many mg", "tablet", "dosage", "antibiotic", "paracetamol"]):
        if lang == "hi":
            reply = "सार्वजनिक स्वास्थ्य सुरक्षा दिशानिर्देशों के अनुसार, मैं दवाइयों के नाम या मिलीग्राम (mg) की खुराक नहीं बता सकता। दवाओं की सही मात्रा आपकी उम्र, वजन और डॉक्टर की जांच पर निर्भर करती है। सुरक्षित आराम के लिए पर्याप्त पानी पिएं और अपने नजदीकी डॉक्टर या फार्मासिस्ट से परामर्श लें।"
        elif lang == "gu":
            reply = "સુરક્ષા કારણોસર હું દવાઓ કે મિલિગ્રામ (mg) નો ડોઝ આપી શકતો નથી. દવાની યોગ્ય માત્રા માટે કૃપા કરીને ડૉક્ટરની સલાહ લો. સામાન્ય રાહત માટે પૂરતું પાણી પીવો અને આરામ કરો."
        else:
            reply = "In accordance with public health safety rules, I cannot prescribe pharmaceutical medications or recommend specific dosages (such as milligrams or number of tablets). Medication dosages require a physical medical consultation. For safe comfort, focus on hydration and rest, and consult a qualified healthcare provider."
        return {
            "reply": reply,
            "is_emergency": False,
            "quick_replies": ["Rest & Hydration tips", "When to see a doctor", "Other symptoms"]
        }

    # 3. KNOWLEDGE-GROUNDED CONVERSATIONAL GUIDANCE
    matched_knowledge = retrieve_relevant_knowledge(clean_text)
    
    # Check for core conditions
    is_fever = any(w in lower_input for w in ["fever", "bukhar", "temperature", "ताप", "તાવ", "বুখার"])
    is_cough_cold = any(w in lower_input for w in ["cough", "cold", "runny nose", "sneezing", "khansi", "खांसी", "શરદી", "ઉધરસ"])
    is_headache = any(w in lower_input for w in ["headache", "head pain", "sir dard", "माथा", "માથું"])
    is_stomach = any(w in lower_input for w in ["diarrhea", "vomit", "loose motion", "dast", "ulti", "ઝાડા", "उल्टी"])

    # Formulate empathetic structured guidance
    # Check for general guidelines query
    is_guidelines = any(w in lower_input for w in ["guideline", "guidelines", "tips", "lifestyle", "healthy habit", "prevention", "नियम", "सुझाव", "સલાહ", "નિયમો"])

    if is_guidelines:
        if lang == "hi":
            reply = (
                "यहाँ दैनिक जीवन के लिए महत्वपूर्ण **सार्वजनिक स्वास्थ्य दिशानिर्देश (WHO एवं MoHFW)** दिए गए हैं:\n\n"
                "• **💧 पर्याप्त पानी पिएं:** दिनभर में 8-10 गिलास (2.5 से 3 लीटर) साफ पानी पिएं।\n"
                "• **🥗 संतुलित आहार:** भोजन में ताजी हरी सब्जियां, दालें और फल शामिल करें। अधिक तले और मीठे भोजन से बचें।\n"
                "• **😴 7-8 घंटे की नींद:** रोग प्रतिरोधक क्षमता (इम्यूनिटी) मजबूत रखने के लिए पूरी नींद लें।\n"
                "• **🚶‍♂️ शारीरिक सक्रियता:** प्रतिदिन कम से कम 30 मिनट तेज चलें या हल्का व्यायाम करें।\n"
                "• **🧼 स्वच्छता:** खाना खाने से पहले और शौच के बाद साबुन से हाथ अवश्य धोएं।\n"
                "• **🩺 समय पर जांच:** 30 वर्ष से अधिक उम्र होने पर बीपी और ब्लड शुगर की नियमित जांच कराएं।"
            )
            quick_replies = ["बुखार के लिए सुझाव 🌡️", "सर्दी-खांसी के उपाय 🤧", "हेल्थ टेस्ट शुरू करें 📋"]
        elif lang == "gu":
            reply = (
                "દૈનિક તંદુરસ્તી માટેના મહત્વપૂર્ણ **જાહેર આરોગ્ય નિયમો (WHO & MoHFW)**:\n\n"
                "• **💧 પૂરતું પાણી:** દિવસમાં ૨.૫ થી ૩ લીટર સ્વચ્છ પીવાનું પાણી લો.\n"
                "• **🥗 પૌષ્ટિક આહાર:** લીલા શાકભાજી, કઠોળ અને તાજા ફળો ખોરાકમાં રાખો.\n"
                "• **😴 ૭-૮ કલાકની ઊંઘ:** રોગપ્રતિકારક શક્તિ જાળવવા યોગ્ય ઊંઘ જરૂરી છે.\n"
                "• **🚶‍♂️ કસરત:** રોજ ઓછામાં ઓછું ૩૦ મિનિટ ઝડપી ચાલો.\n"
                "• **🧼 સ્વચ્છતા:** જમતાં પહેલાં હાથ સાબુથી બરાબર ધોવા."
            )
            quick_replies = ["તાવ માટે સલાહ 🌡️", "શરદી માટે સલાહ 🤧", "ટેસ્ટ શરૂ કરો 📋"]
        else:
            reply = (
                "Here are core **Public Health Guidelines for Daily Wellness (WHO & MoHFW)**:\n\n"
                "• **💧 Adequate Hydration:** Drink 2.5 to 3 liters (8–10 glasses) of clean water daily.\n"
                "• **🥗 Balanced Nutrition:** Prioritize fresh vegetables, lentils (dal), whole grains, and limit high-salt, deep-fried foods.\n"
                "• **😴 Restorative Sleep:** Ensure 7–8 hours of quality sleep to support immune repair.\n"
                "• **🚶‍♂️ Physical Activity:** Aim for at least 30 minutes of brisk walking or light exercise most days.\n"
                "• **🧼 Hand Hygiene:** Wash hands with soap and water before meals and after outdoor contact.\n"
                "• **🩺 Preventive Screenings:** Have routine checks for blood pressure and blood sugar annually."
            )
            quick_replies = ["Fever advice 🌡️", "Cough & Cold care 🤧", "Take Health Test 📋"]

    elif is_fever:
        if lang == "hi":
            reply = (
                "हल्का बुखार अक्सर वायरल संक्रमण के खिलाफ शरीर की स्वाभाविक रोग-प्रतिरोधक प्रतिक्रिया होती है।\n\n"
                "**🌿 सुरक्षित देखभाल के उपाय:**\n"
                "• हल्के और हवादार कपड़े पहनें, शरीर को ढक कर बहुत अधिक गर्म न रखें।\n"
                "• डिहाइड्रेशन से बचने के लिए पर्याप्त मात्रा में गुनगुना पानी, ओआरएस (ORS) या सूप पिएं।\n"
                "• यदि अत्यधिक गर्मी लगे तो माथे पर सामान्य पानी की ठंडी पट्टी रखें (बर्फ का पानी न लगाएं)।\n\n"
                "**⚠️ इन चेतावनी संकेतों पर तुरंत डॉक्टर से मिलें:**\n"
                "• बुखार 3 दिन से अधिक समय तक लगातार बना रहे।\n"
                "• गर्दन में अकड़न, अत्यधिक सुस्ती या त्वचा पर लाल चकत्ते आएं।"
            )
            quick_replies = ["तापमान 100° से अधिक है", "खांसी भी आ रही है", "1-2 दिन से है", "3+ दिन से है"]
        elif lang == "gu":
            reply = (
                "હળવો તાવ સામાન્ય રીતે ચેપ સામે શરીરની કુદરતી રોગપ્રતિકારક શક્તિ દર્શાવે છે.\n\n"
                "**🌿 સામાન્ય કાળજીના ઉપાયો:**\n"
                "• પૂરતા પ્રમાણમાં પાણી, ઓઆરએસ (ORS) અને પ્રવાહી લો.\n"
                "• હળવા કપડાં પહેરો અને પૂરતો આરામ કરો.\n"
                "• જરૂર જણાય તો સામાન્ય નવશેકા પાણીથી સ્પોન્જિંગ કરો.\n\n"
                "**⚠️ સાવચેતીના લક્ષણો:**\n"
                "• તાવ ૩ દિવસથી વધુ સમય સુધી રહે.\n"
                "• ગરદન કડક થવી કે અતિશય સુસ્તી લાગવી."
            )
            quick_replies = ["૧-૨ દિવસથી છે", "૩ દિવસથી વધુ છે", "શરદી પણ છે"]
        else:
            reply = (
                "Mild fever is commonly the body's natural defense mechanism fighting off a viral irritation.\n\n"
                "**🌿 Supportive Self-Care:**\n"
                "• Rest in a well-ventilated room with light clothing.\n"
                "• Stay well-hydrated with plenty of water, clear broths, or Oral Rehydration Salts (ORS).\n"
                "• Use a lukewarm sponge bath on forehead and neck if feeling uncomfortably warm (never ice-cold water).\n"
                "• Record your temperature with a clean digital thermometer.\n\n"
                "**⚠️ When to Seek Care:**\n"
                "• Fever lasting longer than 3 consecutive days.\n"
                "• Accompanied by stiff neck, confusion, or difficulty breathing."
            )
            quick_replies = ["Fever is 1-2 days", "Fever is 3+ days", "Have cough too", "Child has fever"]

    elif is_cough_cold:
        if lang == "hi":
            reply = (
                "सर्दी-जुकाम और खांसी ज्यादातर ऊपरी श्वसन नली के हल्के वायरल संक्रमण होते हैं, जो 7 से 10 दिनों में ठीक हो जाते हैं।\n\n"
                "**🌿 सुरक्षित घरेलू आराम के उपाय:**\n"
                "• दिन में 2-3 बार गर्म पानी से भाप (Steam) लें ताकि बंद नाक खुले।\n"
                "• गले की खराश के लिए हल्के गुनगुने नमक के पानी से गरारे करें।\n"
                "• गुनगुना पानी और हर्बल चाय पिएं और पर्याप्त आराम करें।\n\n"
                "**⚠️ डॉक्टर को कब दिखाएं:**\n"
                "• सांस लेने में भारी तकलीफ या सीने में दर्द हो।\n"
                "• खांसी में खून आए या यह 2 सप्ताह से अधिक समय तक बनी रहे।"
            )
            quick_replies = ["गले में खराश है", "सूखी खांसी है", "सांस लेने में कोई दिक्कत नहीं"]
        elif lang == "gu":
            reply = (
                "સામાન્ય શરદી અને ખાંસી વાયરલ ચેપના કારણે હોય છે અને સામાન્ય રીતે ૭-૧૦ દિવસમાં આપમેળે મટે છે.\n\n"
                "**🌿 ઘરેલું રાહતના ઉપાયો:**\n"
                "• ગળા માટે મીઠાવાળા હૂંફાળા પાણીના કોગળા કરો.\n"
                "• દિવસમાં ૨ વાર વરાળ (સ્ટીમ) લો.\n"
                "• હૂંફાળું પાણી અને સૂપ પીવો, પૂરતો આરામ કરો.\n\n"
                "**⚠️ ડૉક્ટરનો સંપર્ક ક્યારે કરવો:**\n"
                "• શ્વાસ લેવામાં તકલીફ જણાય અથવા ઉધરસમાં લોહી આવે."
            )
            quick_replies = ["ગળામાં દુખાવો છે", "સાદી શરદી છે", "૨ દિવસથી છે"]
        else:
            reply = (
                "Symptoms of a common cold and cough are typically self-limiting viral upper respiratory infections that peak in 2–3 days and resolve within 7–10 days.\n\n"
                "**🌿 Supportive Self-Care:**\n"
                "• Drink plenty of warm liquids including water, clear soups, and herbal teas.\n"
                "• Perform warm saline gargles to soothe throat irritation.\n"
                "• Use steam inhalation to loosen nasal mucus and relieve congestion.\n"
                "• Ensure adequate sleep to help your immune system recover.\n\n"
                "**⚠️ When to Seek Care:**\n"
                "• Any shortness of breath, wheezing, or chest tightness.\n"
                "• Coughing up blood or symptoms lasting more than 2 weeks."
            )
            quick_replies = ["Dry cough", "Sore throat too", "Mild cold (<3 days)", "Persistent (>1 week)"]

    elif is_headache:
        if lang == "hi":
            reply = (
                "हल्का सिरदर्द अक्सर तनाव, निर्जलीकरण (कम पानी पीना), नींद की कमी या स्क्रीन पर अधिक समय बिताने से हो सकता है।\n\n"
                "**🌿 राहत के उपाय:**\n"
                "• एक बड़ा गिलास पानी पिएं ताकि डिहाइड्रेशन दूर हो सके।\n"
                "• शांत, मंद रोशनी वाले कमरे में थोड़ी देर विश्राम करें।\n"
                "• माथे पर हल्की ठंडी या गर्म पट्टी रखें।\n\n"
                "**⚠️ आपातकालीन चेतावनी:**\n"
                "• यदि सिरदर्द अचानक और बहुत तीव्र हो ('जीवन का सबसे भयानक सिरदर्द')।\n"
                "• यदि इसके साथ उल्टी, गर्दन में अकड़न या बेहोशी हो, तो तुरंत अस्पताल जाएं।"
            )
            quick_replies = ["हल्का तनाव वाला दर्द", "उल्टी नहीं है", "नींद की कमी है"]
        elif lang == "gu":
            reply = (
                "માથાનો દુખાવો તણાવ, ઊંઘનો અભાવ અથવા પાણી ઓછું પીવાના કારણે થઈ શકે છે.\n\n"
                "**🌿 રાહતના ઉપાયો:**\n"
                "• પૂરતું પાણી પીવો અને શાંત જગ્યાએ આરામ કરો.\n"
                "• સ્ક્રીન (મોબાઇલ/કોમ્પ્યુટર) થી થોડો બ્રેક લો.\n\n"
                "**⚠️ જો અચાનક અસહ્ય તીવ્ર દુખાવો થાય અથવા ઉલટી થાય, તો તાત્કાલિક ડૉક્ટરને બતાવો.**"
            )
            quick_replies = ["સામાન્ય દુખાવો", "પાણી પીધું છે"]
        else:
            reply = (
                "Mild tension-type headaches are commonly related to stress, eye strain, dehydration, or lack of sleep.\n\n"
                "**🌿 Self-Care Measures:**\n"
                "• Drink a large glass of clean water to ensure dehydration is not the cause.\n"
                "• Rest in a quiet, dimly lit room and take a break from digital screens.\n"
                "• Gently massage the temples and perform light neck stretches.\n\n"
                "**⚠️ Red Flags:**\n"
                "• Sudden explosive headache ('worst headache of your life').\n"
                "• Headache accompanied by high fever, stiff neck, or vomiting."
            )
            quick_replies = ["Mild headache", "Feeling tired / strained", "No fever or vomiting"]

    elif is_stomach:
        if lang == "hi":
            reply = (
                "दस्त या पेट खराब होने में सबसे बड़ा खतरा शरीर में पानी और लवण (Dehydration) की कमी का होता है।\n\n"
                "**🌿 महत्वपूर्ण देखभाल:**\n"
                "• डब्ल्यूएचओ (WHO) प्रमाणित ओआरएस (ORS) का घोल नियमित पिएं।\n"
                "• हल्का और सुपाच्य भोजन लें जैसे खिचड़ी, केला, दही या चावल का मांड।\n"
                "• शौच के बाद और भोजन से पहले साबुन से हाथ अच्छी तरह धोएं।\n\n"
                "**⚠️ तुरंत डॉक्टर से मिलें:**\n"
                "• मल में खून आना, 8 घंटे से पेशाब न होना या अत्यधिक कमजोरी महसूस होना।"
            )
            quick_replies = ["ओआरएस पी रहा हूँ", "उल्टी नहीं है", "हल्के दस्त हैं"]
        else:
            reply = (
                "With loose motions or an upset stomach, the primary public health priority is preventing dehydration.\n\n"
                "**🌿 Priority Care:**\n"
                "• Sip WHO-formulated Oral Rehydration Salts (ORS) solution regularly.\n"
                "• Eat light, easily digestible foods like rice, bananas, and khichdi.\n"
                "• Wash hands thoroughly with soap before eating and after using the restroom.\n\n"
                "**⚠️ When to Seek Urgent Care:**\n"
                "• Any signs of severe dehydration: no urination for >8 hours, sunken eyes, dry mouth.\n"
                "• Presence of blood in stools or inability to retain any liquids."
            )
            quick_replies = ["Sipping ORS", "Started today", "No blood in stool"]

    else:
        # General supportive guidance
        if lang == "hi":
            reply = (
                "मैं आपके द्वारा बताए गए लक्षणों को समझ रहा हूँ। सुरक्षित और सटीक जानकारी के लिए क्या आप कुछ और बातें बता सकते हैं?\n\n"
                "• यह परेशानी आपको कितने दिनों से हो रही है?\n"
                "• क्या यह हल्की है, मध्यम है या बहुत गंभीर?\n"
                "• क्या कोई अन्य लक्षण भी हैं (जैसे बुखार, सांस लेने में दिक्कत या उल्टी)?"
            )
            quick_replies = ["1-2 दिन से है", "लक्षण हल्के हैं", "सामान्य स्वास्थ्य नियम 📋"]
        elif lang == "gu":
            reply = (
                "હું તમારા લક્ષણો સમજી રહ્યો છું. વધુ યોગ્ય સલાહ માટે:\n\n"
                "• આ તકલીફ કેટલા દિવસથી છે?\n"
                "• શું તાવ કે અન્ય કોઈ મુશ્કેલી છે?"
            )
            quick_replies = ["૧-૨ દિવસથી છે", "લક્ષણો હળવા છે", "આરોગ્ય નિયમો 📋"]
        else:
            reply = (
                "Thank you for sharing your symptoms. To help guide you safely, could you clarify a few details?\n\n"
                "• How long have you been experiencing this?\n"
                "• Would you describe it as mild, moderate, or severe?\n"
                "• Are you noticing any other symptoms like fever, headache, or breathing discomfort?"
            )
            quick_replies = ["Since yesterday (<24h)", "Mild discomfort", "General Guidelines 📋", "Take Guided Assessment 📋"]

    # Prepend personalized name salutation
    if name_salutation:
        reply = f"**{name_salutation}**" + reply


    # 4. Output Safety Filter Scan
    violations = scan_text_for_violations(reply)
    if violations:
        reply = (
            "Based on public health guidelines, monitor your symptoms closely, ensure adequate hydration and rest. "
            "If your symptoms persist or worsen, please consult a qualified healthcare professional in person."
        )

    return {
        "reply": reply,
        "is_emergency": False,
        "quick_replies": quick_replies,
        "source": "WHO & MoHFW Public Health Clinical Guidelines"
    }
