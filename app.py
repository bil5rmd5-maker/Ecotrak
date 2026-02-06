import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. إعدادات المنصة
st.set_page_config(page_title="Ecotrak Ultimate", layout="wide", page_icon="💎")

# 2. تهيئة البيانات في ذاكرة الجلسة (Session State)
if 'products_df' not in st.session_state:
    st.session_state.products_df = pd.DataFrame([
        {'product_name': 'توربينات كهربائية', 'daily_sales': 12, 'stock': 45, 'price': 8000, 'order_cost': 1200, 'holding_cost': 200, 'lead_time': 10},
        {'product_name': 'لوحات تحكم', 'daily_sales': 35, 'stock': 120, 'price': 1500, 'order_cost': 300, 'holding_cost': 45, 'lead_time': 5}
    ])

# --- القائمة الجانبية للتعديل السريع (الميزة الجديدة) ---
st.sidebar.title("💎 Ecotrak Control")

st.sidebar.subheader("🔄 تعديل سريع للمخزون")
p_to_edit = st.sidebar.selectbox("اختر المنتج لتعديله:", st.session_state.products_df['product_name'].unique())
new_stock_val = st.sidebar.number_input("الكمية الجديدة في المستودع:", min_value=0, value=int(st.session_state.products_df.loc[st.session_state.products_df['product_name'] == p_to_edit, 'stock'].values[0]))

if st.sidebar.button("تحديث الكمية الآن"):
    st.session_state.products_df.loc[st.session_state.products_df['product_name'] == p_to_edit, 'stock'] = new_stock_val
    st.sidebar.success(f"تم تحديث مخزون {p_to_edit}!")

st.sidebar.markdown("---")
menu = st.sidebar.radio("انتقل إلى:", ["📊 لوحة القراءات الذكية", "➕ إضافة أصناف جديدة", "🚚 رادر الموردين", "🌱 الاستدامة"])

# --- القائمة 1: لوحة القراءات الذكية ---
if menu == "📊 لوحة القراءات الذكية":
    st.header("📊 تحليل حالة المنتج والدعم اللحظي")
    
    selected_p = st.selectbox("اختر المنتج لتحليله العادي:", st.session_state.products_df['product_name'].unique(), key="main_select")
    p_data = st.session_state.products_df[st.session_state.products_df['product_name'] == selected_p].iloc[0]
    
    # الحسابات الهندسية
    days_left = p_data['stock'] / p_data['daily_sales']
    eoq = np.sqrt((2 * p_data['daily_sales'] * 365 * p_data['order_cost']) / p_data['holding_cost'])
    needed_to_order = int(eoq) if days_left <= p_data['lead_time'] else 0
    
    # عرض النتائج
    m1, m2, m3 = st.columns(3)
    if days_left <= p_data['lead_time']:
        m1.error("الحالة: حرجة 🚨 (تحتاج توريد)")
    else:
        m1.success("الحالة: آمنة ✅ (مخزون كافٍ)")
        
    m2.metric("المخزون الحالي", f"{int(p_data['stock'])} قطعة")
    m3.metric("الكمية المطلوبة (EOQ)", f"{needed_to_order} قطعة")

    st.markdown("---")
    st.subheader(f"📈 تحليل التوازن لـ {selected_p}")
    fig = px.bar(x=['المخزون الحالي', 'الكمية الاقتصادية المثالية'], y=[p_data['stock'], eoq], 
                 color=['الحالي', 'المثالي'], color_discrete_sequence=['#FF4B4B', '#00CC96'])
    st.plotly_chart(fig, use_container_width=True)

# --- القائمة 2: إضافة المنتجات الجديدة ---
elif menu == "➕ إضافة أصناف جديدة":
    st.header("➕ تسجيل صنف جديد في النظام")
    with st.form("new_p"):
        name = st.text_input("اسم المنتج")
        c1, c2 = st.columns(2)
        sales = c1.number_input("متوسط السحب اليومي", min_value=1, value=10)
        price = c2.number_input("سعر الوحدة", min_value=1, value=500)
        if st.form_submit_button("حفظ المنتج الجديد"):
            new_row = {'product_name': name, 'daily_sales': sales, 'stock': 0, 'price': price, 'order_cost': 200, 'holding_cost': 10, 'lead_time': 7}
            st.session_state.products_df = pd.concat([st.session_state.products_df, pd.DataFrame([new_row])], ignore_index=True)
            st.success("تمت الإضافة!")

# بقية القوائم تعمل بنفس المنطق السابق...
