
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# إعدادات واجهة المستخدم الاحترافية
st.set_page_config(page_title="Ecotrak Pro AI", layout="wide", page_icon="🤖")

# تصميم الثيم وتنسيق الصفحة
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Ecotrak AI: مستقبل إدارة سلاسل الإمداد")
st.markdown("---")

# دالة ذكية لجلب البيانات وتجهيزها
@st.cache_data
def load_data():
    df = pd.read_csv('energy.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    # إضافة أعمدة مالية افتراضية للعرض الاحترافي
    if 'Price' not in df.columns:
        df['Price'] = 150 # سعر بيع افتراضي
    return df

try:
    df = load_data()
    
    # القائمة الجانبية الذكية
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2649/2649223.png", width=100)
    st.sidebar.header("🕹️ لوحة التحكم")
    product = st.sidebar.selectbox("اختر المنتج لتحليله:", df['Product'].unique())
    
    # فلترة البيانات بناءً على المنتج
    p_data = df[df['Product'] == product].sort_values('Date')
    
    # --- قسم الأرقام الكبرى (Key Metrics) ---
    avg_sales = p_data['Sales'].mean()
    current_stock = p_data['Stock'].iloc[-1]
    S = p_data['Cost_S'].iloc[0]
    H = p_data['Cost_H'].iloc[0]
    
    # معادلة EOQ الهندسية
    eoq = np.sqrt((2 * avg_sales * 365 * S) / H)
    
    # توقع مبيعات غداً (ذكاء اصطناعي بسيط: متوسط متحرك)
    forecast = p_data['Sales'].rolling(window=2).mean().iloc[-1] * 1.1 # زيادة 10% كتوقع
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📦 المخزون الحالي", f"{current_stock} قطعة")
    m2.metric("📈 التوقع لغداً", f"{forecast:.1f} قطعة", delta="10%+")
    m3.metric("💰 الكمية الاقتصادية (EOQ)", f"{int(eoq)} قطعة")
    m4.metric("💵 الدخل المتوقع", f"{int(forecast * p_data['Price'].iloc[0])} ريال")

    # --- قسم الرسوم البيانية التفاعلية ---
    st.markdown("### 📊 التحليل البصري المتقدم")
    c1, c2 = st.columns(2)
    
    with c1:
        # رسم بياني تفاعلي للمبيعات
        fig_sales = px.area(p_data, x='Date', y='Sales', title='حركة السحب اليومية', 
                            line_shape='spline', color_discrete_sequence=['#3498db'])
        st.plotly_chart(fig_sales, use_container_width=True)
        
    with c2:
        # رسم بياني للمخزون
        fig_stock = px.line(p_data, x='Date', y='Stock', title='مستويات المخزون مقابل الوقت',
                           markers=True, color_discrete_sequence=['#e74c3c'])
        st.plotly_chart(fig_stock, use_container_width=True)

    # --- قسم التوصية الذكية (AI Recommendation) ---
    st.markdown("---")
    st.subheader("🤖 توصية المساعد الذكي (Ecotrak AI)")
    
    days_left = current_stock / avg_sales
    
    if days_left < 3:
        st.error(f"🚨 **تحذير حرج:** المخزون سيفنى خلال {days_left:.1f} أيام. يرجى طلب {int(eoq)} وحدة فوراً من المورد لتجنب خسارة {int(forecast * 3 * p_data['Price'].iloc[0])} ريال.")
    elif days_left < 7:
        st.warning(f"⚠️ **تنبيه:** المخزون يكفي لأسبوع فقط. ابدأ بتجهيز أمر الشراء.")
    else:
        st.success(f"✅ **حالة ممتازة:** المخزون مستقر ويكفي لمدة {int(days_left)} يوماً. لا داعي للشراء الآن.")

except Exception as e:
    st.error(f"حدث خطأ تقني: {e}")
