import streamlit as st
import requests
import hashlib
from zxcvbn import zxcvbn
import random
import string

st.set_page_config(page_title="بوابة فحص كلمات المرور", page_icon="🔐")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("nu_logo.png", use_container_width=True)
    except:
        pass

def translate_time(time_str):
    translations = {
        "less than a second": "أقل من ثانية", "seconds": "ثواني", "second": "ثانية",
        "minutes": "دقائق", "minute": "دقيقة", "hours": "ساعات", "hour": "ساعة",
        "days": "أيام", "day": "يوم", "months": "أشهر", "month": "شهر",
        "years": "سنوات", "year": "سنة", "centuries": "قرون", "century": "قرن"
    }
    for eng, ar in translations.items():
        time_str = time_str.replace(eng, ar)
    return time_str

def check_pwned_password(password):
    sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    first5_chars, tail = sha1_password[:5], sha1_password[5:]
    try:
        response = requests.get(f'https://api.pwnedpasswords.com/range/{first5_chars}', timeout=5)
        if response.status_code != 200:
            return -1
        hashes = (line.split(':') for line in response.text.splitlines())
        for h, count in hashes:
            if h == tail:
                return int(count)
        return 0
    except requests.exceptions.RequestException:
        return -1

def generate_academic_password():
    lower_letters = ''.join(random.choices(string.ascii_lowercase, k=4))
    digits = ''.join(random.choices(string.digits, k=4))
    first_two_upper = lower_letters[:2].upper()
    return f"{lower_letters}{digits}{first_two_upper}@"

st.title("بوابة فحص أمان كلمات المرور 🔐")
st.write("أداة سيبرانية متقدمة لتحليل قوة كلمات المرور والتحقق من تسريبها.")

password = st.text_input("أدخل كلمة المرور هنا لفحصها:", type="password")

if password:
    st.write("---")
    
    result = zxcvbn(password)
    score = result['score'] 
    raw_crack_time = result['crack_times_display']['offline_slow_hashing_1e4_per_second']
    crack_time = translate_time(raw_crack_time)
    
    st.subheader("📊 تحليل متانة الكلمة:")
    st.progress((score + 1) / 5)
    
    if score <= 1:
        st.error(f"⚠️ التقييم: ضعيفة جداً! \n\n ⏱️ الوقت المتوقع لكسرها: **{crack_time}**")
    elif score == 2:
        st.warning(f"⚠️ التقييم: متوسطة. \n\n ⏱️ الوقت المتوقع لكسرها: **{crack_time}**")
    elif score == 3:
        st.info(f"✅ التقييم: جيدة. \n\n ⏱️ الوقت المتوقع لكسرها: **{crack_time}**")
    else:
        st.success(f"🛡️ التقييم: قوية جداً! \n\n ⏱️ سيستغرق المخترق لكسرها: **{crack_time}**")
        
    st.write("---")
    st.subheader("🔍 فحص التسريبات العالمية (Data Breaches):")
    
    with st.spinner("جاري الاتصال بقواعد البيانات المشفرة..."):
        leak_count = check_pwned_password(password)
        
    if leak_count == -1:
        st.warning("⚠️ تعذر الاتصال بقاعدة بيانات التسريبات العالمية. تم فحص قوة الكلمة محلياً بنجاح.")
    elif leak_count > 0:
        st.error(f"🚨 تحذير خطير: هذه الكلمة تم تسريبها **{leak_count}** مرة في اختراقات سابقة! لا تستخدمها أبداً.")
    else:
        st.success("✅ أمان تام: لم يتم العثور على هذه الكلمة في أي تسريبات معروفة.")

st.write("---")
st.subheader("🛡️ مولد كلمات المرور ")
st.write("توليد كلمة مرور بنفس نمط الحسابات الجامعية والأنظمة الأكاديمية:")

if st.button("✨ توليد كلمة مرور "):
    new_pass = generate_academic_password()
    st.success(f"كلمة المرور المقترحة:  `{new_pass}`")
