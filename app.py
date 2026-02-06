import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. إعدادات المنصة
st.set_page_config(page_title="Ecotrak Ultimate AI", layout="wide", page_icon="💎")

# 2. تهيئة البيانات
if 'products_df' not in st.session_state:
    st.session_state.products_df = pd.DataFrame([
        {'product_name': 'توربينات كهربائية', 'daily_sales': 12, 'stock': 45, 'price': 8000, 'order_cost': 1200, 'holding_cost': 200, 'lead_time': 10},
        {'product_name': 'لوحات تحكم', 'daily_sales': 35, 'stock': 120, 'price': 1500, 'order_cost': 300, 'holding_cost': 45, 'lead_time': 5}
    ])

# --- القائمة الجانبية ---
st.sidebar.title("💎 Ecotrak Control")
menu = st.sidebar.radio("انتقل إلى:", ["📊 لوحة القراءات", "🎛️ محاكي التأثير الاقتصادي", "➕ إضافة/تعديل أصناف", "🚚 رادار الموردين"])

# --- القائمة 1: لوحة القراءات (تم إبقاؤها بسيطة للعرض) ---
if menu == "📊 لوحة القراءات":
    st.header("📊 حالة المخزون اللحظية")
    selected_p = st.selectbox("اختر المنتج:", st.session_state.products_df['product_name'].unique())
    p_data = st.session_state.products_df[st.session_state.products_df['product_name'] == selected_p].iloc[0]
    
    col1, col2, col3 = st.columns(3)
    days_left = p_data['stock'] / p_data['daily_sales']
    col1.metric("المخزون الحالي", f"{int(p_data['stock'])} قطعة")
    col2.metric("أيام التغطية", f"{int(days_left)} يوم")
    col3.metric("الدخل اليومي", f"{int(p_data['daily_sales'] * p_data['price'])} ريال")
    
    st.progress(min(days_left/30, 1.0), text="مؤشر استدامة المخزون (30 يوم)")

# --- القائمة 2: محاكي التأثير الاقتصادي (الميزة المطلوبة) ---
elif menu == "🎛️ محاكي التأثير الاقتصادي":
    st.header("🎛️ محاكي الحساسية ودراسة الأثر")
    st.write("هنا يمكنك تجربة كيف تؤثر قراراتك في السعر والتكاليف على أداء المنتج")
    
    selected_p = st.selectbox("اختر المنتج للتجربة:", st.session_state.products_df['product_name'].unique())
    p_data = st.session_state.products_df[st.session_state.products_df['product_name'] == selected_p].iloc[0]
    
    col_ctrl, col_res = st.columns([1, 2])
    
    with col_ctrl:
        st.subheader("🛠️ معايير التحكم")
        # محاكاة تغيير السعر وتأثيره على الطلب (قانون العرض والطلب)
        sim_price = st.slider("تعديل سعر الوحدة (ريال)", int(p_data['price']*0.5), int(p_data['price']*1.5), int(p_data['price']))
        sim_order_cost = st.slider("تعديل تكاليف الشحن (S)", 50, 2000, int(p_data['order_cost']))
        
        # معادلة تخيلية: إذا قل السعر زاد السحب (بنسبة مرونة 1.5)
        price_change_ratio = sim_price / p_data['price']
        sim_sales = p_data['daily_sales'] / (price_change_ratio ** 1.5)
        
        # إعادة حساب EOQ بناءً على المعايير الجديدة
        sim_eoq = np.sqrt((2 * sim_sales * 365 * sim_order_cost) / p_data['holding_cost'])

    with col_res:
        st.subheader("📈 النتائج المتوقعة")
        r1, r2 = st.columns(2)
        r1.metric("السحب اليومي الجديد", f"{sim_sales:.1f} قطعة", delta=f"{sim_sales - p_data['daily_sales']:.1f}")
        r2.metric("الكمية الاقتصادية الجديدة", f"{int(sim_eoq)} قطعة")
        
        # رسم بياني للعلاقة بين السعر والطلب
        prices = np.linspace(p_data['price']*0.5, p_data['price']*1.5, 20)
        sales_curve = p_data['daily_sales'] / ((prices / p_data['price']) ** 1.5)
        
        fig = px.line(x=prices, y=sales_curve, labels={'x':'السعر (ريال)', 'y':'السحب المتوقع'}, title="منحنى مرونة الطلب (السعر مقابل السحب)")
        fig.add_vline(x=sim_price, line_dash="dash", line_color="red", annotation_text="السعر المختار")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.info(f"💡 **تحليل المستشار:** إذا قمت بخفض السعر إلى **{sim_price} ريال**، سيزيد السحب اليومي بنسبة **{((sim_sales/p_data['daily_sales'])-1)*100:.1f}%**. هذا سيتطلب منك زيادة الكمية المطلوبة في كل شحنة إلى **{int(sim_eoq)} قطعة** لضمان أقل تكلفة تشغيلية.")

# بقية القوائم...
