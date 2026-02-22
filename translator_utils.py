from deep_translator import GoogleTranslator
import streamlit as st

# supported languages
LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Marathi": "mr",
    "Spanish": "es",
    "French": "fr",
    "German": "de"
}

@st.cache_data
def translate_text(text, target_lang="en"):
    if target_lang == "en" or not text:
        return text
    
    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return text

# Dictionary for common UI elements to avoid API calls for every render
UI_TRANSLATIONS = {
    "hi": {
        "Flight Disruption Recovery Assistant": "उड़ान व्यवधान बहाली सहायक",
        "Your AI-powered solution for flight cancellations and delays": "उड़ान रद्द होने और देरी के लिए आपका AI-संचालित समाधान",
        "Flights Available": "उपलब्ध उड़ानें",
        "How to use": "कैसे उपयोग करें",
        "Chat Mode": "चैट मोड",
        "Recovery Mode": "रिकवरी मोड",
        "Why this flight?": "यही उड़ान क्यों?",
        "Example Queries": "उदाहरण प्रश्न",
        "DISRUPTION MODE": "व्यवधान मोड",
        "LIVE DATA": "लाइव डेटा",
        "Sync Live Planes": "लाइव विमान सिंक करें",
        "Data Source Filter": "डेटा स्रोत फ़िल्टर",
        "Enter flight ID": "फ्लाइट आईडी दर्ज करें",
        "Find Alternatives": "विकल्प खोजें",
        "Ask about flights...": "उड़ानों के बारे में पूछें...",
        "💡 Why this flight?": "💡 यही उड़ान क्यों?",
        "Enter flight ID": "फ्लाइट आईडी दर्ज करें",
        "All": "सभी",
        "Live Only": "केवल लाइव",
        "Fake Only": "केवल नकली (Fake)",
        "Sync had errors": "सिंक में त्रुटियां थीं",
        "Synced": "सिंक किया गया",
        "aircraft": "विमान",
        "flights": "उड़ानें",
        "Sync failed": "सिंक विफल रहा",
        "Seats": "सीटें",
        "Weather Risk": "मौसम जोखिम",
        "Delay Risk": "देरी का जोखिम",
        "Price": "मूल्य",
        "Plenty": "भरपूर",
        "Limited": "सीमित",
        "Scarce": "बहुत कम",
        "Accessible": "सुलभ (Accessible)",
        "Low": "कम",
        "Medium": "मध्यम",
        "High": "उच्च"
    },
    "mr": {
        "Flight Disruption Recovery Assistant": "विमान फेरबदल निवारण सहाय्यक",
        "Your AI-powered solution for flight cancellations and delays": "विमान रद्द होणे आणि विलंबासाठी तुमचे AI-आधारित समाधान",
        "Flights Available": "उपलब्ध विमान फेऱ्या",
        "How to use": "कसे वापरावे",
        "Chat Mode": "चैट मोड",
        "Recovery Mode": "रिकव्हरी मोड",
        "Why this flight?": "हीच विमान फेरी का?",
        "Example Queries": "नमुना प्रश्न",
        "DISRUPTION MODE": "व्यत्यय मोड",
        "LIVE DATA": "लाइव डेटा",
        "Sync Live Planes": "थेट विमान माहिती मिळवा",
        "Data Source Filter": "डेटा स्रोत फिल्टर",
        "Enter flight ID": "विमान क्रमांक टाका",
        "Find Alternatives": "पर्याय शोधा",
        "Ask about flights...": "विमानांबद्दल विचारा...",
        "💡 Why this flight?": "💡 हीच विमान फेरी का?",
        "All": "सर्व",
        "Live Only": "फक्त लाइव्ह",
        "Fake Only": "फक्त डमी (Fake)",
        "Seats": "जागा",
        "Weather Risk": "हवामान जोखीम",
        "Delay Risk": "विलंब जोखीम",
        "Price": "किंमत",
        "Plenty": "भरपूर",
        "Limited": "मर्यादित",
        "Scarce": "दुर्मिळ",
        "Accessible": "सुलभ (Accessible)",
        "Low": "कमी",
        "Medium": "मध्यम",
        "High": "उच्च"
    }
}

def get_text(text, target_lang="en"):
    if target_lang == "en":
        return text
    
    # Check dictionary first
    if target_lang in UI_TRANSLATIONS and text in UI_TRANSLATIONS[target_lang]:
        return UI_TRANSLATIONS[target_lang][text]
    
    # Fallback to API translation
    return translate_text(text, target_lang)
