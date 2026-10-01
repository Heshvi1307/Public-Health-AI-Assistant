"""
tests/test_red_flags.py - Unit tests for deterministic multilingual red-flag prefilter.
"""
from safety.red_flags import scan_for_red_flags


def test_english_chest_pain_emergency():
    res = scan_for_red_flags("I have sudden severe chest pain and sweating", "en")
    assert res.is_red_flag is True
    assert res.flag_type == "emergency"
    assert "108" in str(res.helpline_numbers)


def test_hindi_chest_pain_emergency():
    res = scan_for_red_flags("मुझे सीने में दर्द हो रहा है", "hi")
    assert res.is_red_flag is True
    assert res.flag_type == "emergency"


def test_gujarati_chest_pain_emergency():
    res = scan_for_red_flags("મને છાતીમાં દુખાવો થાય છે", "gu")
    assert res.is_red_flag is True
    assert res.flag_type == "emergency"


def test_hinglish_emergency():
    res = scan_for_red_flags("chhati me dard hai aur behosh ho gaya tha", "en")
    assert res.is_red_flag is True
    assert res.flag_type == "emergency"


def test_breathing_difficulty_emergency():
    res = scan_for_red_flags("Severe difficulty breathing and gasping for air", "en")
    assert res.is_red_flag is True
    assert res.flag_type == "emergency"


def test_mental_health_crisis_english():
    res = scan_for_red_flags("I want to end my life, feeling completely hopeless", "en")
    assert res.is_red_flag is True
    assert res.flag_type == "mental_health"
    assert res.helpline_numbers.get("Tele-MANAS (Govt of India 24x7)") == "14416"


def test_mental_health_crisis_hindi():
    res = scan_for_red_flags("मैं आत्महत्या करना चाहता हूँ", "hi")
    assert res.is_red_flag is True
    assert res.flag_type == "mental_health"


def test_mental_health_crisis_gujarati():
    res = scan_for_red_flags("મને હવે જીવવું નથી", "gu")
    assert res.is_red_flag is True
    assert res.flag_type == "mental_health"


def test_routine_symptoms_not_red_flag():
    res = scan_for_red_flags("I have a runny nose and slight scratchy throat", "en")
    assert res.is_red_flag is False
