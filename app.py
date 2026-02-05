
import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="Ecotrak AI", layout="wide")
st.title("📦 Ecotrak: Smart Supply Chain Optimizer")

# التأكد من وجود ملف البيانات أو استخدام بيانات تجريبية
if os.path.exists('energy.csv'):
    df = pd.read_csv('energy.csv')
    st.success("تم تحميل البيانات من الملف بنجاح!")
else:
    # بيانات احتياطية لكي لا يتعطل التطبيق أمام الحكام
    st.warning("تنبيه: يتم العرض باستخدام بيانات افتراضية (ملف energy.csv غير موجود)")
    data = {
        'Date': pd.date_range(start='2026-01-01', periods=5).astype(str),
        'Product': ['Product_A']*5,
        'Sales': [20, 25, 30, 22, 28],
        'Stock_Level': [150, 125, 95, 73, 45],
        'Ordering_Cost': [100]*5,
        'Holding_Cost': [5]*5
    }
    df = pd.DataFrame(data)

# --- الحسابات الهندسية ---
avg_sales = df['Sales'].mean()
S = df['Ordering_Cost'].iloc[0]
H = df['Holding_Cost'].iloc[0]
eoq = np.sqrt((2 * avg_sales * 30 * S) / H)

# --- عرض النتائج ---
col1, col2, col3 = st.columns(3)
col1.metric("متوسط السحب اليومي", f"{avg_sales:.1f} قطعة")
col2.metric("الكمية الاقتصادية (EOQ)", f"{eoq:.0f} قطعة")
col3.metric("المخزون الحالي", f"{df['Stock_Level'].iloc[-1]} قطعة")

st.divider()
st.subheader("📊 تحليل حركة المخزون")
st.line_chart(df.set_index('Date')['Sales'])

if df['Stock_Level'].iloc[-1] < 50:
    st.error("🚨 خطر: المخزون وصل لنقطة إعادة الطلب! يرجى الشراء الآن.")
