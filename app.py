
import streamlit as st
import pandas as pd
import numpy as np
import os

# إعدادات الصفحة
st.set_page_config(page_title="Ecotrak AI", page_icon="📦", layout="wide")

st.title("📦 Ecotrak: Smart Supply Chain Optimizer")
st.markdown("---")

# وظيفة لتحميل البيانات أو إنشاء بيانات افتراضية
def load_data():
    if os.path.exists('energy.csv'):
        try:
            return pd.read_csv('energy.csv')
        except:
            pass
    
    # بيانات افتراضية في حال عدم وجود ملف
    data = {
        'Date': pd.date_range(start='2026-01-01', periods=10).astype(str),
        'Product': ['Product_A']*10,
        'Sales': [20, 25, 30, 22, 28, 35, 18, 24, 29, 31],
        'Stock_Level': [200, 175, 145, 123, 95, 60, 42, 118, 89, 58],
        'Ordering_Cost': [100]*10,
        'Holding_Cost': [5]*10
    }
    return pd.DataFrame(data)

df = load_data()

# --- الحسابات الهندسية (EOQ) ---
avg_sales = df['Sales'].mean()
S = df['Ordering_Cost'].iloc[0]
H = df['Holding_Cost'].iloc[0]
# EOQ = sqrt(2 * الطلب السنوي * تكلفة الطلب / تكلفة التخزين)
annual_demand = avg_sales * 365
eoq = np.sqrt((2 * annual_demand * S) / H)

# --- عرض لوحة التحكم ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("متوسط السحب اليومي", f"{avg_sales:.1f} قطعة")
with col2:
    st.metric("الكمية الاقتصادية (EOQ)", f"{eoq:.0f} قطعة")
with col3:
    st.metric("المخزون الحالي", f"{df['Stock_Level'].iloc[-1]} قطعة")

st.markdown("### 📊 تحليل اتجاهات المبيعات")
st.line_chart(df.set_index('Date')['Sales'])

# نظام التنبيه
st.markdown("### 🔔 حالة الطلب")
current_stock = df['Stock_Level'].iloc[-1]
if current_stock < 50:
    st.error(f"⚠️ المخزون منخفض ({current_stock} قطعة). يرجى طلب شحنة جديدة فوراً!")
else:
    st.success(f"✅ المخزون كافٍ ({current_stock} قطعة). لا حاجة للطلب الآن.")
