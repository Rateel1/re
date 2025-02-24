
import streamlit as st
import joblib
import pandas as pd
import folium
from streamlit_folium import st_folium
from PIL import Image

# Set up the page configuration
st.set_page_config(page_title="لوحة المعلومات العقارية ", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for styling
st.markdown("""
<style>
.stApp {
    background-color: #f0f2f6;
}
.stButton>button {
    color: #ffffff;
    background-color: #4CAF50;
    border-radius: 5px;
}
.stMetricLabel {
    font-size: 20px;
}
.stMetricValue {
    font-size: 40px;
    color: #4CAF50;
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    return joblib.load("lgbm.joblib")

model = load_model()

# Relevant features for prediction
relevant_features = [
    'beds', 'livings', 'wc', 'area', 'street_width', 'age', 'street_direction', 'ketchen',
    'furnished', 'location.lat', 'location.lng', 'city_id', 'district_id'
]

# Prediction function
def predict_price(new_record):
    new_record_df = pd.DataFrame([new_record])
    new_record_df = pd.get_dummies(new_record_df, drop_first=True)
    new_record_df = new_record_df.reindex(columns=relevant_features, fill_value=0)
    return model.predict(new_record_df)[0]

# Initialize session state for location
if 'location_lat' not in st.session_state:
    st.session_state['location_lat'] = 24.7136
if 'location_lng' not in st.session_state:
    st.session_state['location_lng'] = 46.6753

# Main application
st.title("🏠  لوحة المعلومات العقارية  ")

# Create layout for the dashboard
col1, col2 = st.columns(2)

# Column 1: Map and Location Selection
with col1:
    st.subheader("📍 اختر الموقع")
    # Folium map
    m = folium.Map(location=[st.session_state['location_lat'], st.session_state['location_lng']], zoom_start=6)
    marker = folium.Marker(
        location=[st.session_state['location_lat'], st.session_state['location_lng']],
        draggable=True
    )
    marker.add_to(m)
    map_data = st_folium(m, width=700, height=400)
    if map_data['last_clicked']:
        st.session_state['location_lat'] = map_data['last_clicked']['lat']
        st.session_state['location_lng'] = map_data['last_clicked']['lng']
    st.write(f"الموقع المحدد: {st.session_state['location_lat']:.4f}, {st.session_state['location_lng']:.4f}")

# Column 2: Input Form
with col2:
    st.subheader("🏠 أدخل تفاصيل المنزل")
    # Manual location input
    st.subheader("📍 إدخال الموقع يدويًا")
    manual_lat = st.number_input("أدخل خط العرض:", value=st.session_state['location_lat'], format="%.6f")
    manual_lng = st.number_input("أدخل خط الطول:", value=st.session_state['location_lng'], format="%.6f")
    if manual_lat and manual_lng:
        st.session_state['location_lat'] = manual_lat
        st.session_state['location_lng'] = manual_lng
        st.write(f"الموقع المدخل يدويًا: {manual_lat:.4f}, {manual_lng:.4f}")

    # Create a form for house details
    with st.form("house_details_form"):
        # Create uniform input fields
        col_a, col_b = st.columns(2)
        with col_a:
            beds = st.slider("عدد غرف النوم 🛏️", 1, 10, 3)
            livings = st.slider("عدد غرف المعيشة 🛋️", 1, 5, 1)
            wc = st.slider(" عدد دورات المياه 🚽", 1, 5, 2)
            area = st.number_input("المساحة (متر مربع) 📏", 50.0, 1000.0, 150.0)
        with col_b:
            # Replace the existing street_width input with a selectbox
            street_width = st.selectbox("عرض الشارع (متر) 🛣️", [10, 12, 15, 18, 20, 25], index=2)  # Default to 20


            age = st.number_input(" عمر العقار 🗓️", 0, 100, 5)
            street_direction = st.selectbox(" نوع الواجهة 🧭", [
    " واجهة شمالية",
    " واجهة شرقية",
    " واجهة غربية",
    " واجهة جنوبية",
    " واجهة شمالية شرقية",
    " واجهة جنوبية شرقية",
    " واجهة جنوبية غربية",
    " واجهة شمالية غربية",
    " الفلة تقع على ثلاثة شوارع",
    " الفلة تقع على أربعة شوارع"
])



            ketchen = st.selectbox("وجود المطبخ 🍳", [0, 1], format_func=lambda x: "نعم" if x == 1 else "لا")
            furnished = st.selectbox("الفلة مؤثثة 🪑", [0, 1], format_func=lambda x: "نعم" if x == 1 else "لا")

        # District selection
        city_name_to_id = {
            'جدة': 21,
            'الرياض': 66,
            'الخبر': 12,
            'الدمام': 18,
        }
        district_data = [
    (3440, 'حي الاندلس', 'جدة'),
    (470, 'حي السويدي', 'الرياض'),
    (692, 'حي عتيقة', 'الرياض'),
    (1228, 'حي الريان', 'الدمام'),
    (474, 'حي الشرفية', 'الرياض'),
    (1284, 'حي المزروعية', 'الدمام'),
    (1208, 'حي الجوهرة', 'الدمام'),
    (3558, 'حي الفيصلية', 'جدة'),
    (3428, 'حي الاجاويد', 'جدة'),
    (1080, 'حي الراكة الجنوبية', 'الخبر'),
    (1054, 'حي البندرية', 'الخبر'),
    (606, 'حي النسيم الغربي', 'الرياض'),
    (1278, 'حي المحمدية', 'الدمام'),
    (3554, 'حي الفلاح', 'جدة'),
    (3550, 'حي الفضل', 'جدة'),
    (590, 'حي المونسية', 'الرياض'),
    (1244, 'حي الشعلة', 'الدمام'),
    (448, 'حي الرماية', 'الرياض'),
    (3508, 'حي السلامة', 'جدة'),
    (3530, 'حي الصناعية', 'جدة'),
    (514, 'حي الغدير', 'الرياض'),
    (718, 'حي نمار', 'الرياض'),
    (1102, 'حي الكورنيش', 'الخبر'),
    (622, 'حي الوادي', 'الرياض'),
    (616, 'حي النور', 'الرياض'),
    (1052, 'حي البستان', 'الخبر'),
    (1322, 'حي غرناطة', 'الدمام'),
    (3450, 'حي البغدادية الغربية', 'جدة'),
    (1268, 'حي الفنار', 'الدمام'),
    (1072, 'حي الخبر الجنوبية', 'الخبر'),
    (3584, 'حي المرجان', 'جدة'),
    (542, 'حي المربع', 'الرياض'),
    (1290, 'حي المنتزه', 'الدمام'),
    (1270, 'حي الفيحاء', 'الدمام'),
    (416, 'حي الحمراء', 'الرياض'),
    (3594, 'حي المنتزه', 'جدة'),
    (504, 'حي العقيق', 'الرياض'),
    (1056, 'حي التحلية', 'الخبر'),
    (604, 'حي النسيم الشرقي', 'الرياض'),
    (1274, 'حي القادسية', 'الدمام'),
    (568, 'حي الملز', 'الرياض'),
    (3574, 'حي المتنزهات', 'جدة'),
    (3536, 'حي العدل', 'جدة'),
    (2436, 'حي الريان', 'رياض الخبراء'),
    (548, 'حي المروج', 'الرياض'),
    (1302, 'حي النسيم', 'الدمام'),
    (658, 'حي جامعة الملك سعود', 'الرياض'),
    (3602, 'حي النزهة', 'جدة'),
    (424, 'حي الدار البيضاء', 'الرياض'),
    (3642, 'حي مدائن الفهد', 'جدة'),
    (3478, 'حي الرحاب', 'جدة'),
    (3470, 'حي الحمراء', 'جدة'),
    (3446, 'حي البشائر', 'جدة'),
    (1076, 'حي الخزامى', 'الخبر'),
    (492, 'حي الضباط', 'الرياض'),
    (3462, 'حي الثغر', 'جدة'),
    (1314, 'حي جامعة الدمام', 'الدمام'),
    (3488, 'حي الرويس', 'جدة'),
    (2448, 'حي القدس', 'رياض الخبراء'),
    (3538, 'حي العزيزية', 'جدة'),
    (3498, 'حي الساحل', 'جدة'),
    (3468, 'حي الحمدانية', 'جدة'),
    (3600, 'حي النزلة اليمانية', 'جدة'),
    (1320, 'حي عبدالله فؤاد', 'الدمام'),
    (688, 'حي ظهرة لبن', 'الرياض'),
    (3424, 'حي ابحر الشمالية', 'جدة'),
    (3510, 'حي السليمانية', 'جدة'),
    (532, 'حي القدس', 'الرياض'),
    (1282, 'حي المريكبات', 'الدمام'),
    (1112, 'حي الهدا', 'الخبر'),
    (496, 'حي العريجاء', 'الرياض'),
    (1230, 'حي الزهور', 'الدمام'),
    (418, 'حي الخالدية', 'الرياض'),
    (436, 'حي الرائد', 'الرياض'),
    (1264, 'حي الفردوس', 'الدمام'),
    (3526, 'حي الصحيفة', 'جدة'),
    (612, 'حي النموذجية', 'الرياض'),
    (3512, 'حي السنابل', 'جدة'),
    (410, 'حي الجنادرية', 'الرياض'),
    (682, 'حي طويق', 'الرياض'),
    (3494, 'حي الزمرد', 'جدة'),
    (1252, 'حي الضباب', 'الدمام'),
    (510, 'حي العمل', 'الرياض'),
    (3624, 'حي ام السلم', 'جدة'),
    (3514, 'حي الشاطئ', 'جدة'),
    (706, 'حي قرطبة', 'الرياض'),
    (588, 'حي المهدية', 'الرياض'),
    (690, 'حي ظهرة نمار', 'الرياض'),
    (536, 'حي القيروان', 'الرياض'),
    (3490, 'حي الرياض', 'جدة'),
    (644, 'حي ام سليم', 'الرياض'),
    (516, 'حي الغنامية', 'الرياض'),
    (1324, 'حي قصر الخليج', 'الدمام'),
    (716, 'حي منفوحة الجديدة', 'الرياض'),
    (1108, 'حي المرجان', 'الخبر'),
    (530, 'حي القادسية', 'الرياض'),
    (1246, 'حي الصدفة', 'الدمام'),
    (3444, 'حي البساتين', 'جدة'),
    (554, 'حي المصفاة', 'الرياض'),
    (3516, 'حي الشراع', 'جدة'),
    (398, 'حي البديعة', 'الرياض'),
    (3622, 'حي الياقوت', 'جدة'),
    (3432, 'حي الامواج', 'جدة'),
    (3646, 'حي مريخ', 'جدة'),
    (582, 'حي المنار', 'الرياض'),
    (662, 'حي جرير', 'الرياض'),
    (1218, 'حي الدانة', 'الدمام'),
    (1092, 'حي الصواري', 'الخبر'),
    (3438, 'حي الاميرعبدالمجيد', 'جدة'),
    (566, 'حي المغرزات', 'الرياض'),
    (526, 'حي الفيحاء', 'الرياض'),
    (3582, 'حي المدينة الصناعية الثانية', 'جدة'),
    (714, 'حي منفوحة', 'الرياض'),
    (2454, 'حي النهضة', 'رياض الخبراء'),
    (586, 'حي المنصورية', 'الرياض'),
    (3546, 'حي الفردوس', 'جدة'),
    (1096, 'حي العقيق', 'الخبر'),
    (442, 'حي الرحمانية', 'الرياض'),
    (1100, 'حي الكوثر', 'الخبر'),
    (3648, 'حي مشرفة', 'جدة'),
    (392, 'حي الازدهار', 'الرياض'),
    (574, 'حي الملك عبدالله', 'الرياض'),
    (2430, 'حي الربيع', 'رياض الخبراء'),
    (684, 'حي طيبة', 'الرياض'),
    (3442, 'حي البركة', 'جدة'),
    (3486, 'حي الروضة', 'جدة'),
    (3588, 'حي المسرة', 'جدة'),
    (1192, 'حي الانوار', 'الدمام'),
    (488, 'حي الصفا', 'الرياض'),
    (708, 'حي لبن', 'الرياض'),
    (1088, 'حي السفن', 'الخبر'),
    (646, 'حي أحد', 'الرياض'),
    (1098, 'حي العليا', 'الخبر'),
    (1106, 'حي المدينة الرياضية', 'الخبر'),
    (520, 'حي الفاروق', 'الرياض'),
    (3504, 'حي السروات', 'جدة'),
    (698, 'حي عكاظ', 'الرياض'),
    (614, 'حي النهضة', 'الرياض'),
    (1318, 'حي طيبة', 'الدمام'),
    (572, 'حي الملك عبدالعزيز', 'الرياض'),
    (1236, 'حي السيف', 'الدمام'),
    (578, 'حي الملك فيصل', 'الرياض'),
    (1204, 'حي الجامعيين', 'الدمام'),
    (1120, 'حي مدينة العمال', 'الخبر'),
    (3618, 'حي الورود', 'جدة'),
    (1238, 'حي الشاطئ الشرقي', 'الدمام'),
    (1070, 'حي الحمرا', 'الخبر'),
    (1110, 'حي المها', 'الخبر'),
    (1104, 'حي اللؤلؤ', 'الخبر'),
    (1256, 'حي العدامة', 'الدمام'),
    (458, 'حي الزهرة', 'الرياض'),
    (1118, 'حي قرطبة', 'الخبر'),
    (712, 'حي مطار الملك خالد الدولي', 'الرياض'),
    (1082, 'حي الرجاء', 'الخبر'),
    (672, 'حي سلطانة', 'الرياض'),
    (618, 'حي الهدا', 'الرياض'),
    (524, 'حي الفوطة', 'الرياض'),
    (518, 'حي الفاخرية', 'الرياض'),
    (506, 'حي العليا', 'الرياض'),
    (3464, 'حي الجامعة', 'جدة'),
    (3458, 'حي التعاون', 'جدة'),
    (3644, 'حي مدينة الملك عبدالعزيز الطبية', 'جدة'),
    (1286, 'حي المطار', 'الدمام'),
    (674, 'حي شبرا', 'الرياض'),
    (444, 'حي الرفيعة', 'الرياض'),
    (1084, 'حي الروابي', 'الخبر'),
    (1044, 'حي الامواج', 'الخبر'),
    (404, 'حي التعاون', 'الرياض'),
    (2456, 'حي الياسمين', 'رياض الخبراء'),
    (1040, 'حي اشبيليا', 'الخبر'),
    (3592, 'حي المنار', 'جدة'),
    (1316, 'حي ضاحية الملك فهد', 'الدمام'),
    (592, 'حي المؤتمرات', 'الرياض'),
    (1046, 'حي الاندلس', 'الخبر'),
    (450, 'حي الروابي', 'الرياض'),
    (422, 'حي الخليج', 'الرياض'),
    (632, 'حي الياسمين', 'الرياض'),
    (3466, 'حي الجوهرة', 'جدة'),
    (1210, 'حي الحمراء', 'الدمام'),
    (558, 'حي المعذر', 'الرياض'),
    (624, 'حي الورود', 'الرياض'),
    (3492, 'حي الريان', 'جدة'),
    (546, 'حي المروة', 'الرياض'),
    (478, 'حي الشفا', 'الرياض'),
    (396, 'حي الاندلس', 'الرياض'),
    (494, 'حي العارض', 'الرياض'),
    (3586, 'حي المروة', 'جدة'),
    (2446, 'حي القادسية', 'رياض الخبراء'),
    (1188, 'حي الامانة', 'الدمام'),
    (3528, 'حي الصفا', 'جدة'),
    (3626, 'حي ام حبلين', 'جدة'),
    (598, 'حي الندى', 'الرياض'),
    (1216, 'حي الخليج', 'الدمام'),
    (446, 'حي الرمال', 'الرياض'),
    (3426, 'حي ابرق الرغامة', 'جدة'),
    (676, 'حي صلاح الدين', 'الرياض'),
    (3606, 'حي النعيم', 'جدة'),
    (502, 'حي العزيزية', 'الرياض'),
    (602, 'حي النزهة', 'الرياض'),
    (1272, 'حي الفيصلية', 'الدمام'),
    (570, 'حي الملقا', 'الرياض'),
    (620, 'حي الواحة', 'الرياض'),
    (3604, 'حي النسيم', 'جدة'),
    (680, 'حي ضاحية نمار', 'الرياض'),
    (420, 'حي الخزامى', 'الرياض'),
    (3502, 'حي السبيل', 'جدة'),
    (456, 'حي الزهراء', 'الرياض'),
    (710, 'حي مركز الملك عبدالله للدراسات والبحوث', 'الرياض'),
    (2422, 'حي الحزم', 'رياض الخبراء'),
    (428, 'حي الدريهمية', 'الرياض'),
    (3608, 'حي النهضة', 'جدة'),
    (3422, 'حي ابحر الجنوبية', 'جدة'),
    (1212, 'حي الخالدية الشمالية', 'الدمام'),
    (1050, 'حي البحيرة', 'الخبر'),
    (3562, 'حي القرينة', 'جدة'),
    (1288, 'حي المنار', 'الدمام'),
    (3640, 'حي قاعدة الملك فيصل البحرية', 'جدة'),
    (1298, 'حي الندى', 'الدمام'),
    (464, 'حي السلام', 'الرياض'),
    (3650, 'حي مطار الملك عبدالعزيز الدولي', 'جدة'),
    (2426, 'حي الخزان', 'رياض الخبراء'),
    (3610, 'حي الهدى', 'جدة'),
    (2434, 'حي الروضة', 'رياض الخبراء'),
    (3638, 'حي طيبة', 'جدة'),
    (3572, 'حي اللؤلؤ', 'جدة'),
    (2418, 'حي الاندلس', 'رياض الخبراء'),
    (3476, 'حي الربوة', 'جدة'),
    (564, 'حي المعيزلة', 'الرياض'),
    (522, 'حي الفلاح', 'الرياض'),
    (1258, 'حي العزيزية', 'الدمام'),
    (560, 'حي المعذر الشمالي', 'الرياض'),
    (3598, 'حي النزلة الشرقية', 'جدة'),
    (538, 'حي المحمدية', 'الرياض'),
    (3552, 'حي الفضيلة', 'جدة'),
    (3484, 'حي الروابي', 'جدة'),
    (528, 'حي الفيصلية', 'الرياض'),
    (3578, 'حي المحمدية', 'جدة'),
    (550, 'حي المشاعل', 'الرياض'),
    (3454, 'حي البوادي', 'جدة'),
    (1062, 'حي الجسر', 'الخبر'),
    (3506, 'حي السرورية', 'جدة'),
    (3436, 'حي الامير فواز الشمالي', 'جدة'),
    (3472, 'حي الخالدية', 'جدة'),
    (1312, 'حي بدر', 'الدمام'),
    (3564, 'حي القوزين', 'جدة'),
    (1330, 'حي ميناء الملك عبدالعزيز', 'الدمام'),
    (694, 'حي عرقة', 'الرياض'),
    (3596, 'حي النخيل', 'جدة'),
    (1262, 'حي العنود', 'الدمام'),
    (1200, 'حي البديع', 'الدمام'),
    (668, 'حي ديراب', 'الرياض'),
    (460, 'حي السعادة', 'الرياض'),
    (3570, 'حي الكوثر', 'جدة'),
    (696, 'حي عريض', 'الرياض'),
    (1048, 'حي البحر', 'الخبر'),
    (1066, 'حي الحزام الاخضر', 'الخبر'),
    (1068, 'حي الحزام الذهبي', 'الخبر'),
    (3632, 'حي بريمان', 'جدة'),
    (652, 'حي ثليم', 'الرياض'),
    (686, 'حي ظهرة البديعة', 'الرياض'),
    (3614, 'حي الواحة', 'جدة'),
    (1296, 'حي النخيل', 'الدمام'),
    (1300, 'حي النزهة', 'الدمام'),
    (1196, 'حي البادية', 'الدمام'),
    (580, 'حي المناخ', 'الرياض'),
    (3532, 'حي الصوارى', 'جدة'),
    (3518, 'حي الشرفية', 'جدة'),
    (3634, 'حي بني مالك', 'جدة'),
    (656, 'حي جامعة الأميرة نورة', 'الرياض'),
    (400, 'حي البرية', 'الرياض'),
    (640, 'حي ام الحمام الغربي', 'الرياض'),
    (3448, 'حي البغدادية الشرقية', 'جدة'),
    (552, 'حي المصانع', 'الرياض'),
    (1240, 'حي الشاطئ الغربي', 'الدمام'),
    (3520, 'حي الشروق', 'جدة'),
    (1178, 'حي ابن خلدون', 'الدمام'),
    (1308, 'حي النورس', 'الدمام'),
    (3452, 'حي البلد', 'جدة'),
    (3430, 'حي الاصالة', 'جدة'),
    (704, 'حي غرناطة', 'الرياض'),
    (3524, 'حي الصالحية', 'جدة'),
    (3434, 'حي الامير فواز الجنوبي', 'جدة'),
    (1306, 'حي النور', 'الدمام'),
    (3540, 'حي العمارية', 'جدة'),
    (452, 'حي الروضة', 'الرياض'),
    (3636, 'حي جامعة الملك عبدالعزيز', 'جدة'),
    (1232, 'حي السلام', 'الدمام'),
    (600, 'حي النرجس', 'الرياض'),
    (654, 'حي جامعة الامام محمد بن سعود الاسلامية', 'الرياض'),
    (394, 'حي الاسكان', 'الرياض'),
    (482, 'حي الشهداء', 'الرياض'),
    (576, 'حي الملك فهد', 'الرياض'),
    (1064, 'حي الجوهرة', 'الخبر'),
    (486, 'حي الصحافة', 'الرياض'),
    (666, 'حي خشم العان', 'الرياض'),
    (1226, 'حي الروضة', 'الدمام'),
    (1060, 'حي الثقبة', 'الخبر'),
    (626, 'حي الوزارات', 'الرياض'),
    (2440, 'حي السحابين الشمالي', 'رياض الخبراء'),
    (1310, 'حي الهضبة', 'الدمام'),
    (440, 'حي الربيع', 'الرياض'),
    (650, 'حي بنبان', 'الرياض'),
    (1180, 'حي احد', 'الدمام'),
    (466, 'حي السلي', 'الرياض'),
    (3630, 'حي بحرة', 'جدة'),
    (3496, 'حي الزهراء', 'جدة'),
    (1194, 'حي الأمل', 'الدمام'),
    (584, 'حي المنصورة', 'الرياض'),
    (438, 'حي الربوة', 'الرياض'),
    (1114, 'حي اليرموك', 'الخبر'),
    (408, 'حي الجزيرة', 'الرياض'),
    (1074, 'حي الخبر الشمالية', 'الخبر'),
    (1058, 'حي التعاون', 'الخبر'),
    (3556, 'حي الفيحاء', 'جدة'),
    (608, 'حي النظيم', 'الرياض'),
    (596, 'حي النخيل', 'الرياض'),
    (390, 'حي اشبيلية', 'الرياض'),
    (412, 'حي الحائر', 'الرياض'),
    (1326, 'حي مدينة العمال', 'الدمام'),
    (406, 'حي الجرادية', 'الرياض'),
    (3474, 'حي الخمرة', 'جدة'),
    (3500, 'حي السامر', 'جدة'),
    (610, 'حي النفل', 'الرياض'),
    (1304, 'حي النهضة', 'الدمام'),
    (476, 'حي الشرق', 'الرياض'),
    (648, 'حي بدر', 'الرياض'),
    (1184, 'حي الاتصالات', 'الدمام'),
    (1280, 'حي المدينة الصناعية الثانية', 'الدمام'),
    (544, 'حي المرسلات', 'الرياض'),
    (472, 'حي السويدي الغربي', 'الرياض'),
    (3612, 'حي الهندواية', 'جدة'),
    (1094, 'حي العقربية', 'الخبر'),
    (1254, 'حي الطبيشي', 'الدمام'),
    (636, 'حي اليمامة', 'الرياض'),
    (540, 'حي المدينة الصناعية الجديدة', 'الرياض'),
    (454, 'حي الريان', 'الرياض'),
    (1206, 'حي الجلوية', 'الدمام'),
    (1242, 'حي الشرق', 'الدمام'),
    (3548, 'حي الفروسية', 'جدة'),
    (634, 'حي اليرموك', 'الرياض'),
    (556, 'حي المصيف', 'الرياض'),
    (3522, 'حي الشفا', 'جدة'),
    (660, 'حي جبرة', 'الرياض'),
    (468, 'حي السليمانية', 'الرياض'),
    (630, 'حي الوشام', 'الرياض'),
    (2450, 'حي المجد', 'رياض الخبراء'),
    (2452, 'حي النزهة', 'رياض الخبراء'),
    (498, 'حي العريجاء الغربية', 'الرياض'),
    (490, 'حي الصناعية', 'الرياض'),
    (500, 'حي العريجاء الوسطى', 'الرياض'),
    (700, 'حي عليشة', 'الرياض'),
    (702, 'حي غبيرة', 'الرياض'),
    (638, 'حي ام الحمام الشرقي', 'الرياض'),
    (1090, 'حي الشراع', 'الخبر'),
    (664, 'حي حطين', 'الرياض'),
    (3480, 'حي الرحمانية', 'جدة'),
    (3542, 'حي الغليل', 'جدة'),
    (1266, 'حي الفرسان', 'الدمام'),
    (414, 'حي الحزم', 'الرياض'),
]
       
        selected_district = st.selectbox(
            "اختر الحي 🏙️",
            district_data,
            format_func=lambda x: f"{x[1]} ({x[2]})"
        )
        district_id = selected_district[0]
        city_id = city_name_to_id[selected_district[2]]

        # Submit button
        submitted = st.form_submit_button("🔮 توقع السعر")
        if submitted:
            with st.spinner('جاري الحساب...'):
                new_record = {
                    'beds': beds, 'livings': livings, 'wc': wc, 'area': area,
                    'street_width': street_width,  # Updated to be a list

                    'age': age, 'street_direction': street_direction,
                    'ketchen': ketchen, 'furnished': furnished,
                    'location.lat': st.session_state['location_lat'],
                    'location.lng': st.session_state['location_lng'],
                    'city_id': city_id, 'district_id': district_id
                }
                predicted_price = predict_price(new_record)
            st.success('تمت عملية التوقع بنجاح!')
            st.metric(label=" السعر التقريبي ", value=f"ريال {predicted_price:,.2f}")

# Bottom section: Visualization
st.header("📊 رؤى")
images = ["chart1.png", "chart2.png"]
for i, img in enumerate(images, 1):
    image = Image.open(img)
    st.image(image, caption=f"الرسم البياني {i}", use_column_width=True)

# Footer
st.markdown("---")

