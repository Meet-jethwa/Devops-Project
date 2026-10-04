# Phase 1 copied advisory templates; generation behavior remains unchanged.
"""
Advisory Generation Templates and Paraphrases for English and Hindi.
Maps structured records:
  {action, when, duration_hours, rain_expected, fertigation}
to natural language agricultural advisories.
Includes TODO_NATIVE_CHECK annotations for manual linguistic verification.
"""

# English Templates with Paraphrase Variations
EN_TEMPLATES = {
    ("irrigate", False, False): [
        "Apply irrigation for {duration_hours} hours in the {when}.",
        "Run the irrigation system for {duration_hours} hours during the {when}.",
        "It is advised to irrigate your sugarcane field for {duration_hours} hours in the {when}.",
        "Water the crop for {duration_hours} hours in the {when}."
    ],
    ("irrigate", False, True): [
        "Apply drip irrigation for {duration_hours} hours in the {when} along with fertigation as scheduled.",
        "Run irrigation for {duration_hours} hours in the {when} and inject the prescribed fertilizer dose.",
        "Irrigate for {duration_hours} hours in the {when} with fertigation enabled.",
        "Perform {duration_hours} hours of irrigation in the {when}, mixing soluble fertilizers through the drip line."
    ],
    ("irrigate", True, False): [
        "Rain is expected; limit irrigation to {duration_hours} hours in the {when} and monitor soil wetness.",
        "Rainfall forecasted. Provide light watering for {duration_hours} hours in the {when} if soil feels dry.",
        "Due to impending rain, reduce irrigation duration to {duration_hours} hours in the {when}."
    ],
    ("irrigate", True, True): [
        "Rain is forecast. Apply {duration_hours} hours of irrigation in the {when} with light fertigation only if rainfall is delayed.",
        "With rain expected, complete fertigation with {duration_hours} hours of irrigation in the {when} before heavy showers begin."
    ],
    ("skip_irrigation", True, False): [
        "Rain is expected. Postpone irrigation and monitor soil moisture.",
        "Hold off on irrigation as rainfall is forecasted for the area.",
        "No irrigation needed currently; expected rain will maintain adequate root zone moisture.",
        "Skip irrigation today due to incoming rainfall."
    ],
    ("skip_irrigation", True, True): [
        "Rain is expected. Postpone both irrigation and fertigation to avoid fertilizer leaching.",
        "Hold fertigation and irrigation due to upcoming rain; resume after soil dries out."
    ],
    ("skip_irrigation", False, False): [
        "Soil moisture is adequate. No irrigation needed in the {when}.",
        "Skip watering in the {when}; conserve water as current soil moisture is sufficient."
    ],
    ("skip_irrigation", False, True): [
        "Postpone irrigation in the {when}. Defer fertigation until next scheduled irrigation cycle."
    ],
    ("delay_irrigation", False, False): [
        "Delay irrigation until {when} and run for {duration_hours} hours.",
        "Wait until {when} before applying {duration_hours} hours of water."
    ],
    ("delay_irrigation", True, False): [
        "Delay irrigation to {when} as rain is expected; check field moisture before starting."
    ],
    ("light_irrigation", False, False): [
        "Provide a light irrigation of {duration_hours} hours in the {when}.",
        "Give a light watering for {duration_hours} hours during the {when} to prevent moisture stress."
    ],
    ("light_irrigation", False, True): [
        "Apply a light fertigation run for {duration_hours} hours in the {when}."
    ]
}

# Hindi Templates with Paraphrase Variations (Annotated with TODO_NATIVE_CHECK)
HI_TEMPLATES = {
    ("irrigate", False, False): [
        "{when} में {duration_hours} घंटे तक सिंचाई करें।",
        "गन्ने के खेत में {when} {duration_hours} घंटे के लिए पानी लगाएं।",
        "सलाह दी जाती है कि {when} में {duration_hours} घंटे ड्रिप सिंचाई चलाएं।",  # TODO_NATIVE_CHECK
        "{when} के समय {duration_hours} घंटे पानी देना पर्याप्त रहेगा।"
    ],
    ("irrigate", False, True): [
        "{when} में {duration_hours} घंटे सिंचाई करें और साथ में तय खाद (फर्टिगेशन) भी दें।",
        "{when} के समय {duration_hours} घंटे पानी चलाएं और ड्रिप से उर्वरक डालें।",  # TODO_NATIVE_CHECK
        "उर्वरक देने के लिए {when} में {duration_hours} घंटे ड्रिप सिंचाई चलाएं।"
    ],
    ("irrigate", True, False): [
        "बारिश की संभावना है, अतः {when} में केवल {duration_hours} घंटे हल्की सिंचाई करें।",  # TODO_NATIVE_CHECK
        "वर्षा का अनुमान है। यदि मिट्टी में नमी कम हो तभी {when} में {duration_hours} घंटे पानी दें।"
    ],
    ("irrigate", True, True): [
        "बारिश आने की संभावना है। {when} में {duration_hours} घंटे हल्की फर्टिगेशन करें ताकि खाद बह न जाए।",  # TODO_NATIVE_CHECK
        "वर्षा को ध्यान में रखते हुए {when} में {duration_hours} घंटे नियंत्रित सिंचाई और उर्वरक दें।"
    ],
    ("skip_irrigation", True, False): [
        "बारिश की संभावना है। अभी सिंचाई न करें और खेत में नमी की स्थिति देखें।",
        "वर्षा का अनुमान होने के कारण सिंचाई रोक दें।",  # TODO_NATIVE_CHECK
        "बारिश आने वाली है, इसलिए अभी पानी लगाने की आवश्यकता नहीं है।"
    ],
    ("skip_irrigation", True, True): [
        "बारिश की संभावना है। खाद बह जाने से बचाने के लिए सिंचाई और फर्टिगेशन दोनों टाल दें।",  # TODO_NATIVE_CHECK
        "वर्षा को देखते हुए उर्वरक और पानी देना अभी रोक दें।"
    ],
    ("skip_irrigation", False, False): [
        "खेत में पर्याप्त नमी मौजूद है। {when} में सिंचाई की आवश्यकता नहीं है।",  # TODO_NATIVE_CHECK
        "मिट्टी में पर्याप्त नमी है, अतः {when} पानी न लगाएं।"
    ],
    ("skip_irrigation", False, True): [
        "{when} में सिंचाई रोकें। उर्वरक अगली नियमित सिंचाई के साथ ही दें।"  # TODO_NATIVE_CHECK
    ],
    ("delay_irrigation", False, False): [
        "सिंचाई {when} तक के लिए टालें और तब {duration_hours} घंटे पानी दें।",  # TODO_NATIVE_CHECK
        "{when} तक प्रतीक्षा करें, फिर {duration_hours} घंटे सिंचाई करें।"
    ],
    ("delay_irrigation", True, False): [
        "बारिश के कारण सिंचाई {when} तक स्थगित करें।"  # TODO_NATIVE_CHECK
    ],
    ("light_irrigation", False, False): [
        "{when} में {duration_hours} घंटे की हल्की सिंचाई दें ताकि फसल पर नमी का तनाव न हो।",  # TODO_NATIVE_CHECK
        "फसल की सुरक्षा के लिए {when} केवल {duration_hours} घंटे हल्का पानी लगाएं।"
    ],
    ("light_irrigation", False, True): [
        "{when} में {duration_hours} घंटे के लिए हल्की फर्टिगेशन चलाएं।"  # TODO_NATIVE_CHECK
    ]
}

# Translation mapping for 'when' temporal slot per language
WHEN_MAP = {
    "hi": {
        "morning": "सुबह",
        "evening": "शाम",
        "tomorrow": "कल",
        "after_2_days": "2 दिन बाद",
        "today": "आज",
        "afternoon": "दोपहर",
        "night": "रात"
    },
    "mr": {
        "morning": "सकाळी",
        "evening": "संध्याकाळी",
        "tomorrow": "उद्या",
        "after_2_days": "2 दिवसांनी",
        "today": "आज",
        "afternoon": "दुपारी",
        "night": "रात्री"
    },
    "gu": {
        "morning": "સવારે",
        "evening": "સાંજે",
        "tomorrow": "કાલે",
        "after_2_days": "2 દિવસ પછી",
        "today": "આજ",
        "afternoon": "બપોરે",
        "night": "રાત્રે"
    },
    "pa": {
        "morning": "ਸਵੇਰੇ",
        "evening": "ਸ਼ਾਮ ਨੂੰ",
        "tomorrow": "ਕੱਲ੍ਹ",
        "after_2_days": "2 ਦਿਨਾਂ ਬਾਅਦ",
        "today": "ਅੱਜ",
        "afternoon": "ਦੁਪਹਿਰ",
        "night": "ਰਾਤ"
    },
    "kn": {
        "morning": "ಬೆಳಿಗ್ಗೆ",
        "evening": "ಸಂಜೆ",
        "tomorrow": "ನಾಳೆ",
        "after_2_days": "2 ದಿನಗಳ ನಂತರ",
        "today": "ಇಂದು",
        "afternoon": "ಮಧ್ಯಾಹ್ನ",
        "night": "ರಾತ್ರಿ"
    },
}

# Keep backward-compat alias
HI_WHEN_MAP = WHEN_MAP["hi"]

LOCALIZED_TEMPLATES = {
    "mr": {
        ("irrigate", False, False): [
            "{when} {duration_hours} तास ऊस पिकाला सिंचन करा.",
            "गन्न्याच्या शेतात {when} {duration_hours} तास पाणी द्या."
        ],
        ("irrigate", False, True): [
            "{when} {duration_hours} तास सिंचन करा आणि नियोजित खत व्यवस्थापन करा.",
            "ड्रिप सिंचनातून {when} {duration_hours} तास पाणी द्या आणि विद्राव्य खत द्या."
        ],
        ("irrigate", True, False): [
            "पावसाची शक्यता असली तरी माती कोरडी असल्यास {when} {duration_hours} तास हलकी सिंचन करा."
        ],
        ("irrigate", True, True): [
            "पावसापूर्वी {when} {duration_hours} तास हलक्या फर्टिगेशनसह सिंचन करा."
        ],
        ("skip_irrigation", True, False): [
            "पावसाची शक्यता आहे. सिंचन पुढे ढकला आणि जमिनीतील ओलावा तपासा.",
            "वर्षाळ्यामुळे आत्ता सिंचन आवश्यक नाही."
        ],
        ("skip_irrigation", True, True): [
            "पावसामुळे सिंचन आणि खत देणे पुढे ढकला, जेणेकरून खत वाहून जाणार नाही."
        ],
        ("skip_irrigation", False, False): [
            "जमिनीत पुरेसा ओलावा आहे. {when} सिंचनाची गरज नाही.",
            "आत्ता पाणी देऊ नका; माती पुरेशी ओलसर आहे."
        ],
        ("skip_irrigation", False, True): [
            "{when} सिंचन थांबवा. खत पुढील नियमित सिंचनात द्या."
        ],
        ("delay_irrigation", False, False): [
            "{when} पर्यंत सिंचन पुढे ढकला आणि मग {duration_hours} तास पाणी द्या."
        ],
        ("delay_irrigation", True, False): [
            "पावसामुळे सिंचन {when} पर्यंत पुढे ढकला."
        ],
        ("light_irrigation", False, False): [
            "{when} {duration_hours} तासांची हलकी सिंचन द्या."
        ],
    },
    "gu": {
        ("irrigate", False, False): [
            "{when} {duration_hours} કલાક શેરડીના પાકને સિંચાઈ આપો.",
            "ગોળ ઉત્પાદન માટે {when} {duration_hours} કલાક સિંચાઈ ચલાવો."
        ],
        ("irrigate", False, True): [
            "{when} {duration_hours} કલાક સિંચાઈ કરો અને નિયોજિત ખાતર વ્યવસ્થાપન કરો.",
            "ડ્રિપ દ્વારા {when} {duration_hours} કલાક ફર્ટિગેશન ચલાવો."
        ],
        ("irrigate", True, False): [
            "વરસાદ અપેક્ષિત છે; જો ભેજ ઓછો હોય તો {when} {duration_hours} કલાક હળવી સિંચાઈ કરો."
        ],
        ("irrigate", True, True): [
            "વરસાદ પહેલાં {when} {duration_hours} કલાક ફર્ટિગેશન સાથે સિંચાઈ પૂર્ણ કરો."
        ],
        ("skip_irrigation", True, False): [
            "વરસાદની શક્યતા છે. સિંચાઈ મુલતવી રાખો અને જમીનની ભેજ તપાસો.",
            "વરસાદ આવવાનો છે, એટલે સિંચાઈ જરૂરી નથી."
        ],
        ("skip_irrigation", True, True): [
            "વરસાદને કારણે સિંચાઈ અને ખાતર આપવાનું મુલતવી રાખો, જેથી ખાતર વહી ન જાય."
        ],
        ("skip_irrigation", False, False): [
            "જમીનમાં પૂરતી ભેજ છે. {when} સિંચાઈ જરૂરી નથી.",
            "હાલ પૂરતી ભેજ છે, એટલે {when} પાણી ન આપો."
        ],
        ("skip_irrigation", False, True): [
            "{when} સિંચાઈ મુલતવી રાખો. ખાતર આગામી નિયમિત સિંચાઈ સાથે આપો."
        ],
        ("delay_irrigation", False, False): [
            "{when} સુધી સિંચાઈ મુલતવી રાખો, પછી {duration_hours} કલાક પાણી આપો."
        ],
        ("delay_irrigation", True, False): [
            "વરસાદ અપેક્ષિત છે; સિંચાઈ {when} સુધી મોકૂફ રાખો."
        ],
        ("light_irrigation", False, False): [
            "{when} {duration_hours} કલાકની હળવી સિંચાઈ આપો."
        ],
    },
    "pa": {
        ("irrigate", False, False): [
            "{when} ਗੰਨੇ ਦੀ ਫਸਲ ਨੂੰ {duration_hours} ਘੰਟੇ ਸਿੰਚਾਈ ਦਿਓ.",
            "{when} {duration_hours} ਘੰਟੇ ਖੇਤ ਨੂੰ ਪਾਣੀ ਦਿਓ."
        ],
        ("irrigate", False, True): [
            "{when} {duration_hours} ਘੰਟੇ ਸਿੰਚਾਈ ਕਰੋ ਅਤੇ ਨਿਰਧਾਰਤ ਖਾਦ ਪ੍ਰਬੰਧਨ ਕਰੋ.",
            "ਡ੍ਰਿਪ ਰਾਹੀਂ {when} {duration_hours} ਘੰਟੇ ਫਰਟੀਗੇਸ਼ਨ ਕਰੋ."
        ],
        ("irrigate", True, False): [
            "ਮੀਂਹ ਦੀ ਸੰਭਾਵਨਾ ਹੈ; ਜੇ ਮਿੱਟੀ ਸੁੱਕੀ ਲੱਗੇ ਤਾਂ {when} {duration_hours} ਘੰਟੇ ਹਲਕੀ ਸਿੰਚਾਈ ਕਰੋ."
        ],
        ("irrigate", True, True): [
            "ਮੀਂਹ ਤੋਂ ਪਹਿਲਾਂ {when} {duration_hours} ਘੰਟੇ ਹਲਕੀ ਫਰਟੀਗੇਸ਼ਨ ਨਾਲ ਸਿੰਚਾਈ ਪੂਰੀ ਕਰੋ."
        ],
        ("skip_irrigation", True, False): [
            "ਮੀਂਹ ਦੀ ਸੰਭਾਵਨਾ ਹੈ। ਸਿੰਚਾਈ ਮੁਲਤਵੀ ਕਰੋ ਅਤੇ ਮਿੱਟੀ ਦੀ ਨਮੀ ਜਾਂਚੋ.",
            "ਮੀਂਹ ਆਉਣ ਕਾਰਨ ਹੁਣ ਸਿੰਚਾਈ ਜ਼ਰੂਰੀ ਨਹੀਂ."
        ],
        ("skip_irrigation", True, True): [
            "ਮੀਂਹ ਕਾਰਨ ਸਿੰਚਾਈ ਅਤੇ ਖਾਦ ਪਾਉਣਾ ਮੁਲਤਵੀ ਕਰੋ ਤਾਂ ਜੋ ਖਾਦ ਨਾ ਵਹੇ."
        ],
        ("skip_irrigation", False, False): [
            "ਮਿੱਟੀ ਵਿੱਚ ਪਰਿਆਪਤ ਨਮੀ ਹੈ। {when} ਸਿੰਚਾਈ ਦੀ ਲੋੜ ਨਹੀਂ.",
            "ਹੁਣ ਮਿੱਟੀ ਠੀਕ ਹੈ; {when} ਪਾਣੀ ਨਾ ਦਿਓ."
        ],
        ("skip_irrigation", False, True): [
            "{when} ਸਿੰਚਾਈ ਰੋਕੋ। ਖਾਦ ਅਗਲੀ ਨਿਯਮਿਤ ਸਿੰਚਾਈ ਨਾਲ ਦਿਓ."
        ],
        ("delay_irrigation", False, False): [
            "{when} ਤੱਕ ਸਿੰਚਾਈ ਮੁਲਤਵੀ ਕਰੋ ਅਤੇ ਫਿਰ {duration_hours} ਘੰਟੇ ਪਾਣੀ ਦਿਓ."
        ],
        ("delay_irrigation", True, False): [
            "ਮੀਂਹ ਕਾਰਨ {when} ਤੱਕ ਸਿੰਚਾਈ ਟਾਲੋ."
        ],
        ("light_irrigation", False, False): [
            "{when} {duration_hours} ਘੰਟੇ ਦੀ ਹਲਕੀ ਸਿੰਚਾਈ ਦਿਓ."
        ],
    },
    "kn": {
        ("irrigate", False, False): [
            "{when} ಕಬ್ಬಿನ ಬೆಳೆಗೆ {duration_hours} ಗಂಟೆಗಳ ಕಾಲ ನೀರಾವರಿ ನೀಡಿ.",
            "{when} {duration_hours} ಗಂಟೆಗಳ ಕಾಲ ಹೊಲಕ್ಕೆ ನೀರು ಕೊಡಿ."
        ],
        ("irrigate", False, True): [
            "{when} {duration_hours} ಗಂಟೆಗಳ ಕಾಲ ನೀರಾವರಿ ಮಾಡಿ ಮತ್ತು ನಿಗದಿತ ಗೊಬ್ಬರ ನಿರ್ವಹಣೆ ಮಾಡಿ.",
            "ಡ್ರಿಪ್ ಮೂಲಕ {when} {duration_hours} ಗಂಟೆ ಫರ್ಟಿಗೇಶನ್ ಮಾಡಿ."
        ],
        ("irrigate", True, False): [
            "ಮಳೆ ನಿರೀಕ್ಷಿತ; ಮಣ್ಣು ಒಣಗಿದ್ದರೆ {when} {duration_hours} ಗಂಟೆ ಹಗುರ ನೀರಾವರಿ ನೀಡಿ."
        ],
        ("irrigate", True, True): [
            "ಮಳೆಯ ಮೊದಲು {when} {duration_hours} ಗಂಟೆ ಫರ್ಟಿಗೇಶನ್‌ ಸಹಿತ ನೀರಾವರಿ ಪೂರ್ಣಗೊಳಿಸಿ."
        ],
        ("skip_irrigation", True, False): [
            "ಮಳೆಯ ಸಾಧ್ಯತೆ ಇದೆ. ನೀರಾವರಿಯನ್ನು ಮುಂದೂಡಿ ಮತ್ತು ಮಣ್ಣಿನ ತೇವಾಂಶವನ್ನು ಪರಿಶೀಲಿಸಿ.",
            "ಮಳೆ ಬರಲಿದೆ; ಈಗ ನೀರಾವರಿ ಅಗತ್ಯವಿಲ್ಲ."
        ],
        ("skip_irrigation", True, True): [
            "ಮಳೆಯ ಕಾರಣ ನೀರಾವರಿ ಮತ್ತು ಗೊಬ್ಬರ ನೀಡುವುದನ್ನು ಮುಂದೂಡಿ, ಗೊಬ್ಬರ ಕೊಚ್ಚಿಹೋಗದಂತೆ ನೋಡಿಕೊಳ್ಳಿ."
        ],
        ("skip_irrigation", False, False): [
            "ಮಣ್ಣಿನಲ್ಲಿ ಸಾಕಷ್ಟು ತೇವಾಂಶ ಇದೆ. {when} ನೀರಾವರಿ ಅಗತ್ಯವಿಲ್ಲ.",
            "ಇಂದು ಮಣ್ಣು ಸಾಕಷ್ಟು ತೇವವಾಗಿದೆ; {when} ನೀರು ಕೊಡಬೇಡಿ."
        ],
        ("skip_irrigation", False, True): [
            "{when} ನೀರಾವರಿ ನಿಲ್ಲಿಸಿ. ಗೊಬ್ಬರವನ್ನು ಮುಂದಿನ ನಿಯಮಿತ ನೀರಾವರಿ ಜೊತೆ ಕೊಡಿ."
        ],
        ("delay_irrigation", False, False): [
            "{when} ವರೆಗೆ ನೀರಾವರಿ ಮುಂದೂಡಿ, ನಂತರ {duration_hours} ಗಂಟೆ ನೀರು ಕೊಡಿ."
        ],
        ("delay_irrigation", True, False): [
            "ಮಳೆ ನಿರೀಕ್ಷಿತ; {when} ವರೆಗೆ ನೀರಾವರಿ ಮುಂದೂಡಿ."
        ],
        ("light_irrigation", False, False): [
            "{when} {duration_hours} ಗಂಟೆ ಹಗುರ ನೀರಾವರಿ ನೀಡಿ."
        ],
    },
}


def render_advisory(record: dict, lang: str = "en", paraphrase_idx: int = 0) -> str:
    """
    Render an advisory sentence from a structured record.
    record keys: action, when, duration_hours, rain_expected, fertigation
    """
    action = record.get("action", "irrigate")
    when = record.get("when", "morning")
    duration = record.get("duration_hours", 2)
    rain = bool(record.get("rain_expected", False))
    fert = bool(record.get("fertigation", False))

    key = (action, rain, fert)

    # Pick the right template bank; fall back chain: localized -> HI/EN
    if lang in LOCALIZED_TEMPLATES:
        templates_dict = LOCALIZED_TEMPLATES[lang]
        # If specific key missing, fall back gracefully to EN
        fallback_dict = EN_TEMPLATES
    elif lang == "hi":
        templates_dict = HI_TEMPLATES
        fallback_dict = EN_TEMPLATES
    else:
        templates_dict = EN_TEMPLATES
        fallback_dict = EN_TEMPLATES

    candidates = templates_dict.get(key) or fallback_dict.get(key) or EN_TEMPLATES.get(("irrigate", False, False))
    template = candidates[paraphrase_idx % len(candidates)]

    # Translate the 'when' slot into the target language
    when_map = WHEN_MAP.get(lang, {})
    when_localized = when_map.get(str(when).lower(), str(when).replace("_", " "))

    return template.format(duration_hours=duration, when=when_localized)
