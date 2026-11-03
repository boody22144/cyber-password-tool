import streamlit as st
import requests
import hashlib
from zxcvbn import zxcvbn
import secrets
import string
import random 

# 1. إعدادات الصفحة
st.set_page_config(page_title="بوابة فحص كلمات المرور", page_icon="🔐")

# 2. شعار جامعة نجران
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("nu_logo.png", use_container_width=True)

# 3. دالة فحص التسريبات
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
def translate_time(time_str):
    translations = {
        "less than a second": "أقل من ثانية",
        "seconds": "ثواني",
        "second": "ثانية",
        "minutes": "دقائق",
        "minute": "دقيقة",
        "hours": "ساعات",
        "hour": "ساعة",
        "days": "أيام",
        "day": "يوم",
        "months": "أشهر",
        "month": "شهر",
        "years": "سنوات",
        "year": "سنة",
        "centuries": "قرون",
        "century": "قرن"
    }
    for eng, ar in translations.items():
        time_str = time_str.replace(eng, ar)
    return time_str
# 4. دالة توليد كلمة مرور معقدة
def generate_strong_password():
    # قائمة كلمات مألوفة (يمكنك تعديلها وإضافة كلماتك المفضلة)
    words = ["Shadow", "Ryze", "Linux", "Falcon", "River", "Moon", "Tiger", "Ocean", 
             "Iron", "Eagle", "Silver", "Mountain", "Thunder", "Desert", "Storm", 
             "Winter", "Knight", "Dragon", "Castle", "Shield", "Nexus"]
    
    # اختيار 3 كلمات عشوائية
    selected_words = random.sample(words, 3)
    
    # إضافة رقم عشوائي ورمز بسيط لتجاوز شروط التعقيد في أغلب المواقع
    number = random.randint(10, 99)
    symbol = random.choice(["!", "@", "#", "$", "*"])
    
    # دمج الكلمات برمز الـ (Dash) لتسهيل القراءة
    passphrase = "-".join(selected_words) + f"-{number}{symbol}"
    return passphrase

# 5. واجهة المستخدم الأساسية
st.title("بوابة فحص أمان كلمات المرور 🔐")
st.write("أداة سيبرانية متقدمة لتحليل قوة كلمات المرور والتحقق من تسريبها في قواعد بيانات الاختراقات العالمية.")

# قسم إدخال الكلمة
password = st.text_input("أدخل كلمة المرور هنا لفحصها:", type="password")

if password:
    st.write("---")
    
    # تحليل قوة الكلمة
   # تحليل قوة الكلمة
    result = zxcvbn(password)
    score = result['score'] 
    raw_crack_time = result['crack_times_display']['offline_slow_hashing_1e4_per_second']
    crack_time = translate_time(raw_crack_time) # تمرير الوقت للترجمة
    
    st.subheader("📊 تحليل متانة الكلمة:")
    st.progress((score + 1) / 5)
    
    # فصل التقييم عن الوقت باستخدام \n\n لترتيب أفضل
    if score == 0 or score == 1:
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

# 6. قسم توليد كلمات المرور الجديدة
st.write("---")
st.subheader("🛡️ مولد كلمات المرور الآمنة")
st.write("هل تحتاج إلى كلمة مرور قوية لا يمكن اختراقها؟")

if st.button("توليد كلمة مرور سهلة الحفظ"):
    new_password = generate_strong_password() 
    st.info(f"كلمة المرور المقترحة: **{new_password}**")
    st.caption("هذه الكلمة تسمى (Passphrase) وهي تعتمد على الطول لتعقيد الاختراق، وسهولة الكلمات لتسهيل الحفظ ذهنياً.")