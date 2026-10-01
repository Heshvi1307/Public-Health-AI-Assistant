// static/app.js - Swasthya Saarthi Consumer Health Platform Logic

// Global State
let currentLanguage = 'en';
let currentView = 'landing'; // 'landing', 'chat', 'stepper'
let chatHistory = [];
let currentStep = 1;
let currentSpeechUtterance = null;
let isSpeaking = false;

// Authenticated User Profile (Stored in localStorage)
let currentUser = {
  name: 'User',
  phone: '',
  age_group: '18-59',
  is_logged_in: false
};

// Chat Image Attachment State
let chatAttachedImageDataUrl = null;
let chatAttachedImageFileName = null;

// Stepper Form Data
let stepperData = {
  age_group: '18-59',
  sex: 'Male',
  pregnant: 'Not applicable',
  symptoms: [],
  symptoms_text: '',
  duration: '<24h',
  severity: 'Mild',
  chronic_conditions: []
};

// -------------------------------------------------------------------
// 1. COMPREHENSIVE MULTILINGUAL TRANSLATION DICTIONARY (EN, HI, GU)
// -------------------------------------------------------------------
const I18N = {
  en: {
    nav_home: "Home",
    nav_chat: "Chat with Saarthi",
    nav_test: "Health Test",
    nav_med: "Scan Medicine",
    nav_emergency: "Helplines",
    hero_pill: "SCIENCE & WHO-LED PUBLIC HEALTH ASSISTANT",
    hero_title: "Know the root cause of your <span class='lime-text'>health symptoms</span>.",
    hero_subtitle: "Empathetic, multilingual health guidance inside strict safety guardrails. Talk with Saarthi, take a 2-minute clinical triage check, or scan your medicine strip.",
    btn_take_test: "TAKE THE HEALTH TEST™",
    btn_chat_saarthi: "Chat with Saarthi",
    btn_scan_medicine: "Scan Medicine Photo",
    trust_who: "WHO Grounded",
    trust_privacy: "No Data Selling",
    trust_speech: "Voice Spoken Guidance",
    trust_lang: "Hindi & Gujarati Ready",
    card_preview_badge: "✓ 24x7 Public Health Companion",
    card_saarthi_says: "Saarthi says:",
    feat_1: "Instant Multilingual Chat Assistant",
    feat_2: "Listen Aloud (Speech for Elders & Kids)",
    feat_3: "Upload Medicine Photo for Simple Details",
    feat_4: "Instant 108 / 112 Emergency Interception",
    f_chat_title: "Chat with Saarthi",
    f_chat_desc: "Talk naturally in Hindi, Gujarati, or English. Get empathetic guidance, supportive self-care, and warning signs.",
    f_test_title: "2-Min Guided Health Check",
    f_test_desc: "A step-by-step visual questionnaire with clear cards to determine your urgency level and care steps.",
    f_med_title: "Medicine Photo Explainer",
    f_med_desc: "Take a photo of any medicine tablet or syrup to understand what it is used for in simple everyday terms.",
    f_emerg_title: "Emergency Directory",
    f_emerg_desc: "Instant 1-tap call access to 108 Ambulance, 112 Emergency, 14416 Tele-MANAS, and 102 Maternal care.",
    quick_topics_label: "Common:",
    chip_fever: "Fever",
    chip_cough: "Cold & Cough",
    chip_headache: "Headache",
    chip_stomach: "Stomach Upset",
    chip_test: "Take Health Test",
    chip_scan: "Scan Medicine",
    chat_disclaimer: "🔒 Informational guidance only • Not a medical diagnosis • Call 108 in emergencies",
    chat_placeholder: "Type your symptoms (e.g. I have a sore throat and mild fever)...",
    stepper_topbar: "This health assessment is co-created with public health experts",
    btn_prev: "Previous",
    btn_exit: "Exit",
    step_1: "About You",
    step_2: "Symptoms",
    step_3: "Duration & Severity",
    step_4: "Health History",
    step_5: "Care Plan",
    q_who: "Who is this assessment for?",
    sub_who: "Select the age group of the person experiencing symptoms:",
    age_adult: "Adult (18–59 years)",
    age_adult_desc: "Working adult or young adult",
    age_toddler: "Young Child (1–5 years)",
    age_toddler_desc: "Toddler / young child",
    age_infant: "Infant (<1 year)",
    age_infant_desc: "Baby under 12 months",
    age_teen: "Child / Teen (6–17 years)",
    age_teen_desc: "School-age child or teenager",
    age_senior: "Senior (60+ years)",
    age_senior_desc: "Elderly family member",
    gender_title: "Gender",
    gender_male: "Male",
    gender_female: "Female",
    gender_other: "Other / Prefer not to say",
    pregnant_title: "Are you currently pregnant?",
    ans_no: "No",
    ans_yes: "Yes",
    btn_next_symptoms: "Next: Symptoms",
    q_symptoms: "What are your primary symptoms?",
    sub_symptoms: "Select all symptoms you are experiencing right now:",
    sym_fever: "Fever or Chills",
    sym_fever_desc: "Elevated body temperature, feeling hot/cold",
    sym_cold: "Cold & Runny Nose",
    sym_cold_desc: "Nasal congestion, watery nose, sneezing",
    sym_cough: "Cough & Sore Throat",
    sym_cough_desc: "Scratchy throat, dry or wet cough",
    sym_headache: "Headache",
    sym_headache_desc: "Head pain, forehead pressure, tension",
    sym_stomach: "Loose Motions / Vomiting",
    sym_stomach_desc: "Watery stools, nausea, upset stomach",
    sym_fatigue: "Fatigue & Body Aches",
    sym_fatigue_desc: "General weakness, muscle soreness",
    more_details_label: "Additional symptom details (optional):",
    btn_next_duration: "Next: Duration",
    q_duration: "How long and how severe?",
    sub_duration: "Select the duration and impact of your symptoms:",
    dur_title: "How long have you had symptoms?",
    dur_24h: "Less than 24 hours",
    dur_24h_desc: "Just started today or yesterday night",
    dur_3d: "1 to 3 days",
    dur_3d_desc: "Ongoing for a couple of days",
    dur_7d: "4 to 7 days",
    dur_7d_desc: "Almost a full week",
    dur_1w: "More than 1 week",
    dur_1w_desc: "Persistent symptoms lasting over 7 days",
    sev_title: "How severe is your discomfort?",
    sev_mild: "Mild Discomfort",
    sev_mild_desc: "Can easily do normal daily activities",
    sev_mod: "Moderate Impact",
    sev_mod_desc: "Noticeable discomfort, interferes with routine",
    sev_sev: "Severe Discomfort",
    sev_sev_desc: "Very uncomfortable, bed rest required",
    btn_next_history: "Next: Health History",
    q_history: "Any existing health conditions?",
    sub_history: "Select any chronic conditions you manage:",
    cond_diabetes: "Diabetes",
    cond_diabetes_desc: "Blood sugar condition",
    cond_heart: "Heart / Blood Pressure",
    cond_heart_desc: "Cardiovascular condition",
    cond_asthma: "Asthma or Respiratory",
    cond_asthma_desc: "Chronic breathing conditions",
    cond_none: "None / Generally Healthy",
    cond_none_desc: "No major chronic conditions",
    btn_gen_plan: "Generate Saarthi Care Plan ✨",
    btn_restart: "Start New Check",
    btn_continue_chat: "Continue in Chat with Saarthi",
    auth_modal_title: "Your Personal Health Profile",
    auth_headline: "Personalise your Saarthi health guidance",
    auth_sub: "Saved once on your device to remember your language, age group, and provide personalized answers.",
    auth_label_name: "Full Name *",
    auth_label_phone: "Phone Number (Optional)",
    auth_label_age: "Age Group",
    auth_btn_save: "Save & Continue to Saarthi →",
    auth_btn_skip: "Continue as Guest / Skip",
    med_modal_title: "Scan Medicine Photo",
    med_modal_sub: "Upload a photo of your tablet strip, syrup bottle, or box. Saarthi will explain what it is used for in simple, easy terms for your family.",
    med_click_photo: "Take or Upload Medicine Photo",
    med_formats: "Supports JPG, PNG (camera or gallery)",
    med_quick_samples: "Or tap a common medicine:",
    emerg_modal_title: "National Emergency Health Helplines",
    emerg_modal_sub: "Direct toll-free 24x7 emergency contacts across India. Tap any button to call directly:",
    btn_listen: "🔊 Listen to Guidance",
    btn_stop_listen: "⏹️ Stop Voice",
    nav_guidelines: "Guidelines",
    chip_guidelines: "Guidelines",
    settings_modal_title: "Settings & Profile",
    settings_name: "Your Name",
    settings_age: "Age Group",
    settings_language: "Language Preference",
    settings_fontsize: "Text Size (Accessibility)",
    settings_save_btn: "Save Settings",
    settings_clear_chat: "Clear Chat Conversation",
    guide_modal_title: "General Public Health Guidelines",
    guide_modal_sub: "Core wellness and preventive recommendations from WHO and MoHFW:"
  },
  hi: {
    nav_home: "होम",
    nav_chat: "सारथी से बात करें",
    nav_test: "हेल्थ टेस्ट",
    nav_med: "दवा फोटो जांच",
    nav_emergency: "हेल्पलाइन",
    hero_pill: "डब्ल्यूएचओ और विज्ञान आधारित सार्वजनिक स्वास्थ्य सहायक",
    hero_title: "अपने <span class='lime-text'>स्वास्थ्य लक्षणों</span> के मूल कारण को जानें।",
    hero_subtitle: "सहानुभूतिपूर्ण, बहुभाषी स्वास्थ्य मार्गदर्शन। सारथी से बात करें, 2 मिनट की स्वास्थ्य जांच करें या अपनी दवा के पत्ते की फोटो खींचकर आसान जानकारी पाएं।",
    btn_take_test: "हेल्थ टेस्ट शुरू करें™",
    btn_chat_saarthi: "सारथी चैट शुरू करें",
    btn_scan_medicine: "दवा की फोटो जांचें",
    trust_who: "डब्ल्यूएचओ प्रमाणित तथ्य",
    trust_privacy: "गोपनीयता सुरक्षित",
    trust_speech: "बोलकर सुनाने की सुविधा",
    trust_lang: "हिंदी और गुजराती उपलब्ध",
    card_preview_badge: "✓ 24x7 आपका स्वास्थ्य साथी",
    card_saarthi_says: "सारथी का संदेश:",
    feat_1: "तुरंत हिंदी में चैट परामर्श",
    feat_2: "बुजुर्गों और बच्चों के लिए बोलकर सुनाएं",
    feat_3: "दवा की फोटो से आसान भाषा में समझें",
    feat_4: "108 और 112 आपातकालीन सहायता तुरंत",
    f_chat_title: "सारथी से बात करें",
    f_chat_desc: "हिंदी में सामान्य रूप से बात करें। लक्षणों के आधार पर घरेलू देखभाल और चेतावनी संकेत जानें।",
    f_test_title: "2 मिनट की स्वास्थ्य जांच",
    f_test_desc: "चित्रों वाले आसान कार्ड के माध्यम से अपनी स्थिति और सही कदम जानें।",
    f_med_title: "दवा फोटो पहचान",
    f_med_desc: "दवा की गोली या सिरप की फोटो अपलोड करें और आसान हिंदी में समझें कि यह किस काम आती है।",
    f_emerg_title: "आपातकालीन नंबर",
    f_emerg_desc: "108 एम्बुलेंस, 112 आपातकालीन, 14416 टेली-मानस पर सीधे 1-टैप में कॉल करें।",
    quick_topics_label: "मुख्य विषय:",
    chip_fever: "बुखार",
    chip_cough: "सर्दी और खांसी",
    chip_headache: "सिरदर्द",
    chip_stomach: "पेट खराब",
    chip_test: "हेल्थ टेस्ट लें",
    chip_scan: "दवा जांचें",
    chat_disclaimer: "🔒 केवल सूचनात्मक मार्गदर्शन • चिकित्सीय निदान नहीं • आपातकाल में 108 पर कॉल करें",
    chat_placeholder: "अपने लक्षण लिखें (जैसे मुझे कल से हल्का बुखार और गले में खराश है)...",
    stepper_topbar: "यह स्वास्थ्य मूल्यांकन विशेषज्ञों द्वारा तैयार किया गया है",
    btn_prev: "पीछे जाएं",
    btn_exit: "बाहर निकलें",
    step_1: "आपके बारे में",
    step_2: "लक्षण",
    step_3: "अवधि और गंभीरता",
    step_4: "स्वास्थ्य इतिहास",
    step_5: "देखभाल योजना",
    q_who: "यह जांच किसके लिए है?",
    sub_who: "लक्षण महसूस कर रहे व्यक्ति का आयु वर्ग चुनें:",
    age_adult: "वयस्क (18–59 वर्ष)",
    age_adult_desc: "कामकाजी या युवा वयस्क",
    age_toddler: "छोटा बच्चा (1–5 वर्ष)",
    age_toddler_desc: "शिशु या छोटा बच्चा",
    age_infant: "नवजात (<1 वर्ष)",
    age_infant_desc: "12 महीने से कम का बच्चा",
    age_teen: "बच्चा / किशोर (6–17 वर्ष)",
    age_teen_desc: "स्कूल जाने वाला बच्चा या टीनेजर",
    age_senior: "वरिष्ठ नागरिक (60+ वर्ष)",
    age_senior_desc: "बुजुर्ग परिवारजन",
    gender_title: "लिंग",
    gender_male: "पुरुष",
    gender_female: "महिला",
    gender_other: "अन्य",
    pregnant_title: "क्या आप गर्भवती हैं?",
    ans_no: "नहीं",
    ans_yes: "हाँ",
    btn_next_symptoms: "अगला: लक्षण",
    q_symptoms: "आपके मुख्य लक्षण क्या हैं?",
    sub_symptoms: "अभी महसूस हो रहे सभी लक्षण चुनें:",
    sym_fever: "बुखार या ठंड लगना",
    sym_fever_desc: "शरीर का बढ़ा तापमान, कंपकंपी",
    sym_cold: "सर्दी और बहती नाक",
    sym_cold_desc: "नाक बंद होना, छींकें आना",
    sym_cough: "खांसी और गले में खराश",
    sym_cough_desc: "सूखी या कफ वाली खांसी",
    sym_headache: "सिरदर्द",
    sym_headache_desc: "माथे में दर्द या भारीपन",
    sym_stomach: "दस्त / उल्टी",
    sym_stomach_desc: "पतले दस्त, जी मिचलाना",
    sym_fatigue: "कमजोरी और बदन दर्द",
    sym_fatigue_desc: "थकान, मांसपेशियों में दर्द",
    more_details_label: "अन्य विवरण (वैकल्पिक):",
    btn_next_duration: "अगला: अवधि",
    q_duration: "कितने समय से और कितना गंभीर?",
    sub_duration: "लक्षणों का समय और असर चुनें:",
    dur_title: "यह समस्या कितने समय से है?",
    dur_24h: "24 घंटे से कम",
    dur_24h_desc: "आज या कल रात से शुरू हुआ",
    dur_3d: "1 से 3 दिन",
    dur_3d_desc: "कुछ दिनों से लगातार",
    dur_7d: "4 से 7 दिन",
    dur_7d_desc: "लगभग एक सप्ताह",
    dur_1w: "1 सप्ताह से अधिक",
    dur_1w_desc: "लंबे समय से बना हुआ",
    sev_title: "तकलीफ कितनी गंभीर है?",
    sev_mild: "हल्की तकलीफ",
    sev_mild_desc: "दैनिक काम आसानी से कर सकते हैं",
    sev_mod: "मध्यम तकलीफ",
    sev_mod_desc: "असुविधाजनक, कामकाज पर असर",
    sev_sev: "गंभीर तकलीफ",
    sev_sev_desc: "बहुत अधिक कष्ट, बिस्तर पर आराम जरूरी",
    btn_next_history: "अगला: स्वास्थ्य इतिहास",
    q_history: "क्या पहले से कोई बीमारी है?",
    sub_history: "अपने दीर्घकालिक रोग चुनें:",
    cond_diabetes: "डायबिटीज (शुगर)",
    cond_diabetes_desc: "रक्त शर्करा की समस्या",
    cond_heart: "हार्ट या ब्लड प्रेशर",
    cond_heart_desc: "हृदय या बीपी की समस्या",
    cond_asthma: "अस्थमा या सांस की बीमारी",
    cond_asthma_desc: "सांस लेने में दिक्कत",
    cond_none: "कोई नहीं / सामान्य स्वस्थ",
    cond_none_desc: "कोई पुरानी बीमारी नहीं",
    btn_gen_plan: "सारथी देखभाल योजना बनाएं ✨",
    btn_restart: "नई जांच शुरू करें",
    btn_continue_chat: "सारथी चैट में बात जारी रखें",
    auth_modal_title: "आपकी स्वास्थ्य प्रोफ़ाइल",
    auth_headline: "सारथी को अपने बारे में बताएं",
    auth_sub: "यह जानकारी आपके फोन में सुरक्षित रहेगी ताकि आपको सही भाषा और उम्र के अनुसार सलाह मिल सके।",
    auth_label_name: "पूरा नाम *",
    auth_label_phone: "फोन नंबर (वैकल्पिक)",
    auth_label_age: "आयु वर्ग",
    auth_btn_save: "सहेजें और आगे बढ़ें →",
    auth_btn_skip: "अतिथि के रूप में जारी रखें",
    med_modal_title: "दवा की फोटो पहचानें",
    med_modal_sub: "अपनी दवा की गोली या सिरप के पत्ते की फोटो अपलोड करें। सारथी आसान भाषा में बताएगा कि यह किस काम आती है।",
    med_click_photo: "फोटो खींचें या अपलोड करें",
    med_formats: "कैमरा या गैलरी से फोटो लें",
    med_quick_samples: "या सामान्य दवाओं में से चुनें:",
    emerg_modal_title: "राष्ट्रीय आपातकालीन स्वास्थ्य नंबर",
    emerg_modal_sub: "भारत भर में 24x7 निःशुल्क आपातकालीन संपर्क। सीधे कॉल करने के लिए बटन दबाएं:",
    btn_listen: "🔊 बोलकर सुनें",
    btn_stop_listen: "⏹️ आवाज रोकें",
    nav_guidelines: "दिशानिर्देश",
    chip_guidelines: "दिशानिर्देश",
    settings_modal_title: "सेटिंग्स और प्रोफ़ाइल",
    settings_name: "आपका नाम",
    settings_age: "आयु वर्ग",
    settings_language: "भाषा का चयन",
    settings_fontsize: "अक्षर का आकार (बुजुर्गों के लिए)",
    settings_save_btn: "सेटिंग्स सुरक्षित करें",
    settings_clear_chat: "चैट बातचीत साफ़ करें",
    guide_modal_title: "सामान्य सार्वजनिक स्वास्थ्य दिशानिर्देश",
    guide_modal_sub: "विश्व स्वास्थ्य संगठन (WHO) और स्वास्थ्य मंत्रालय (MoHFW) द्वारा अनुशंसित स्वास्थ्य नियम:"
  },
  gu: {
    nav_home: "હોમ",
    nav_chat: "સારથી સાથે ચેટ",
    nav_test: "હેલ્થ ટેસ્ટ",
    nav_med: "દવા ફોટો સ્કેન",
    nav_emergency: "હેલ્પલાઇન",
    hero_pill: "ડબ્લ્યુએચઓ અને વિજ્ઞાન આધારિત જાહેર આરોગ્ય સહાયક",
    hero_title: "તમારા <span class='lime-text'>આરોગ્ય લક્ષણો</span> નું મૂળ કારણ જાણો.",
    hero_subtitle: "સહાનુભૂતિપૂર્ણ, બહુભાષી માર્ગદર્શન. સારથી સાથે વાત કરો, ૨ મિનિટની હેલ્થ તપાસ કરો અથવા તમારી દવાની ફોટો પાડી સરળ માહિતી મેળવો.",
    btn_take_test: "હેલ્થ ટેસ્ટ શરૂ કરો™",
    btn_chat_saarthi: "સારથી સાથે વાત કરો",
    btn_scan_medicine: "દવાની ફોટો સ્કેન કરો",
    trust_who: "WHO પ્રમાણિત",
    trust_privacy: "ડેટા સલામત",
    trust_speech: "અવાજ દ્વારા સાંભળો",
    trust_lang: "ગુજરાતી અને હિન્દી તૈયાર",
    card_preview_badge: "✓ ૨૪x૭ તમારો સ્વાસ્થ્ય મિત્ર",
    card_saarthi_says: "સારથીનો સંદેશ:",
    feat_1: "તરત જ ગુજરાતીમાં વાતચીત",
    feat_2: "વડીલો અને બાળકો માટે બોલીને સંભળાવે",
    feat_3: "દવાની ફોટો પરથી સરળ સમજૂતી",
    feat_4: "૧૦૮ અને ૧૧૨ કટોકટી સેવા તાત્કાલિક",
    f_chat_title: "સારથી સાથે ચેટ કરો",
    f_chat_desc: "ગુજરાતીમાં સહજતાથી વાત કરો. ઘરેલું કાળજી અને સાવચેતીના લક્ષણો જાણો.",
    f_test_title: "૨ મિનિટ હેલ્થ ચેક",
    f_test_desc: "સરળ કાર્ડ્સ દ્વારા તમારી સ્થિતિ અને સલામત પગલાં સમજો.",
    f_med_title: "દવા ફોટો સમજૂતી",
    f_med_desc: "દવાની ગોળી કે સિરપની ફોટો પાડીને જાણો કે તે શેના માટે વપરાય છે.",
    f_emerg_title: "કટોકટી હેલ્પલાઇન",
    f_emerg_desc: "૧૦૮ એમ્બ્યુલન્સ, ૧૧૨ ઇમરજન્સી અને ૧૪૪૧૬ ટેલી-માનસ પર ૧-ટેપમાં કોલ કરો.",
    quick_topics_label: "મુખ્ય વિષયો:",
    chip_fever: "તાવ",
    chip_cough: "શરદી-ખાંસી",
    chip_headache: "માથાનો દુખાવો",
    chip_stomach: "પેટની તકલીફ",
    chip_test: "ટેસ્ટ શરૂ કરો",
    chip_scan: "દવા તપાસો",
    chat_disclaimer: "🔒 માત્ર માહિતી માટે • તબીબી નિદાન નથી • કટોકટીમાં ૧૦૮ પર કોલ કરો",
    chat_placeholder: "તમારા લક્ષણો લખો (જેમ કે મને ગઈકાલથી હળવો તાવ છે)...",
    stepper_topbar: "આ આરોગ્ય મૂલ્યાંકન નિષ્ણાતો દ્વારા તૈયાર કરાયું છે",
    btn_prev: "પાછળ જાઓ",
    btn_exit: "બહાર નીકળો",
    step_1: "તમારા વિશે",
    step_2: "લક્ષણો",
    step_3: "સમય અને ગંભીરતા",
    step_4: "ઇતિહાસ",
    step_5: "સંભાળ યોજના",
    q_who: "આ તપાસ કોના માટે છે?",
    sub_who: "લક્ષણો અનુભવતા વ્યક્તિનું વયજૂથ પસંદ કરો:",
    age_adult: "પુખ્ત (૧૮–૫૯ વર્ષ)",
    age_adult_desc: "કામ કરતા અથવા યુવાન",
    age_toddler: "નાનું બાળક (૧–૫ વર્ષ)",
    age_toddler_desc: "નાનું બાળક",
    age_infant: "શિશુ (<૧ વર્ષ)",
    age_infant_desc: "૧૨ મહિનાથી નાનું બાળક",
    age_teen: "કિશોર (૬–૧૭ વર્ષ)",
    age_teen_desc: "શાળાએ જતું બાળક કે ટીનેજર",
    age_senior: "વરિષ્ઠ નાગરિક (૬૦+ વર્ષ)",
    age_senior_desc: "ઘરના વડીલ",
    gender_title: "જાતિ",
    gender_male: "પુરુષ",
    gender_female: "સ્ત્રી",
    gender_other: "અન્ય",
    pregnant_title: "શું તમે સગર્ભા છો?",
    ans_no: "ના",
    ans_yes: "હા",
    btn_next_symptoms: "આગળ: લક્ષણો",
    q_symptoms: "તમારા મુખ્ય લક્ષણો શું છે?",
    sub_symptoms: "અત્યારે થતા તમામ લક્ષણો પસંદ કરો:",
    sym_fever: "તાવ કે ધ્રુજારી",
    sym_fever_desc: "શરીરનું તાપમાન વધવું",
    sym_cold: "શરદી અને વહેતું નાક",
    sym_cold_desc: "નાક બંધ થવું, છીંકો આવવી",
    sym_cough: "ઉધરસ અને ગળામાં દુખાવો",
    sym_cough_desc: "સૂકી કે કફવાળી ખાંસી",
    sym_headache: "માથાનો દુખાવો",
    sym_headache_desc: "માથામાં ભાર લાગવો",
    sym_stomach: "ઝાડા / ઉલટી",
    sym_stomach_desc: "પાતળા ઝાડા, ઉબકા આવવા",
    sym_fatigue: "થાક અને શરીરનો દુખાવો",
    sym_fatigue_desc: "અશક્તિ, સ્નાયુઓમાં દુખાવો",
    more_details_label: "અન્ય વિગત (વૈકલ્પિક):",
    btn_next_duration: "આગળ: સમય",
    q_duration: "કેટલા સમયથી અને કેટલું ગંભીર?",
    sub_duration: "લક્ષણોનો સમયગાળો પસંદ કરો:",
    dur_title: "આ તકલીફ કેટલા સમયથી છે?",
    dur_24h: "૨૪ કલાકથી ઓછો",
    dur_24h_desc: "આજે કે ગઈકાલે શરૂ થયું",
    dur_3d: "૧ થી ૩ દિવસ",
    dur_3d_desc: "થોડા દિવસોથી ચાલુ છે",
    dur_7d: "૪ થી ૭ દિવસ",
    dur_7d_desc: "લગભગ એક અઠવાડિયું",
    dur_1w: "૧ અઠવાડિયાથી વધુ",
    dur_1w_desc: "લાંબા સમયથી છે",
    sev_title: "તકલીફ કેટલી ગંભીર છે?",
    sev_mild: "હળવી તકલીફ",
    sev_mild_desc: "રોજિંદા કામ સરળતાથી થઈ શકે",
    sev_mod: "મધ્યમ તકલીફ",
    sev_mod_desc: "કામકાજમાં અડચણરૂપ",
    sev_sev: "ગંભીર તકલીફ",
    sev_sev_desc: "અતિશય કષ્ટ, આરામ જરૂરી",
    btn_next_history: "આગળ: ઇતિહાસ",
    q_history: "શું પહેલેથી કોઈ બીમારી છે?",
    sub_history: "તમારી બીમારીઓ પસંદ કરો:",
    cond_diabetes: "ડાયાબિટીસ (શુગર)",
    cond_diabetes_desc: "બ્લડ શુગરની તકલીફ",
    cond_heart: "હૃદય કે બ્લડ પ્રેશર",
    cond_heart_desc: "બીપી કે હૃદયની બીમારી",
    cond_asthma: "અસ્થમા કે શ્વાસની તકલીફ",
    cond_asthma_desc: "શ્વાસ લેવામાં તકલીફ",
    cond_none: "કોઈ નહીં / સામાન્ય તંદુરસ્ત",
    cond_none_desc: "કોઈ જૂની બીમારી નથી",
    btn_gen_plan: "સારથી સંભાળ યોજના બનાવો ✨",
    btn_restart: "નવી તપાસ કરો",
    btn_continue_chat: "સારથી ચેટમાં વાત ચાલુ રાખો",
    auth_modal_title: "તમારી હેલ્થ પ્રોફાઇલ",
    auth_headline: "સારથીને તમારા વિશે જણાવો",
    auth_sub: "આ માહિતી તમારા ફોનમાં સંગ્રહિત રહેશે જેથી યોગ્ય ભાષા અને વય અનુસાર સલાહ મળી શકે.",
    auth_label_name: "પૂરું નામ *",
    auth_label_phone: "ફોન નંબર (વૈકલ્પિક)",
    auth_label_age: "વયજૂથ",
    auth_btn_save: "સાચવો અને આગળ વધો →",
    auth_btn_skip: "ગેસ્ટ તરીકે આગળ વધો",
    med_modal_title: "દવા ફોટો સ્કેન કરો",
    med_modal_sub: "તમારી ગોળી કે સિરપની ફોટો અપલોડ કરો. સારથી સરળ ગુજરાતીમાં સમજાવશે કે તે શેના માટે છે.",
    med_click_photo: "ફોટો પાડો અથવા અપલોડ કરો",
    med_formats: "કેમેરા કે ગેલેરીમાંથી ફોટો લો",
    med_quick_samples: "અથવા જાણીતી દવા પસંદ કરો:",
    emerg_modal_title: "રાષ્ટ્રીય કટોકટી આરોગ્ય નંબર",
    emerg_modal_sub: "સમગ્ર ભારતમાં ૨૪x૭ મફત સેવાઓ. સીધો કોલ કરવા માટે બટન દબાવો:",
    btn_listen: "🔊 સાંભળો",
    btn_stop_listen: "⏹️ અવાજ બંધ કરો",
    nav_guidelines: "માર્ગદર્શિકા",
    chip_guidelines: "માર્ગદર્શિકા",
    settings_modal_title: "સેટિંગ્સ અને પ્રોફાઇલ",
    settings_name: "તમારું નામ",
    settings_age: "ઉંમર જૂથ",
    settings_language: "ભાષા પસંદગી",
    settings_fontsize: "અક્ષરનું કદ (મોટું લખાણ)",
    settings_save_btn: "સેટિંગ્સ સેવ કરો",
    settings_clear_chat: "ચેટ સાફ કરો",
    guide_modal_title: "સામાન્ય જાહેર આરોગ્ય માર્ગદર્શિકા",
    guide_modal_sub: "વિશ્વ આરોગ્ય સંસ્થા (WHO) અને આરોગ્ય મંત્રાલય દ્વારા સામાન્ય સ્વાસ્થ્ય નિયમો:"
  }
};

// -------------------------------------------------------------------
// 2. INITIALIZATION & TRANSLATION ENGINE
// -------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  loadStoredUser();
  const savedFs = localStorage.getItem('swasthya_saarthi_fontsize');
  if (savedFs) {
    toggleFontSize(savedFs);
  }
  applyLanguageTranslations(currentLanguage);
  setDefaultStepperSelections();
});

function onLanguageSelect() {
  currentLanguage = document.getElementById('lang-select').value;
  applyLanguageTranslations(currentLanguage);
  renderGuidelinesBody();
  if (currentView === 'chat') {
    loadChatWelcome(true);
  }
}

function applyLanguageTranslations(lang) {
  const dict = I18N[lang] || I18N.en;

  // Translate all [data-i18n] elements
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (dict[key]) {
      el.innerHTML = dict[key];
    }
  });

  // Translate placeholders
  const chatInput = document.getElementById('chat-user-input');
  if (chatInput && dict.chat_placeholder) {
    chatInput.placeholder = dict.chat_placeholder;
  }

  // Update dynamic guidelines
  renderGuidelinesBody();
}

// View Navigation (Landing vs Chat vs Stepper)
function showView(viewName) {
  currentView = viewName;
  const isLanding = viewName === 'landing';
  const isChat = viewName === 'chat';
  const isStepper = viewName === 'stepper';

  document.getElementById('section-landing').style.display = isLanding ? 'block' : 'none';
  document.getElementById('main-content-app').style.display = isLanding ? 'none' : 'block';

  document.getElementById('section-chat').style.display = isChat ? 'flex' : 'none';
  document.getElementById('section-stepper').style.display = isStepper ? 'block' : 'none';

  document.getElementById('nav-btn-home').classList.toggle('active', isLanding);
  document.getElementById('nav-btn-chat').classList.toggle('active', isChat);
  document.getElementById('nav-btn-stepper').classList.toggle('active', isStepper);

  if (isChat && chatHistory.length === 0) {
    loadChatWelcome();
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// -------------------------------------------------------------------
// 3. USER AUTHENTICATION & PERSISTENCE
// -------------------------------------------------------------------
function loadStoredUser() {
  try {
    const saved = localStorage.getItem('swasthya_saarthi_user');
    if (saved) {
      currentUser = JSON.parse(saved);
      if (currentUser.language) {
        currentLanguage = currentUser.language;
        document.getElementById('lang-select').value = currentLanguage;
      }
      updateUserBadge();
    }
  } catch (e) {
    console.error('Error loading stored user', e);
  }
}

function updateUserBadge() {
  const badgeEl = document.getElementById('user-display-name');
  if (currentUser.is_logged_in && currentUser.name && currentUser.name !== 'User') {
    const salutation = currentLanguage === 'hi' ? 'नमस्ते' : (currentLanguage === 'gu' ? 'નમસ્તે' : 'Hello');
    badgeEl.innerText = `👤 ${salutation}, ${currentUser.name.split(' ')[0]}`;
  } else {
    badgeEl.innerText = currentLanguage === 'hi' ? 'साइन इन' : (currentLanguage === 'gu' ? 'સાઇન ઇન' : 'Sign In');
  }
}

function openAuthModal() {
  document.getElementById('modal-auth').style.display = 'flex';
  if (currentUser.name && currentUser.name !== 'User') {
    document.getElementById('auth-name').value = currentUser.name;
    document.getElementById('auth-phone').value = currentUser.phone || '';
    document.getElementById('auth-age').value = currentUser.age_group || '18-59';
  }
}

function closeAuthModal() {
  document.getElementById('modal-auth').style.display = 'none';
}

function handleAuthSubmit(e) {
  e.preventDefault();
  const name = document.getElementById('auth-name').value.trim();
  const phone = document.getElementById('auth-phone').value.trim();
  const age = document.getElementById('auth-age').value;

  currentUser = {
    name: name || 'User',
    phone: phone,
    age_group: age,
    language: currentLanguage,
    is_logged_in: true
  };

  localStorage.setItem('swasthya_saarthi_user', JSON.stringify(currentUser));
  updateUserBadge();
  closeAuthModal();

  // If in chat, or opening chat, reload chat welcome with their personalized name!
  showView('chat');
  loadChatWelcome(true);
}

function closeModalOnBackdrop(e, modalId) {
  if (e.target && e.target.id === modalId) {
    document.getElementById(modalId).style.display = 'none';
  }
}

// -------------------------------------------------------------------
// 4. TEXT-TO-SPEECH (Listen Aloud Feature for All Ages)
// -------------------------------------------------------------------
function toggleSpeech(text, btnEl) {
  if (!('speechSynthesis' in window)) {
    alert("Audio speech is not supported in this browser.");
    return;
  }

  // If already speaking this text, stop it
  if (isSpeaking) {
    window.speechSynthesis.cancel();
    isSpeaking = false;
    document.querySelectorAll('.btn-speech-listen').forEach(b => {
      b.classList.remove('speaking');
      const dict = I18N[currentLanguage] || I18N.en;
      b.innerHTML = `🔊 ${dict.btn_listen}`;
    });
    return;
  }

  window.speechSynthesis.cancel(); // Reset any existing speech

  // Strip html tags and markdown for clean pronunciation
  const cleanSpeechText = text
    .replace(/<[^>]*>/g, ' ')
    .replace(/\*\*/g, '')
    .replace(/[•#_*]/g, '')
    .replace(/\s+/g, ' ')
    .trim();

  currentSpeechUtterance = new SpeechSynthesisUtterance(cleanSpeechText);
  
  // Set language voice
  if (currentLanguage === 'hi') {
    currentSpeechUtterance.lang = 'hi-IN';
  } else if (currentLanguage === 'gu') {
    currentSpeechUtterance.lang = 'gu-IN';
  } else {
    currentSpeechUtterance.lang = 'en-IN';
  }

  currentSpeechUtterance.rate = 0.95; // slightly slower for elderly/clear comprehension

  currentSpeechUtterance.onstart = () => {
    isSpeaking = true;
    if (btnEl) {
      btnEl.classList.add('speaking');
      const dict = I18N[currentLanguage] || I18N.en;
      btnEl.innerHTML = `⏹️ ${dict.btn_stop_listen}`;
    }
  };

  currentSpeechUtterance.onend = () => {
    isSpeaking = false;
    if (btnEl) {
      btnEl.classList.remove('speaking');
      const dict = I18N[currentLanguage] || I18N.en;
      btnEl.innerHTML = `🔊 ${dict.btn_listen}`;
    }
  };

  currentSpeechUtterance.onerror = () => {
    isSpeaking = false;
    if (btnEl) {
      btnEl.classList.remove('speaking');
      const dict = I18N[currentLanguage] || I18N.en;
      btnEl.innerHTML = `🔊 ${dict.btn_listen}`;
    }
  };

  window.speechSynthesis.speak(currentSpeechUtterance);
}

// -------------------------------------------------------------------
// 5. CONVERSATIONAL CHATBOT (Swasthya Saarthi)
// -------------------------------------------------------------------
async function loadChatWelcome(resetHistory = false) {
  if (resetHistory) {
    chatHistory = [];
    document.getElementById('chat-messages-container').innerHTML = '';
  }

  try {
    const res = await fetch(`/api/chat/welcome?language=${currentLanguage}`);
    const data = await res.json();
    let welcomeText = data.text;

    // Personalize with user name if available
    if (currentUser && currentUser.is_logged_in && currentUser.name && currentUser.name !== 'User') {
      const firstName = currentUser.name.split(' ')[0];
      if (currentLanguage === 'hi') {
        welcomeText = welcomeText.replace('नमस्ते!', `नमस्ते ${firstName} जी! 🙏`);
      } else if (currentLanguage === 'gu') {
        welcomeText = welcomeText.replace('નમસ્તે!', `નમસ્તે ${firstName}! 🙏`);
      } else {
        welcomeText = welcomeText.replace('Namaste!', `Namaste ${firstName}! 🙏`);
      }
    }

    renderAssistantMessage(welcomeText, data.quick_replies);
  } catch (err) {
    const dict = I18N[currentLanguage] || I18N.en;
    let fallbackText = "Namaste! I am Swasthya Saarthi. How are you feeling today?";
    if (currentUser && currentUser.is_logged_in && currentUser.name && currentUser.name !== 'User') {
      fallbackText = `Namaste ${currentUser.name.split(' ')[0]}! I am Swasthya Saarthi. How are you feeling today?`;
    }
    renderAssistantMessage(fallbackText, ["Fever 🌡️", "Cough 🤧"]);
  }
}

function sendQuickMessage(text) {
  showView('chat');
  document.getElementById('chat-user-input').value = text;
  handleUserChatSubmit();
}

// Chat Image Attachment Handlers
function triggerChatImageUpload() {
  const fileInput = document.getElementById('chat-file-input');
  if (fileInput) fileInput.click();
}

function handleChatImageSelected(e) {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(evt) {
    chatAttachedImageDataUrl = evt.target.result;
    chatAttachedImageFileName = file.name;

    const bar = document.getElementById('chat-attached-image-bar');
    const thumb = document.getElementById('chat-attached-image-thumb');
    const nameLabel = document.getElementById('chat-attached-image-name');

    if (bar && thumb && nameLabel) {
      thumb.src = chatAttachedImageDataUrl;
      nameLabel.innerText = file.name.length > 25 ? file.name.substring(0, 22) + '...' : file.name;
      bar.style.display = 'flex';
    }
  };
  reader.readAsDataURL(file);
}

function cancelChatImageAttachment() {
  chatAttachedImageDataUrl = null;
  chatAttachedImageFileName = null;
  const bar = document.getElementById('chat-attached-image-bar');
  if (bar) bar.style.display = 'none';
  const fileInput = document.getElementById('chat-file-input');
  if (fileInput) fileInput.value = '';
}

async function handleUserChatSubmit(e) {
  if (e) e.preventDefault();

  const inputEl = document.getElementById('chat-user-input');
  const userText = inputEl.value.trim();
  const hasImage = !!chatAttachedImageDataUrl;

  if (!userText && !hasImage) return;

  const activeImage = chatAttachedImageDataUrl;
  const activeFileName = chatAttachedImageFileName;
  cancelChatImageAttachment();

  inputEl.value = '';
  inputEl.focus();

  // Render user message (displaying image thumbnail if attached)
  const defaultText = currentLanguage === 'hi' 
    ? 'कृपया इस दवा की जानकारी दें 💊' 
    : (currentLanguage === 'gu' ? 'કૃપા કરીને આ દવા સમજાવો 💊' : 'Please explain this medicine photo 💊');
  
  renderUserMessage(userText || defaultText, activeImage);

  const typingId = showTypingIndicator();

  // If user attached an image, analyze medicine directly inside the conversation
  if (hasImage) {
    try {
      const res = await fetch('/api/medicine-scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filename: activeFileName || 'medicine.jpg',
          text: userText || activeFileName || 'medicine',
          language: currentLanguage
        })
      });

      const data = await res.json();
      removeTypingIndicator(typingId);

      let introSalutation = "";
      if (currentUser && currentUser.is_logged_in && currentUser.name && currentUser.name !== 'User') {
        const fn = currentUser.name.split(' ')[0];
        introSalutation = currentLanguage === 'hi' ? `**${fn} जी, ** ` : (currentLanguage === 'gu' ? `**${fn}, ** ` : `**${fn}, ** `);
      }

      let formattedMedReply = "";
      if (currentLanguage === 'hi') {
        formattedMedReply = `${introSalutation}यहाँ **${data.name}** की सरल जानकारी है:\n\n` +
          `• **💊 उपयोग:** ${data.used_for}\n` +
          `• **💧 लेने का तरीका:** ${data.how_to_use}\n` +
          `• **⚠️ सावधानी:** ${data.simple_tips}\n\n` +
          `*${data.disclaimer}*`;
      } else if (currentLanguage === 'gu') {
        formattedMedReply = `${introSalutation}અહીં **${data.name}** વિશે સરળ માહિતી છે:\n\n` +
          `• **💊 ઉપયોગ:** ${data.used_for}\n` +
          `• **💧 લેવાની રીત:** ${data.how_to_use}\n` +
          `• **⚠️ સાવચેતી:** ${data.simple_tips}\n\n` +
          `*${data.disclaimer}*`;
      } else {
        formattedMedReply = `${introSalutation}Here is the simple breakdown for **${data.name}**:\n\n` +
          `• **💊 Used for:** ${data.used_for}\n` +
          `• **💧 How it is usually taken:** ${data.how_to_use}\n` +
          `• **⚠️ Precautions:** ${data.simple_tips}\n\n` +
          `*${data.disclaimer}*`;
      }

      renderAssistantMessage(formattedMedReply, ["Ask side effects", "How many days?", "When to see doctor 🩺"]);
      chatHistory.push({ role: 'user', content: userText || `[Attached Photo: ${activeFileName}]` });
      chatHistory.push({ role: 'assistant', content: formattedMedReply });
      return;
    } catch (err) {
      removeTypingIndicator(typingId);
      renderAssistantMessage("Could not analyze the uploaded image. Please ensure good lighting or type the medicine name.", ["Try again"]);
      return;
    }
  }

  // Standard conversational route with user_name context
  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: userText,
        history: chatHistory.slice(-6),
        language: currentLanguage,
        context: {
          user_name: (currentUser && currentUser.is_logged_in && currentUser.name && currentUser.name !== 'User') ? currentUser.name : ''
        }
      })
    });

    const data = await res.json();
    removeTypingIndicator(typingId);

    renderAssistantMessage(data.reply, data.quick_replies, data.alert_card);

    chatHistory.push({ role: 'user', content: userText });
    chatHistory.push({ role: 'assistant', content: data.reply });

  } catch (err) {
    removeTypingIndicator(typingId);
    renderAssistantMessage(
      "I encountered a temporary connection glitch. If your symptoms are severe, please call 108 immediately.",
      ["Try again", "Take Guided Test 📋"]
    );
  }
}

function renderUserMessage(text, imageSrc = null) {
  const container = document.getElementById('chat-messages-container');
  const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  let imageHtml = '';
  if (imageSrc) {
    imageHtml = `<img src="${imageSrc}" style="max-width: 200px; max-height: 150px; border-radius: 8px; margin-bottom: 8px; display: block; object-fit: contain; background: #fff; border: 1px solid rgba(0,0,0,0.08);" alt="Uploaded Photo">`;
  }

  const row = document.createElement('div');
  row.className = 'msg-row user';
  row.innerHTML = `
    <div class="msg-avatar">👤</div>
    <div>
      <div class="msg-bubble">
        ${imageHtml}
        ${escapeHtml(text)}
      </div>
      <span class="msg-time">${timeStr}</span>
    </div>
  `;
  container.appendChild(row);
  scrollToBottom();
}

function renderAssistantMessage(text, quickReplies = [], alertCard = null) {
  const container = document.getElementById('chat-messages-container');
  const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const dict = I18N[currentLanguage] || I18N.en;

  const row = document.createElement('div');
  row.className = 'msg-row assistant';

  let alertCardHtml = '';
  if (alertCard) {
    const isCrisis = alertCard.type === 'crisis';
    let actionsHtml = '';
    (alertCard.actions || []).forEach(act => {
      actionsHtml += `<a href="tel:${act.phone}" class="btn-call ${isCrisis ? 'crisis' : ''}">📞 ${escapeHtml(act.label)}</a>`;
    });

    alertCardHtml = `
      <div class="alert-card-container ${isCrisis ? 'crisis' : ''}">
        <div class="alert-card-title">${escapeHtml(alertCard.title)}</div>
        <div class="alert-card-message">${escapeHtml(alertCard.message)}</div>
        <div class="alert-card-actions">${actionsHtml}</div>
      </div>
    `;
  }

  let quickRepliesHtml = '';
  if (quickReplies && quickReplies.length > 0) {
    quickRepliesHtml = '<div class="quick-replies-container">';
    quickReplies.forEach(qr => {
      quickRepliesHtml += `<button type="button" class="quick-reply-pill" onclick="sendQuickMessage('${escapeHtml(qr)}')">${escapeHtml(qr)}</button>`;
    });
    quickRepliesHtml += '</div>';
  }

  const formattedText = formatMarkdown(text);
  const speechId = 'speech-' + Date.now();

  row.innerHTML = `
    <div class="msg-avatar">🩺</div>
    <div style="flex: 1;">
      <div class="msg-bubble">
        ${formattedText}
        ${alertCardHtml}
        <div class="msg-actions-bar">
          <button class="btn-speech-listen" id="${speechId}">
            🔊 ${dict.btn_listen}
          </button>
          <span style="font-size: 0.68rem; color: #94a3b8;">${timeStr}</span>
        </div>
      </div>
      ${quickRepliesHtml}
    </div>
  `;

  container.appendChild(row);

  // Attach speech listener
  const btnSpeech = row.querySelector(`#${speechId}`);
  if (btnSpeech) {
    btnSpeech.onclick = () => toggleSpeech(text, btnSpeech);
  }

  scrollToBottom();
}

function showTypingIndicator() {
  const container = document.getElementById('chat-messages-container');
  const id = 'typing-' + Date.now();
  const row = document.createElement('div');
  row.className = 'msg-row assistant';
  row.id = id;
  row.innerHTML = `
    <div class="msg-avatar">🩺</div>
    <div class="msg-bubble" style="padding: 10px 14px;">
      <div class="typing-dots">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>
  `;
  container.appendChild(row);
  scrollToBottom();
  return id;
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function scrollToBottom() {
  const container = document.getElementById('chat-messages-container');
  container.scrollTop = container.scrollHeight;
}

// -------------------------------------------------------------------
// 6. MEDICINE PHOTO SCANNER & EXPLAINER (For All Ages)
// -------------------------------------------------------------------
function openMedicineModal() {
  document.getElementById('modal-medicine').style.display = 'flex';
}

function closeMedicineModal() {
  document.getElementById('modal-medicine').style.display = 'none';
}

function handleMedicineFile(e) {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(evt) {
    const dataUrl = evt.target.result;

    const placeholder = document.getElementById('med-upload-placeholder');
    const preview = document.getElementById('med-upload-preview');
    const previewImg = document.getElementById('med-preview-img');
    const previewFilename = document.getElementById('med-preview-filename');

    if (placeholder) placeholder.style.display = 'none';
    if (preview) preview.style.display = 'block';
    if (previewImg) previewImg.src = dataUrl;
    if (previewFilename) previewFilename.innerText = file.name;

    analyzeMedicine(file.name);
  };
  reader.readAsDataURL(file);
}

function analyzeMedicineFromManualInput() {
  const manualInput = document.getElementById('med-manual-input');
  if (!manualInput) return;
  const val = manualInput.value.trim();
  if (!val) {
    alert("Please enter a medicine or symptom name (e.g. Paracetamol, Dolo, Pan 40).");
    return;
  }
  analyzeMedicine(val);
}

async function analyzeMedicine(medicineQuery) {
  const resultDiv = document.getElementById('medicine-analysis-result');
  resultDiv.style.display = 'block';
  resultDiv.innerHTML = '<div style="text-align: center; padding: 20px;">Analyzing medicine in simple terms... ⏳</div>';

  try {
    const res = await fetch('/api/medicine-scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filename: medicineQuery,
        text: medicineQuery,
        language: currentLanguage
      })
    });

    const data = await res.json();
    renderMedicineExplanation(data);
  } catch (err) {
    resultDiv.innerHTML = '<div style="color: #dc2626; padding: 12px;">Could not analyze medicine. Please try again.</div>';
  }
}

function renderMedicineExplanation(data) {
  const resultDiv = document.getElementById('medicine-analysis-result');
  const dict = I18N[currentLanguage] || I18N.en;

  const spokenText = `${data.name}. Used for: ${data.used_for}. How to take: ${data.how_to_use}. Precautions: ${data.simple_tips}`;

  resultDiv.innerHTML = `
    <div class="medicine-result-card">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
        <h3 style="font-size: 1.1rem; font-weight: 800; color: #0f172a;">
          ${data.icon} ${escapeHtml(data.name)}
        </h3>
        <button class="btn-speech-listen" id="btn-med-listen">
          🔊 ${dict.btn_listen}
        </button>
      </div>

      <div style="font-size: 0.85rem; color: #1e293b; margin-bottom: 8px;">
        <strong>💊 What it is used for:</strong>
        <p style="margin-top: 2px; color: #334155;">${escapeHtml(data.used_for)}</p>
      </div>

      <div style="font-size: 0.85rem; color: #1e293b; margin-bottom: 8px;">
        <strong>💧 How it is usually taken:</strong>
        <p style="margin-top: 2px; color: #334155;">${escapeHtml(data.how_to_use)}</p>
      </div>

      <div style="font-size: 0.85rem; color: #b45309; background: #fffbeb; padding: 8px 12px; border-radius: 6px; margin-bottom: 8px;">
        <strong>⚠️ Simple precautions for your family:</strong>
        <p style="margin-top: 2px;">${escapeHtml(data.simple_tips)}</p>
      </div>

      <p style="font-size: 0.72rem; color: #94a3b8; margin-top: 8px;">
        ${escapeHtml(data.disclaimer)}
      </p>

      <button type="button" class="btn-primary" style="margin-top: 12px; width: 100%; border-radius: 8px; font-size: 0.85rem; padding: 10px; background: var(--primary); color: white; border: none; font-weight: 700; cursor: pointer;" onclick="askSaarthiAboutMedicine('${escapeHtml(data.name)}')">
        💬 Ask Saarthi in Chat about this medicine
      </button>
    </div>
  `;

  const btnListen = document.getElementById('btn-med-listen');
  if (btnListen) {
    btnListen.onclick = () => toggleSpeech(spokenText, btnListen);
  }
}

function askSaarthiAboutMedicine(medName) {
  closeMedicineModal();
  showView('chat');
  document.getElementById('chat-user-input').value = `Can you explain ${medName}?`;
  handleUserChatSubmit();
}

// -------------------------------------------------------------------
// 7. EMERGENCY HELPLINE DIRECTORY MODAL
// -------------------------------------------------------------------
function openEmergencyModal() {
  document.getElementById('modal-emergency').style.display = 'flex';
}

function closeEmergencyModal() {
  document.getElementById('modal-emergency').style.display = 'none';
}

// -------------------------------------------------------------------
// 7.1 SETTINGS & PROFILE MODAL
// -------------------------------------------------------------------
function openSettingsModal() {
  document.getElementById('modal-settings').style.display = 'flex';
  const nameInput = document.getElementById('settings-name');
  const ageSelect = document.getElementById('settings-age');
  const langSelect = document.getElementById('settings-lang');
  const fsSelect = document.getElementById('settings-fontsize');

  if (nameInput) nameInput.value = (currentUser.name && currentUser.name !== 'User') ? currentUser.name : '';
  if (ageSelect) ageSelect.value = currentUser.age_group || '18-59';
  if (langSelect) langSelect.value = currentLanguage;
  if (fsSelect) {
    const savedFs = localStorage.getItem('swasthya_saarthi_fontsize') || 'normal';
    fsSelect.value = savedFs;
  }
}

function closeSettingsModal() {
  document.getElementById('modal-settings').style.display = 'none';
}

function handleSettingsSave(e) {
  if (e) e.preventDefault();
  const name = document.getElementById('settings-name').value.trim();
  const age = document.getElementById('settings-age').value;
  const lang = document.getElementById('settings-lang').value;
  const fs = document.getElementById('settings-fontsize').value;

  currentUser.name = name || 'User';
  currentUser.age_group = age;
  currentUser.language = lang;
  currentUser.is_logged_in = true;

  localStorage.setItem('swasthya_saarthi_user', JSON.stringify(currentUser));
  toggleFontSize(fs);

  if (lang !== currentLanguage) {
    currentLanguage = lang;
    document.getElementById('lang-select').value = lang;
    applyLanguageTranslations(lang);
    if (currentView === 'chat') {
      loadChatWelcome(true);
    }
  }

  updateUserBadge();
  closeSettingsModal();
}

function onSettingsLangChange() {
  const newLang = document.getElementById('settings-lang').value;
  currentLanguage = newLang;
  document.getElementById('lang-select').value = newLang;
  applyLanguageTranslations(newLang);
}

function toggleFontSize(size) {
  if (size === 'large') {
    document.body.classList.add('large-font');
  } else {
    document.body.classList.remove('large-font');
  }
  localStorage.setItem('swasthya_saarthi_fontsize', size);
}

function clearChatHistory() {
  if (confirm("Are you sure you want to clear your current conversation?")) {
    chatHistory = [];
    document.getElementById('chat-messages-container').innerHTML = '';
    closeSettingsModal();
    loadChatWelcome(true);
  }
}

// -------------------------------------------------------------------
// 7.2 GENERAL PUBLIC HEALTH GUIDELINES MODAL
// -------------------------------------------------------------------
const GUIDELINES_CONTENT = {
  en: `
    <p style="font-size: 0.85rem; color: #475569; margin-bottom: 16px;">
      Core wellness and preventive recommendations from the World Health Organization (WHO) and MoHFW:
    </p>
    <div class="plan-section">
      <div class="plan-title">💧 1. Daily Hydration</div>
      <p style="font-size: 0.85rem; color: #334155;">Drink at least 2.5 to 3 liters (8–10 glasses) of clean drinking water daily. Increase intake during fever, loose motions, or hot weather.</p>
    </div>
    <div class="plan-section">
      <div class="plan-title">🥗 2. Balanced Nutrition</div>
      <p style="font-size: 0.85rem; color: #334155;">Consume home-cooked meals rich in lentils (dal), green leafy vegetables, and seasonal fruits. Limit excess sodium, refined sugars, and deep-fried items.</p>
    </div>
    <div class="plan-section">
      <div class="plan-title">😴 3. Sleep & Recovery</div>
      <p style="font-size: 0.85rem; color: #334155;">Aim for 7 to 8 hours of uninterrupted sleep every night to maintain cellular repair and immune defense.</p>
    </div>
    <div class="plan-section">
      <div class="plan-title">🚶 4. Physical Movement</div>
      <p style="font-size: 0.85rem; color: #334155;">Practice 30 minutes of moderate activity such as brisk walking, yoga, or stretching on most days.</p>
    </div>
    <div class="plan-section">
      <div class="plan-title">🧼 5. Hand & Food Hygiene</div>
      <p style="font-size: 0.85rem; color: #334155;">Wash hands with soap for at least 20 seconds before preparing food, eating, and after using restrooms or coming from outdoors.</p>
    </div>
    <div class="plan-section" style="background: #fffbeb; border-color: #fde68a;">
      <div class="plan-title" style="color: #b45309;">🩺 6. When to Seek In-Person Medical Care</div>
      <p style="font-size: 0.85rem; color: #334155;">If fever exceeds 3 days, cough persists over 2 weeks, or you experience difficulty breathing, chest pain, or severe weakness, always consult a qualified healthcare provider.</p>
    </div>
  `,
  hi: `
    <p style="font-size: 0.85rem; color: #475569; margin-bottom: 16px;">
      विश्व स्वास्थ्य संगठन (WHO) और स्वास्थ्य मंत्रालय (MoHFW) द्वारा प्रमाणित दैनिक स्वास्थ्य नियम:
    </p>
    <div class="plan-section">
      <div class="plan-title">💧 1. पर्याप्त जलपान (हाइड्रेशन)</div>
      <p style="font-size: 0.85rem; color: #334155;">प्रतिदिन कम से कम 2.5 से 3 लीटर (8-10 गिलास) साफ पानी पिएं। बुखार, उल्टी-दस्त या गर्मी के मौसम में तरल पदार्थों की मात्रा बढ़ाएं।</p>
    </div>
    <div class="plan-section">
      <div class="plan-title">🥗 2. संतुलित और पौष्टिक आहार</div>
      <p style="font-size: 0.85rem; color: #334155;">घर का बना ताजा भोजन करें जिसमें दालें, हरी सब्जियां और मौसमी फल शामिल हों। अधिक नमक, चीनी और तले-भुने खाने से बचें।</p>
    </div>
    <div class="plan-section">
      <div class="plan-title">😴 3. पर्याप्त नींद और विश्राम</div>
      <p style="font-size: 0.85rem; color: #334155;">प्रतिदिन 7 से 8 घंटे की गहरी नींद लें ताकि शरीर की रोग प्रतिरोधक क्षमता (इम्यूनिटी) मजबूत रहे।</p>
    </div>
    <div class="plan-section">
      <div class="plan-title">🚶 4. नियमित शारीरिक गतिविधि</div>
      <p style="font-size: 0.85rem; color: #334155;">सप्ताह के अधिकांश दिनों में कम से कम 30 मिनट तेज चाल, योग या व्यायाम अवश्य करें।</p>
    </div>
    <div class="plan-section">
      <div class="plan-title">🧼 5. स्वच्छता और हाथ धोना</div>
      <p style="font-size: 0.85rem; color: #334155;">भोजन बनाने और खाने से पहले, तथा बाहर से आने या शौचालय के बाद 20 सेकंड तक साबुन से हाथ धोएं।</p>
    </div>
    <div class="plan-section" style="background: #fffbeb; border-color: #fde68a;">
      <div class="plan-title" style="color: #b45309;">🩺 6. डॉक्टर को कब दिखाएं</div>
      <p style="font-size: 0.85rem; color: #334155;">यदि बुखार 3 दिन से अधिक रहे, खांसी 2 सप्ताह से ज्यादा हो, या सांस लेने में तकलीफ अथवा सीने में दर्द हो, तो तुरंत डॉक्टर से परामर्श लें।</p>
    </div>
  `,
  gu: `
    <p style="font-size: 0.85rem; color: #475569; margin-bottom: 16px;">
      વિશ્વ આરોગ્ય સંસ્થા (WHO) અને આરોગ્ય મંત્રાલય દ્વારા સામાન્ય સ્વાસ્થ્ય માર્ગદર્શિકા:
    </p>
    <div class="plan-section">
      <div class="plan-title">💧 1. પૂરતું પાણી પીવો</div>
      <p style="font-size: 0.85rem; color: #334155;">દિવસમાં ઓછામાં ઓછું ૨.૫ થી ૩ લિટર (૮-૧૦ ગ્લાસ) સ્વચ્છ પાણી પીવો. તાવ કે ગરમીમાં પ્રવાહી વધારો.</p>
    </div>
    <div class="plan-section">
      <div class="plan-title">🥗 2. પૌષ્ટિક અને સંતુલિત આહાર</div>
      <p style="font-size: 0.85rem; color: #334155;">દાળ, લીલા શાકભાજી અને તાજા ફળોનો આહારમાં સમાવેશ કરો. વધુ તેલ અને ખાંડવાળા ખોરાકથી દૂર રહો.</p>
    </div>
    <div class="plan-section">
      <div class="plan-title">😴 3. પૂરતી ઊંઘ અને આરામ</div>
      <p style="font-size: 0.85rem; color: #334155;">રોગપ્રતિકારક શક્તિ જાળવવા રોજ ૭ થી ૮ કલાકની શાંત ઊંઘ લો.</p>
    </div>
    <div class="plan-section">
      <div class="plan-title">🚶 4. દૈનિક કસરત અને યોગ</div>
      <p style="font-size: 0.85rem; color: #334155;">રોજ ઓછામાં ઓછી ૩૦ મિનિટ ઝડપી ચાલવું કે યોગાસન કરવાની ટેવ પાડો.</p>
    </div>
    <div class="plan-section">
      <div class="plan-title">🧼 5. હાથની સ્વચ્છતા</div>
      <p style="font-size: 0.85rem; color: #334155;">જમતા પહેલાં અને બહારથી આવ્યા પછી ઓછામાં ઓછી ૨૦ સેકન્ડ સાબુથી હાથ ધોવો.</p>
    </div>
    <div class="plan-section" style="background: #fffbeb; border-color: #fde68a;">
      <div class="plan-title" style="color: #b45309;">🩺 6. ડૉક્ટરની સલાહ ક્યારે લેવી</div>
      <p style="font-size: 0.85rem; color: #334155;">જો તાવ ૩ દિવસથી વધુ રહે, ખાંસી ૨ અઠવાડિયાથી વધુ હોય કે શ્વાસ લેવામાં તકલીફ થાય તો તરત ડૉક્ટરનો સંપર્ક કરો.</p>
    </div>
  `
};

function openGuidelinesModal() {
  renderGuidelinesBody();
  document.getElementById('modal-guidelines').style.display = 'flex';
}

function closeGuidelinesModal() {
  document.getElementById('modal-guidelines').style.display = 'none';
}

function renderGuidelinesBody() {
  const container = document.getElementById('guidelines-content-body');
  if (container) {
    container.innerHTML = GUIDELINES_CONTENT[currentLanguage] || GUIDELINES_CONTENT.en;
  }
}


// -------------------------------------------------------------------
// 8. TRAYA-STYLE STEPPER HEALTH TEST
// -------------------------------------------------------------------
function setDefaultStepperSelections() {
  selectCardOption('age', '18-59', document.querySelector('#step-pane-1 .option-card'));
}

function selectCardOption(field, value, el) {
  stepperData[field] = value;

  const parent = el.closest('.options-grid');
  if (parent) {
    parent.querySelectorAll('.option-card').forEach(c => c.classList.remove('selected'));
    el.classList.add('selected');
  }

  if (field === 'sex') {
    const pregBlock = document.getElementById('stepper-pregnancy-block');
    if (value === 'Female') {
      pregBlock.style.display = 'block';
    } else {
      pregBlock.style.display = 'none';
      stepperData.pregnant = 'Not applicable';
    }
  }
}

function toggleMultiCardOption(type, value, el) {
  if (type === 'symptom') {
    const idx = stepperData.symptoms.indexOf(value);
    if (idx > -1) {
      stepperData.symptoms.splice(idx, 1);
      el.classList.remove('selected');
    } else {
      stepperData.symptoms.push(value);
      el.classList.add('selected');
    }
  } else if (type === 'chronic') {
    const noneCard = document.querySelector('#step-pane-4 .option-card:last-child');
    if (noneCard) noneCard.classList.remove('selected');

    const idx = stepperData.chronic_conditions.indexOf(value);
    if (idx > -1) {
      stepperData.chronic_conditions.splice(idx, 1);
      el.classList.remove('selected');
    } else {
      stepperData.chronic_conditions.push(value);
      el.classList.add('selected');
    }
  }
}

function selectNoneChronic(el) {
  stepperData.chronic_conditions = ['None'];
  const parent = el.closest('.options-grid');
  parent.querySelectorAll('.option-card').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
}

function goToStep(stepNum) {
  currentStep = stepNum;

  for (let i = 1; i <= 5; i++) {
    const pane = document.getElementById(`step-pane-${i}`);
    const tab = document.getElementById(`tab-step-${i}`);
    if (pane) pane.style.display = (i === stepNum) ? 'block' : 'none';
    if (tab) {
      tab.classList.toggle('active', i === stepNum);
      tab.classList.toggle('completed', i < stepNum);
    }
  }

  const progressPercent = stepNum * 20;
  document.getElementById('stepper-progress-fill').style.width = `${progressPercent}%`;
  document.getElementById('stepper-progress-text').innerText = `Step ${stepNum} of 5 (${progressPercent}%)`;

  const prevBtn = document.getElementById('btn-stepper-prev');
  if (prevBtn) {
    prevBtn.style.visibility = (stepNum > 1 && stepNum < 5) ? 'visible' : 'hidden';
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function goToPreviousStep() {
  if (currentStep > 1) {
    goToStep(currentStep - 1);
  }
}

function resetStepper() {
  stepperData = {
    age_group: '18-59',
    sex: 'Male',
    pregnant: 'Not applicable',
    symptoms: [],
    symptoms_text: '',
    duration: '<24h',
    severity: 'Mild',
    chronic_conditions: []
  };
  document.querySelectorAll('.option-card').forEach(c => c.classList.remove('selected'));
  document.getElementById('stepper-symptoms-text').value = '';
  goToStep(1);
}

async function generateGuidedAssessment() {
  const btn = document.getElementById('btn-generate-assessment');
  btn.disabled = true;
  btn.innerHTML = 'Analyzing with Public Health Safety Pipeline... ⏳';

  const customText = document.getElementById('stepper-symptoms-text').value.trim();
  const symptomsCombined = [...stepperData.symptoms];
  if (customText) symptomsCombined.push(customText);
  const symptomsQuery = symptomsCombined.join(', ') || 'Mild general fatigue and discomfort';

  const chronicPayload = stepperData.chronic_conditions.length > 0 
    ? stepperData.chronic_conditions 
    : ['None'];

  const payload = {
    age_group: stepperData.age_group,
    sex: stepperData.sex,
    pregnant: stepperData.pregnant,
    duration: stepperData.duration,
    severity: stepperData.severity,
    chronic_conditions: chronicPayload,
    symptoms_text: symptomsQuery,
    language: currentLanguage
  };

  try {
    const res = await fetch('/api/assess', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    renderAssessmentReport(data);
    goToStep(5);
  } catch (err) {
    alert("Could not complete assessment. Please check connection and try again.");
  } finally {
    btn.disabled = false;
    btn.innerHTML = 'Generate Saarthi Care Plan ✨';
  }
}

function renderAssessmentReport(data) {
  const container = document.getElementById('assessment-result-card');
  const dict = I18N[currentLanguage] || I18N.en;
  const uiState = data.ui_state;

  if (uiState === 'emergency' || uiState === 'mental_health') {
    const rf = data.red_flag;
    const isCrisis = uiState === 'mental_health';

    container.innerHTML = `
      <div class="triage-hero ${isCrisis ? 'yellow' : 'red'}">
        <span class="triage-pill" style="background: ${isCrisis ? '#7c3aed' : '#dc2626'};">
          ${isCrisis ? 'Crisis Support Needed' : 'Immediate Emergency Care'}
        </span>
        <h2 class="triage-hero-title">${escapeHtml(rf.title)}</h2>
        <p class="triage-hero-desc">${escapeHtml(rf.message)}</p>
        <div style="margin-top: 16px; display: flex; gap: 10px; flex-wrap: wrap;">
          ${isCrisis 
            ? `<a href="tel:14416" class="btn-call crisis">💜 Call Tele-MANAS (14416)</a>
               <a href="tel:112" class="btn-call">🚨 Call 112</a>`
            : `<a href="tel:108" class="btn-call">📞 Call 108 (Ambulance)</a>
               <a href="tel:112" class="btn-call">🚨 Call 112</a>`
          }
        </div>
      </div>
    `;
    return;
  }

  const g = data.guidance;
  const level = g.triage_level;

  let heroClass = 'green';
  let pillText = 'Self-Care & Monitor';
  let titleText = 'Supportive Self-Care Plan';

  if (level === 'doctor_2_3_days') {
    heroClass = 'yellow';
    pillText = 'Consult Doctor in 2–3 Days';
    titleText = 'Planned Medical Follow-up Advised';
  } else if (level === 'doctor_today') {
    heroClass = 'orange';
    pillText = 'See a Doctor Today';
    titleText = 'Same-Day Clinical Evaluation Recommended';
  } else if (level === 'emergency') {
    heroClass = 'red';
    pillText = 'Seek Emergency Care';
    titleText = 'Urgent Clinical Evaluation Warranted';
  }

  let selfCareHtml = '';
  (g.self_care_tips || []).forEach(tip => {
    selfCareHtml += `<li>${escapeHtml(tip)}</li>`;
  });

  let warningHtml = '';
  (g.warning_signs || []).forEach(w => {
    warningHtml += `<li>${escapeHtml(w)}</li>`;
  });

  const spokenReportText = `${titleText}. ${g.summary}. Self care: ${(g.self_care_tips || []).join('. ')}. Warning signs: ${(g.warning_signs || []).join('. ')}`;

  container.innerHTML = `
    <div class="triage-hero ${heroClass}">
      <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <span class="triage-pill">${pillText}</span>
        <button class="btn-speech-listen" id="btn-report-listen">
          🔊 ${dict.btn_listen}
        </button>
      </div>
      <h2 class="triage-hero-title">${titleText}</h2>
      <p class="triage-hero-desc">${escapeHtml(g.summary)}</p>
    </div>

    <div class="plan-section">
      <div class="plan-title">🌿 Verified Comfort & Self-Care Guidance</div>
      <ul class="plan-list">${selfCareHtml || '<li>Rest and stay hydrated.</li>'}</ul>
    </div>

    <div class="plan-section" style="background: #fffbeb; border-color: #fde68a;">
      <div class="plan-title" style="color: #b45309;">⚠️ Warning Signs (When to Escalate)</div>
      <ul class="plan-list warning">${warningHtml || '<li>High fever persisting or shortness of breath.</li>'}</ul>
    </div>
  `;

  const btnListen = document.getElementById('btn-report-listen');
  if (btnListen) {
    btnListen.onclick = () => toggleSpeech(spokenReportText, btnListen);
  }
}

function continueInChat() {
  showView('chat');
  renderAssistantMessage(
    "I have reviewed your completed health assessment! Feel free to ask me any questions about staying hydrated, comfort measures, or what questions to ask your doctor.",
    ["How to stay hydrated?", "When should I see a doctor?", "What foods to eat?"]
  );
}

// -------------------------------------------------------------------
// Helper Utilities
// -------------------------------------------------------------------
function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[m]);
}

function formatMarkdown(text) {
  if (!text) return '';
  let html = escapeHtml(text);
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/^•\s*(.*)$/gm, '<li>$1</li>');
  html = html.replace(/\n\n/g, '</p><p>');
  html = html.replace(/\n/g, '<br>');
  return `<p>${html}</p>`;
}
