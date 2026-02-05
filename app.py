
import streamlit as st
import pandas as pd
import numpy as np

st.title("SmartFlow AI - نظام إدارة سلاسل الإمداد")

# قراءة البيانات
df = pd.read_csv('energy.csv')

# معادلة EOQ (الهندسة الصناعية)
def calculate_eoq(D, S, H):
    return np.sqrt((2 * D * S) / H)

st.subheader("تحليل المخزون الحالي")
st.write(df)

# حساب التنبؤ (بسيط للعرض)
avg_demand = df['Sales'].mean()
S = df['Ordering_Cost'].iloc[0]
H = df['Holding_Cost'].iloc[0]

eoq = calculate_eoq(avg_demand * 30, S, H) # لـ 30 يوم

st.divider()
st.metric(label="الطلب المتوقع (شهرياً)", value=f"{avg_demand * 30:.0f} قطعة")
st.metric(label="الكمية الاقتصادية المثالية (EOQ)", value=f"{eoq:.0f} قطعة")

if df['Stock_Level'].iloc[-1] < 50:
    st.error("⚠️ تنبيه: المخزون منخفض جداً! يرجى إعادة الطلب فوراً.")
else:
    st.success("✅ حالة المخزون: آمنة")
