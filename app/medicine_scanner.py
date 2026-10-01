"""
app/medicine_scanner.py - Identifies common medicines and provides simple, age-friendly explanations.
Handles image uploads, filenames, and medicine text inputs for English, Hindi, and Gujarati.
"""
import re
import os
import base64
from typing import Dict, Any, Optional

COMMON_MEDICINES = {
    "paracetamol": {
        "name": "Paracetamol (Dolo 650 / Crocin / Calpol / P-500)",
        "icon": "💊",
        "category": "Fever & Pain Relief",
        "en": {
            "used_for": "Commonly used to lower mild-to-moderate fever and relieve body aches, headache, toothache, or cold pain.",
            "how_to_use": "Usually taken with a full glass of water after meals.",
            "simple_tips": "Do not take more than recommended on the strip. Stay well-hydrated. If fever lasts over 3 days, see a doctor.",
            "who_to_ask": "People with liver conditions should always consult a doctor first."
        },
        "hi": {
            "used_for": "हल्के से मध्यम बुखार को कम करने और सिरदर्द, बदन दर्द या सर्दी के दर्द में आराम देने के लिए उपयोग की जाती है।",
            "how_to_use": "आमतौर पर भोजन के बाद एक गिलास पानी के साथ ली जाती है।",
            "simple_tips": "स्ट्रिप पर लिखी सलाह से ज्यादा न लें। भरपूर पानी पिएं। बुखार 3 दिन से अधिक रहे तो डॉक्टर को दिखाएं।",
            "who_to_ask": "लिवर की बीमारी वाले लोग डॉक्टर से पूछकर ही लें।"
        },
        "gu": {
            "used_for": "હળવો તાવ ઉતારવા અને માથાનો કે શરીરનો દુખાવો ઓછો કરવા માટે વપરાય છે.",
            "how_to_use": "સામાન્ય રીતે જમ્યા પછી એક ગ્લાસ પાણી સાથે લેવાય છે.",
            "simple_tips": "પેકેટ પર લખેલ સલાહથી વધુ ન લો. પૂરતું પાણી પીવો. જો તાવ ૩ દિવસથી વધુ રહે તો ડૉક્ટરને બતાવો.",
            "who_to_ask": "લિવરની તકલીફ હોય તેમણે ડૉક્ટરની સલાહ લેવી."
        }
    },
    "ors": {
        "name": "ORS (Oral Rehydration Salts / Electral)",
        "icon": "💧",
        "category": "Hydration & Electrolyte Balance",
        "en": {
            "used_for": "Replenishes vital fluids and salts lost during loose motions (diarrhea), vomiting, or dehydration in summer heat.",
            "how_to_use": "Dissolve 1 standard packet completely into exactly 1 liter of clean drinking water. Drink in small sips.",
            "simple_tips": "Do not mix with milk or juice. Discard and make fresh solution after 24 hours.",
            "who_to_ask": "Safe for everyone including babies, toddlers, and elderly family members."
        },
        "hi": {
            "used_for": "दस्त, उल्टी या गर्मी से शरीर में पानी और नमक की कमी को पूरा करने के लिए।",
            "how_to_use": "एक पैकेट को ठीक 1 लीटर साफ पानी में घोलें और घूंट-घूंट करके पिएं।",
            "simple_tips": "दूध या जूस में न मिलाएं। 24 घंटे के बाद नया घोल बनाएं।",
            "who_to_ask": "शिशुओं, बच्चों और बुजुर्गों सहित सभी के लिए पूर्णतः सुरक्षित।"
        },
        "gu": {
            "used_for": "ઝાડા, ઉલટી કે ગરમીના કારણે શરીરમાં ઘટેલા પાણી અને ક્ષારની પૂર્તિ માટે.",
            "how_to_use": "૧ પેકેટ ૧ લીટર સ્વચ્છ પાણીમાં ઓગાળીને ધીમે ધીમે પીવો.",
            "simple_tips": "દૂધ કે જ્યુસમાં ન ભેળવો. ૨૪ કલાક પછી નવું દ્રાવણ બનાવો.",
            "who_to_ask": "બાળકો અને વડીલો સહિત સૌ માટે અત્યંત સુરક્ષિત."
        }
    },
    "cetirizine": {
        "name": "Cetirizine / Levocetirizine (Cetzine / Okacet / Alerid)",
        "icon": "🤧",
        "category": "Allergy & Cold Relief",
        "en": {
            "used_for": "Relieves allergy symptoms like continuous sneezing, runny nose, itchy throat, watery eyes, and skin hives.",
            "how_to_use": "Usually taken once daily at bedtime, as it can cause slight drowsiness.",
            "simple_tips": "May cause mild sleepiness; avoid driving right after taking it.",
            "who_to_ask": "Elderly and children should take the exact dosage recommended by a doctor."
        },
        "hi": {
            "used_for": "लगातार छींकें आना, बहती नाक, गले की खुजली और त्वचा पर एलर्जी के चकत्तों में राहत के लिए।",
            "how_to_use": "आमतौर पर रात को सोने से पहले ली जाती है क्योंकि इससे हल्की नींद आ सकती है।",
            "simple_tips": "हल्की सुस्ती आ सकती है, इसलिए लेने के बाद गाड़ी न चलाएं।",
            "who_to_ask": "बुजुर्गों और बच्चों के लिए डॉक्टर से उचित मात्रा पूछें।"
        },
        "gu": {
            "used_for": "છીંક, વહેતું નાક, ગળામાં ખંજવાળ અને ચામડીની એલર્જીમાં રાહત માટે.",
            "how_to_use": "સામાન્ય રીતે રાત્રે સૂતી વખતે લેવાય છે કારણ કે ઊંઘ આવી શકે છે.",
            "simple_tips": "હળવી સુસ્તી આવી શકે છે, તેથી ડ્રાઇવિંગ ટાળો.",
            "who_to_ask": "બાળકો અને વડીલો માટે ડૉક્ટરની સલાહ મુજબ લો."
        }
    },
    "pantoprazole": {
        "name": "Pantoprazole / Omeprazole (Pan 40 / Omez / Pantocid)",
        "icon": "🔥",
        "category": "Acidity & Heartburn Relief",
        "en": {
            "used_for": "Reduces excess stomach acid to relieve heartburn, sour belching, acid reflux, and stomach irritation.",
            "how_to_use": "Best taken first thing in the morning on an empty stomach, 30 minutes before tea or breakfast.",
            "simple_tips": "Swallow whole with water; do not crush. Avoid heavy oily or spicy foods.",
            "who_to_ask": "If burning chest pain spreads to jaw, back or left arm, seek emergency care immediately."
        },
        "hi": {
            "used_for": "पेट में अतिरिक्त एसिड को शांत करने, सीने में जलन और खट्टी डकारों से राहत के लिए।",
            "how_to_use": "सुबह खाली पेट, चाय या नाश्ते से 30 मिनट पहले पानी के साथ लें।",
            "simple_tips": "गोली को चबाएं नहीं, सीधी निगलें। तला-भुना खाना न खाएं।",
            "who_to_ask": "अगर सीने का दर्द जबड़े या हाथ में फैले तो तुरंत अस्पताल जाएं।"
        },
        "gu": {
            "used_for": "પેટમાં એસિડિટી ઓછી કરવા, છાતીમાં બળતરા અને ખાટા ઓડકારમાં રાહત માટે.",
            "how_to_use": "સવારે ભૂખ્યા પેટે નાસ્તાના ૩૦ મિનિટ પહેલાં પાણી સાથે લો.",
            "simple_tips": "ગોળી આખી ગળી જાઓ. તીખો ખોરાક ટાળો.",
            "who_to_ask": "જો છાતીનો દુખાવો હાથ તરફ ફેલાય તો તાત્કાલિક સારવાર લો."
        }
    },
    "cough_syrup": {
        "name": "Cough Syrup (Ascoril / Benadryl / Honitus / Grilinctus)",
        "icon": "🍯",
        "category": "Cough & Throat Soothing",
        "en": {
            "used_for": "Soothes irritated airways, eases dry coughing, or loosens thick chest mucus.",
            "how_to_use": "Use the measured measuring cap provided. Avoid drinking water immediately after so it coats the throat.",
            "simple_tips": "Warm water gargles and steam inhalation work wonders alongside syrups.",
            "who_to_ask": "Check if it is meant for 'dry cough' or 'wet cough'. Diabetics should use sugar-free."
        },
        "hi": {
            "used_for": "गले की खराश को शांत करने और सूखी या बलगम वाली खांसी में आराम देने के लिए।",
            "how_to_use": "दिए गए ढक्कन से नाप कर पिएं। पीने के तुरंत बाद पानी न पिएं।",
            "simple_tips": "गर्म पानी के गरारे और भाप लेना भी बहुत असरदार है।",
            "who_to_ask": "डायबिटीज के मरीज शुगर-फ्री सिरप का ही इस्तेमाल करें।"
        },
        "gu": {
            "used_for": "ગળાની બળતરા શાંત કરવા અને સૂકી કે કફવાળી ઉધરસમાં રાહત માટે.",
            "how_to_use": "માપવાના ઢાંકણાથી માપીને પીવો. પીધા પછી તરત પાણી ન પીવું.",
            "simple_tips": "હૂંફાળા પાણીના કોગળા અને વરાળ લેવી ખૂબ ફાયદાકારક છે.",
            "who_to_ask": "ડાયાબિટીસ હોય તેમણે સુગર-ફ્રી સિરપ લેવી."
        }
    },
    "antacid": {
        "name": "Antacid (Gelusil / Digene / Gas-O-Fast)",
        "icon": "🌿",
        "category": "Quick Gas & Indigestion Relief",
        "en": {
            "used_for": "Neutralizes stomach acid quickly to relieve acute gas, bloating, and burning indigestion.",
            "how_to_use": "Chew tablet thoroughly or shake liquid bottle well and take after meals or when feeling heartburn.",
            "simple_tips": "Sip water slowly. Avoid lying flat immediately after meals.",
            "who_to_ask": "Good for occasional relief. If acidity happens daily, consult a doctor to check the cause."
        },
        "hi": {
            "used_for": "अचानक गैस, पेट फूलने और बदहजमी की जलन में तुरंत आराम के लिए।",
            "how_to_use": "गोली को चबाकर खाएं या सिरप को हिलाकर भोजन के बाद लें।",
            "simple_tips": "खाना खाने के तुरंत बाद सीधा न लेटें। थोड़ा टहलें।",
            "who_to_ask": "कभी-कभार के लिए उपयुक्त। रोज समस्या हो तो डॉक्टर से जांच कराएं।"
        },
        "gu": {
            "used_for": "અચાનક ગેસ, પેટનું ફૂલવું અને અપચાની બળતરામાં ઝડપી રાહત માટે.",
            "how_to_use": "ગોળી ચાવીને ખાવી અથવા લિક્વિડ બરાબર હલાવીને જમ્યા પછી લેવું.",
            "simple_tips": "જમ્યા પછી તરત સૂઈ ન જવું. થોડું ચાલવું સારું રહેશે.",
            "who_to_ask": "ક્યારેક માટે સારું. જો રોજ તકલીફ હોય તો ડૉક્ટરને બતાવો."
        }
    },
    "antibiotic": {
        "name": "Antibiotic (Amoxicillin / Azithromycin / Ciprofloxacin)",
        "icon": "⚠️",
        "category": "Prescription Antibacterial",
        "en": {
            "used_for": "Treats specific bacterial infections diagnosed by a doctor. INEFFECTIVE against viral colds, flu, or simple coughs.",
            "how_to_use": "STRICTLY as prescribed by your registered doctor. Always complete the entire prescribed course.",
            "simple_tips": "Never self-medicate or take leftover antibiotics from family members. Doing so causes antibiotic resistance.",
            "who_to_ask": "Must ONLY be taken with a valid doctor's prescription."
        },
        "hi": {
            "used_for": "केवल डॉक्टर द्वारा पहचाने गए बैक्टीरिया संक्रमण के लिए। सामान्य सर्दी, जुकाम या फ्लू के वायरस पर यह काम नहीं करती।",
            "how_to_use": "केवल पंजीकृत डॉक्टर के पर्चे के अनुसार। डॉक्टर द्वारा बताया गया पूरा कोर्स पूरा करें।",
            "simple_tips": "बिना डॉक्टर की सलाह के कभी एंटीबायोटिक न लें। इससे शरीर में दवा का असर खत्म होने का खतरा रहता है।",
            "who_to_ask": "केवल डॉक्टर के परामर्श पर ही लें।"
        },
        "gu": {
            "used_for": "માત્ર ડૉક્ટર દ્વારા નિદાન થયેલ બેક્ટેરિયલ ચેપ માટે. સામાન્ય શરદી કે વાયરલ તાવ પર આ દવા કામ કરતી નથી.",
            "how_to_use": "માત્ર ડૉક્ટરના પ્રિસ્ક્રિપ્શન મુજબ. ડૉક્ટરે કહેલો પૂરો કોર્સ પૂર્ણ કરવો.",
            "simple_tips": "ડૉક્ટરની સલાહ વિના ક્યારેય એન્ટિબાયોટિક ન લેવી.",
            "who_to_ask": "માત્ર યોગ્ય ડૉક્ટરની સલાહથી જ લેવી."
        }
    }
}


def identify_medicine_from_input(
    filename: str = "",
    text_content: str = "",
    image_data: str = "",
    language: str = "en"
) -> Dict[str, Any]:
    """
    Identifies the medicine from image filename, OCR text, or user input,
    and returns friendly, simple guidance suitable for every age group.
    """
    lang = language.lower()
    if lang not in ["en", "hi", "gu"]:
        lang = "en"

    combined = f"{filename} {text_content}".lower()

    matched_key = None
    if any(k in combined for k in ["paracetamol", "crocin", "dolo", "calpol", "p-500", "pcm", "fever"]):
        matched_key = "paracetamol"
    elif any(k in combined for k in ["ors", "electral", "rehydration", "loose", "diarrhea"]):
        matched_key = "ors"
    elif any(k in combined for k in ["cetirizine", "cetzine", "okacet", "alerid", "levocet", "allergy", "cold"]):
        matched_key = "cetirizine"
    elif any(k in combined for k in ["pantoprazole", "omeprazole", "pan", "omez", "pantocid", "gas", "acid"]):
        matched_key = "pantoprazole"
    elif any(k in combined for k in ["cough", "syrup", "benadryl", "ascoril", "honitus", "grilinctus", "khansi"]):
        matched_key = "cough_syrup"
    elif any(k in combined for k in ["gelusil", "digene", "antacid", "gas-o-fast", "eno"]):
        matched_key = "antacid"
    elif any(k in combined for k in ["amoxicillin", "azithromycin", "ciprofloxacin", "augmentin", "antibiotic", "mox"]):
        matched_key = "antibiotic"
    else:
        # If user uploaded generic image without recognizable medicine name in filename
        # Provide general medicine strip safety reading guide
        if lang == "hi":
            return {
                "status": "guideline",
                "medicine_id": "general_guide",
                "name": "दवा का पत्ता (Medicine Strip) पढ़ने का सही तरीका",
                "icon": "🔍",
                "category": "दवा सुरक्षा मार्गदर्शिका",
                "used_for": "किसी भी दवा को लेने से पहले पत्ते पर उसका जेनेरिक नाम (Active Salt) और एक्सपायरी डेट अवश्य देखें।",
                "how_to_use": "दवा को हमेशा साफ पानी के साथ लें। डॉक्टर या फार्मासिस्ट द्वारा बताए गए समय पर ही लें।",
                "simple_tips": "1. एक्सपायरी तारीख (EXP Date) पार होने के बाद कभी दवा न लें। 2. दवा को धूप और नमी से दूर रखें। 3. बच्चों की पहुंच से दूर रखें।",
                "who_to_ask": "यदि दवा पर लाल लकीर (Schedule H / Rx) बनी है, तो यह केवल डॉक्टर के पर्चे पर ही ली जानी चाहिए।",
                "disclaimer": "सूचनात्मक सहायता। हमेशा अपने पंजीकृत डॉक्टर या फार्मासिस्ट से सलाह लें।"
            }
        elif lang == "gu":
            return {
                "status": "guideline",
                "medicine_id": "general_guide",
                "name": "દવાની પટ્ટી (Medicine Strip) વાંચવાની યોગ્ય રીત",
                "icon": "🔍",
                "category": "દવા સુરક્ષા માર્ગદર્શિકા",
                "used_for": "દવા લેતાં પહેલાં તેનું નામ અને એક્સપાયરી તારીખ (EXP) ખાસ તપાસો.",
                "how_to_use": "હંમેશા સ્વચ્છ પાણી સાથે લો. ડૉક્ટરે સૂચવેલા સમયે જ લો.",
                "simple_tips": "૧. એક્સપાયરી તારીખ પૂરી થઈ ગઈ હોય તો દવા ક્યારેય ન લો. ૨. દવાને તડકા અને ભેજથી દૂર રાખો. ૩. બાળકોથી દૂર રાખો.",
                "who_to_ask": "જો પટ્ટી પર લાલ લીટી (Rx) હોય તો તે માત્ર ડૉક્ટરના પ્રિસ્ક્રિપ્શનથી જ લેવી.",
                "disclaimer": "માત્ર માહિતી માટે. હંમેશા ડૉક્ટર કે ફાર્માસિસ્ટની સલાહ લો."
            }
        else:
            return {
                "status": "guideline",
                "medicine_id": "general_guide",
                "name": "Medicine Label & Strip Reading Guide",
                "icon": "🔍",
                "category": "Safe Medicine Practice",
                "used_for": "Always inspect the generic salt name and Expiry Date (EXP) printed on the medicine blister pack.",
                "how_to_use": "Take with plain clean water as directed by your doctor. Do not mix with soft drinks or alcohol.",
                "simple_tips": "1. Never consume medicines past their Expiry Date. 2. Store in a cool, dry place away from direct sunlight. 3. Keep safely out of reach of children.",
                "who_to_ask": "If the strip has a red vertical line (Rx / Schedule H), it requires a registered doctor's prescription.",
                "disclaimer": "Informational guide only. Always consult a registered physician or pharmacist."
            }

    med = COMMON_MEDICINES[matched_key]
    info = med.get(lang, med["en"])

    return {
        "status": "success",
        "medicine_id": matched_key,
        "name": med["name"],
        "icon": med["icon"],
        "category": med["category"],
        "used_for": info["used_for"],
        "how_to_use": info["how_to_use"],
        "simple_tips": info["simple_tips"],
        "who_to_ask": info["who_to_ask"],
        "disclaimer": "Informational only. Always read packaging and consult a registered doctor or pharmacist."
    }
