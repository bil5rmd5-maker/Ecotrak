
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Ecotrak Pro", layout="wide", page_icon="📈")

# واجهة المستخدم الاحترافية
st.sidebar.title("🎮 لوحة التحكم")
st.sidebar.info("مشروع Ecotrak لتحسين سلاسل الإمداد باستخدام الهندسة الصناعية")

# تحميل البيانات
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('energy.csv')
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except:
        st.error("يرجى التأكد من رفع ملف energy.csv بشكل صحيح")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # فلترة المنتجات
    product = st.sidebar.selectbox("اختر المنتج", df['Product'].unique())
    p_data = df[df['Product'] == product].sort_values('Date')

    st.title(f"📊 تحليل منتج: {product}")
    
    # الحسابات الهندسية
    avg_demand = p_data['Sales'].mean()
    S = p_data['Ordering_Cost'].iloc[-1]
    H = p_data['Holding_Cost'].iloc[-1]
    eoq = np.sqrt((2 * avg_demand * 365 * S) / H)
    
    # عرض المؤشرات (KPIs)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("المخزون الحالي", f"{p_data['Stock_Level'].iloc[-1]} وحدة")
    c2.metric("متوسط المبيعات", f"{avg_demand:.1f}")
    c3.metric("كمية الطلب المثالية (EOQ)", f"{int(eoq)}")
    
    status = "آمن ✅" if p_data['Stock_Level'].iloc[-1] > 50 else "خطر 🚨"
    c4.metric("حالة المخزون", status)

    # الرسوم البيانية
    st.markdown("---")
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 حركة المبيعات اليومية")
        fig_sales = px.line(p_data, x='Date', y='Sales', markers=True)
        st.plotly_chart(fig_sales, use_container_width=True)
        
    with col_right:
        st.subheader("📦 مستويات المخزون")
        fig_stock = px.area(p_data, x='Date', y='Stock_Level', color_discrete_sequence=['#ff4b4b'])
        st.plotly_chart(fig_stock, use_container_width=True)

    # جدول التوصية الهندسية
    st.info(f"💡 نصيحة مهندس: بناءً على تكلفة التخزين ({H} ريال)، يُنصح بطلب {int(eoq)} وحدة في كل شحنة لتقليل التكاليف الإجمالية.")
