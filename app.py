import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. إعدادات المنصة الاحترافية
st.set_page_config(page_title="Ecotrak Master AI", layout="wide", page_icon="💎")

# 2. تهيئة البيانات في ذاكرة الجلسة
if 'products_df' not in st.session_state:
    st.session_state.products_df = pd.DataFrame([
        {'product_name': 'توربينات كهربائية', 'daily_sales': 12, 'stock': 45, 'price': 8000, 'order_cost': 1200, 'holding_cost': 200, 'lead_time': 10},
        {'product_name': 'لوحات تحكم', 'daily_sales': 35, 'stock': 120, 'price': 1500, 'order_cost': 300, 'holding_cost': 45, 'lead_time': 5}
    ])

# --- القائمة الجانبية الموحدة ---
st.sidebar.title("💎 Ecotrak Control Center")

# ميزة التعديل السريع للمخزون (موجودة دائماً في الجنب لسهولة العرض)
st.sidebar.subheader("🔄 تحديث سريع للمخزون")
p_to_edit = st.sidebar.selectbox("اختر المنتج لتعديله:", st.session_state.products_df['product_name'].unique())
current_val = int(st.session_state.products_df.loc[st.session_state.products_df['product_name'] == p_to_edit, 'stock'].values[0])
new_stock_val = st.sidebar.number_input("الكمية الفعلية حالياً:", min_value=0, value=current_val)

if st.sidebar.button("تحديث الكمية"):
    st.session_state.products_df.loc[st.session_state.products_df['product_name'] == p_to_edit, 'stock'] = new_stock_val
    st.sidebar.success("تم التحديث!")

st.sidebar.markdown("---")
# التنقل بين القوائم
menu = st.sidebar.radio("القوائم الرئيسية:", 
    ["📊 لوحة القراءات الذكية", "🎛️ محاكي التأثير الاقتصادي", "➕ إدارة المنتجات", "🚚 رادار الموردين", "🌱 تقرير الاستدامة"])

# --- القائمة 1: لوحة القراءات الذكية ---
if menu == "📊 لوحة القراءات الذكية":
    st.header("📊 حالة المخزون ودعم القرار")
    selected_p = st.selectbox("اختر المنتج للتحليل:", st.session_state.products_df['product_name'].unique())
    p_data = st.session_state.products_df[st.session_state.products_df['product_name'] == selected_p].iloc[0]
    
    days_left = p_data['stock'] / p_data['daily_sales']
    eoq = np.sqrt((2 * p_data['daily_sales'] * 365 * p_data['order_cost']) / p_data['holding_cost'])
    needed = int(eoq) if days_left <= p_data['lead_time'] else 0
    
    c1, c2, c3 = st.columns(3)
    if days_left <= p_data['lead_time']:
        c1.error("الحالة: حرجة 🚨")
    else:
        c1.success("الحالة: آمنة ✅")
    c2.metric("أيام التغطية المتبقية", f"{int(days_left)} يوم")
    c3.metric("الكمية المطلوب طلبها", f"{needed} قطعة")
    
    st.plotly_chart(px.bar(x=['المخزون الحالي', 'الكمية الاقتصادية (EOQ)'], y=[p_data['stock'], eoq], 
                           color=['الحالي', 'المثالي'], title=f"تحليل التوازن لـ {selected_p}"), use_container_width=True)

# --- القائمة 2: محاكي التأثير الاقتصادي (الميزة الجديدة المدمجة) ---
elif menu == "🎛️ محاكي التأثير الاقتصادي":
    st.header("🎛️ محاكي الحساسية (تحليل What-If)")
    selected_p = st.selectbox("اختر المنتج للمحاكاة:", st.session_state.products_df['product_name'].unique())
    p_data = st.session_state.products_df[st.session_state.products_df['product_name'] == selected_p].iloc[0]
    
    col_ctrl, col_res = st.columns([1, 2])
    with col_ctrl:
        st.subheader("🛠️ معايير التحكم")
        sim_price = st.slider("تعديل السعر (ريال)", int(p_data['price']*0.5), int(p_data['price']*1.5), int(p_data['price']))
        sim_order_cost = st.slider("تكلفة الشحن (S)", 50, 2000, int(p_data['order_cost']))
        
        # خوارزمية مرونة الطلب: خفض السعر يزيد السحب
        price_ratio = sim_price / p_data['price']
        sim_sales = p_data['daily_sales'] / (price_ratio ** 1.2)
        sim_eoq = np.sqrt((2 * sim_sales * 365 * sim_order_cost) / p_data['holding_cost'])

    with col_res:
        st.subheader("📈 النتائج المتوقعة")
        r1, r2 = st.columns(2)
        r1.metric("السحب اليومي المتوقع", f"{sim_sales:.1f}", delta=f"{sim_sales - p_data['daily_sales']:.1f}")
        r2.metric("EOQ الجديد", f"{int(sim_eoq)}")
        
        # رسم بياني لمنحنى السعر مقابل الطلب
        price_range = np.linspace(p_data['price']*0.5, p_data['price']*1.5, 30)
        sales_range = p_data['daily_sales'] / ((price_range / p_data['price']) ** 1.2)
        fig = px.line(x=price_range, y=sales_range, labels={'x':'السعر', 'y':'السحب'}, title="منحنى مرونة الطلب")
        fig.add_vline(x=sim_price, line_dash="dash", line_color="red")
        st.plotly_chart(fig, use_container_width=True)

# --- القائمة 3: إدارة المنتجات ---
elif menu == "➕ إدارة المنتجات":
    st.header("➕ إضافة صنف جديد")
    with st.form("add_form"):
        name = st.text_input("اسم المنتج")
        c1, c2, c3 = st.columns(3)
        s_daily = c1.number_input("السحب اليومي", value=10)
        s_stock = c2.number_input("المخزون البدائي", value=0)
        p_price = c3.number_input("السعر", value=500)
        if st.form_submit_button("إضافة للمنظومة"):
            new_row = {'product_name': name, 'daily_sales': s_daily, 'stock': s_stock, 'price': p_price, 'order_cost': 200, 'holding_cost': 10, 'lead_time': 7}
            st.session_state.products_df = pd.concat([st.session_state.products_df, pd.DataFrame([new_row])], ignore_index=True)
            st.success("تم الحفظ!")
    st.dataframe(st.session_state.products_df)

# --- القائمة 4: رادار الموردين ---
elif menu == "🚚 رادار الموردين":
    st.header("🚚 مقارنة الموردين")
    vendors = pd.DataFrame({
        'المورد': ['محلي', 'إقليمي', 'دولي'],
        'أيام_التوصيل': [3, 8, 20],
        'تكلفة_الشحن': [1000, 500, 150],
        'الجودة': [80, 90, 98]
    })
    st.plotly_chart(px.scatter(vendors, x='أيام_التوصيل', y='تكلفة_الشحن', size='الجودة', text='المورد', title="رادار اختيار المورد الأنسب"), use_container_width=True)

# --- القائمة 5: تقرير الاستدامة ---
elif menu == "🌱 تقرير الاستدامة":
    st.header("🌱 تقرير الأثر البيئي")
    co2 = len(st.session_state.products_df) * 12.5
    st.metric("CO2 الموفر (كجم)", f"{co2:.1f}")
    st.success("نظام Ecotrak يساهم في تقليل الهدر اللوجستي بما يتوافق مع رؤية المملكة 2030.")
