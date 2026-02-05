
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Ecotrak Pro", layout="wide")
st.title("📦 Ecotrak: نظام إدارة المخزون الذكي")

# قراءة البيانات
try:
    df = pd.read_csv('energy.csv')
    df['Date'] = pd.to_datetime(df['Date']) # تحويل التاريخ لصيغة صحيحة
    
    # قائمة اختيار المنتج في الجانب
    st.sidebar.header("لوحة التحكم")
    all_products = df['Product'].unique()
    selected_product = st.sidebar.selectbox("اختر المنتج للمعالجة:", all_products)

    # تصفية البيانات حسب المنتج المختار
    filtered_df = df[df['Product'] == selected_product].sort_values('Date')

    # الحسابات الهندسية (EOQ)
    avg_sales = filtered_df['Sales'].mean()
    S = filtered_df['Cost_S'].iloc[0]
    H = filtered_df['Cost_H'].iloc[0]
    eoq = np.sqrt((2 * avg_sales * 365 * S) / H)

    # عرض الأرقام الرئيسية
    col1, col2, col3 = st.columns(3)
    col1.metric("متوسط المبيعات اليومية", f"{avg_sales:.1f}")
    col2.metric("الكمية المثالية للطلب (EOQ)", f"{int(eoq)} وحدة")
    col3.metric("المخزون الحالي", f"{filtered_df['Stock'].iloc[-1]}")

    st.divider()

    # الرسوم البيانية
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📈 اتجاه المبيعات")
        st.line_chart(filtered_df.set_index('Date')['Sales'])
        
    with col_b:
        st.subheader("📉 مستويات المخزون")
        st.area_chart(filtered_df.set_index('Date')['Stock'])

    # تنبيه ذكي
    if filtered_df['Stock'].iloc[-1] < 50:
        st.error(f"⚠️ تنبيه: مخزون {selected_product} منخفض جداً! يرجى طلب {int(eoq)} وحدة.")
    else:
        st.success(f"✅ وضع المخزون لـ {selected_product} مستقر.")

except Exception as e:
    st.error(f"حدث خطأ في قراءة البيانات: {e}")
    st.info("تأكد من رفع ملف energy.csv بشكل صحيح")
