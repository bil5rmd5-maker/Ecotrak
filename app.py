
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. إعدادات الصفحة الاحترافية
st.set_page_config(page_title="Ecotrak AI v2.0", layout="wide", page_icon="🛡️")

# تنسيق مخصص لجعل الواجهة تبدو كأنها نظام مؤسسي
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #e1e4e8; }
    .stAlert { border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Ecotrak AI: منصة هندسة سلاسل الإمداد المتكاملة")
st.markdown("---")

# 2. قاعدة بيانات افتراضية للمنتجات
def get_advanced_data():
    return pd.DataFrame({
        'Product': ['قطع غيار محركات', 'زيوت صناعية', 'فلاتر هيدروليك'],
        'Sales': [15, 45, 10],
        'Stock': [80, 200, 35],
        'Cost_S': [250, 100, 50],
        'Cost_H': [15, 5, 2],
        'Price': [1200, 350, 85],
        'Lead_Time': [5, 3, 7] # وقت وصول الشحنة بالأيام
    })

df = get_advanced_data()

# 3. القائمة الجانبية: لوحة التحكم المتقدمة
st.sidebar.header("🕹️ التحكم بالسيناريوهات")
selected_p = st.sidebar.selectbox("اختر الصنف:", df['Product'])
row = df[df['Product'] == selected_p].iloc[0]

st.sidebar.markdown("---")
with st.sidebar.expander("📝 المعطيات التشغيلية", expanded=True):
    daily_sales = st.slider("السحب اليومي المتوقع", 1, 200, int(row['Sales']))
    price = st.number_input("سعر بيع الوحدة (ريال)", value=int(row['Price']))
    current_stock = st.number_input("المخزون الفعلي الحالي", value=int(row['Stock']))

with st.sidebar.expander("⚙️ معايير الهندسة الصناعية", expanded=False):
    order_cost = st.number_input("تكلفة الطلب والشحن (S)", value=int(row['Cost_S']))
    holding_cost = st.number_input("تكلفة التخزين للوحدة (H)", value=float(row['Cost_H']))
    safety_days = st.slider("مخزون الأمان (تغطية بالأيام)", 0, 15, 3)

# 4. الحسابات الهندسية والمالية المتقدمة
# معادلة EOQ
eoq = np.sqrt((2 * daily_sales * 365 * order_cost) / holding_cost)

# حساب مخزون الأمان (Safety Stock)
safety_stock = daily_sales * safety_days

# حساب نقطة إعادة الطلب (Reorder Point)
reorder_point = safety_stock + (daily_sales * row['Lead_Time'])

# حساب الأرباح الضائعة المتوقعة (Lost Profit Potential)
days_to_zero = current_stock / daily_sales
potential_loss = 0
if days_to_zero < 5:
    potential_loss = (5 - days_to_zero) * daily_sales * price * 0.3 # بافتراض هامش ربح 30%

# 5. عرض النتائج (Dashboard)
col1, col2, col3, col4 = st.columns(4)
col1.metric("المخزون الحالي", f"{current_stock} وحدة")
col2.metric("مخزون الأمان المطلوب", f"{safety_stock} وحدة")
col3.metric("الكمية الاقتصادية (EOQ)", f"{int(eoq)} وحدة")
col4.metric("نقطة إعادة الطلب", f"{int(reorder_point)} وحدة")

st.markdown("---")

# 6. قسم الرسوم البيانية والتحليل المالي
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📊 تحليل تدفق المخزون")
    # محاكاة لهبوط المخزون
    time_range = range(0, 15)
    stock_levels = [max(0, current_stock - (daily_sales * t)) for t in time_range]
    fig = px.line(x=time_range, y=stock_levels, labels={'x':'الأيام القادمة', 'y':'مستوى المخزون'},
                 title="توقع نفاد المخزون الزمني")
    fig.add_hline(y=safety_stock, line_dash="dash", line_color="orange", annotation_text="مخزون الأمان")
    fig.add_hline(y=reorder_point, line_dash="dot", line_color="red", annotation_text="نقطة الطلب")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("💰 التقرير المالي")
    st.write(f"**إجمالي قيمة المخزون:** {current_stock * price:,.0f} ريال")
    st.write(f"**تكلفة التخزين السنوية:** {current_stock * holding_cost * 12:,.0f} ريال")
    if potential_loss > 0:
        st.error(f"**مخاطر خسارة أرباح:** {potential_loss:,.0f} ريال")
    else:
        st.success("**لا يوجد مخاطر خسارة أرباح حالياً**")

# 7. التوصية الذكية النهائية
st.markdown("---")
st.subheader("🤖 توصية المساعد المهني")
if current_stock <= reorder_point:
    st.critical(f"⚠️ **إجراء عاجل مطلوب:** المخزون تحت 'نقطة إعادة الطلب'. يجب طلب {int(eoq)} وحدة فوراً لتجنب توقف العمليات.")
else:
    st.info(f"✅ **الوضع مستقر:** المخزون يغطي احتياجات العمل. موعد الطلب القادم المتوقع بعد {int((current_stock - reorder_point)/daily_sales)} أيام.")
