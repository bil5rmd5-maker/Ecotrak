import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. إعدادات المنصة الاحترافية
st.set_page_config(page_title="Ecotrak Ultimate", layout="wide", page_icon="💎")

# تنسيق CSS مخصص للواجهة
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #ffffff; border-radius: 10px 10px 0 0; gap: 1px; padding: 10px; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# 2. إدارة البيانات (إضافة خاصية التعديل اللحظي)
if 'products_df' not in st.session_state:
    st.session_state.products_df = pd.DataFrame([
        {'Product': 'توربينات كهربائية', 'Sales': 12, 'Stock': 45, 'Price': 8000, 'Cost_S': 1200, 'Cost_H': 200, 'Lead_Time': 10},
        {'Product': 'لوحات تحكم', 'Sales': 35, 'Stock': 120, 'Price': 1500, 'Cost_S': 300, 'Cost_H': 45, 'Lead_Time': 5}
    ])

# --- العنوان الجانبي ---
st.sidebar.title("💎 Ecotrak Control Center")
menu = st.sidebar.radio("القائمة الرئيسية", ["📊 لوحة القراءات العامة", "➕ إدارة المنتجات", "📉 تحليل ABC المتقدم", "🚚 رادار الموردين", "🌱 تقرير الاستدامة", "🧠 مركز دعم القرار"])

# --- القائمة 1: لوحة القراءات العامة ---
if menu == "📊 لوحة القراءات العامة":
    st.header("📊 المؤشرات الاستراتيجية للمنشأة")
    
    # حسابات سريعة
    total_val = (st.session_state.products_df['Stock'] * st.session_state.products_df['Price']).sum()
    avg_stock_cover = (st.session_state.products_df['Stock'] / st.session_state.products_df['Sales']).mean()
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("إجمالي قيمة المخزون", f"{total_val:,.0f} ريال")
    m2.metric("متوسط التغطية (أيام)", f"{int(avg_stock_cover)} يوم")
    m3.metric("عدد الأصناف", len(st.session_state.products_df))
    m4.metric("مؤشر الكفاءة (OEE)", "92%")

    st.markdown("---")
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        fig_stock = px.pie(st.session_state.products_df, names='Product', values='Stock', hole=0.4, title="توزيع كميات المخزون")
        st.plotly_chart(fig_stock, use_container_width=True)
    
    with col_chart2:
        fig_value = px.bar(st.session_state.products_df, x='Product', y='Price', title="مقارنة أسعار الوحدات")
        st.plotly_chart(fig_value, use_container_width=True)

# --- القائمة 2: إضافة وتعديل المنتجات (السلاسة المطلقة) ---
elif menu == "➕ إدارة المنتجات":
    st.header("➕ إضافة وتعديل المنتجات لحظياً")
    with st.form("add_product"):
        name = st.text_input("اسم المنتج الجديد")
        c1, c2, c3 = st.columns(3)
        s_val = c1.number_input("المبيعات اليومية", value=10)
        stk_val = c2.number_input("المخزون الحالي", value=100)
        prc_val = c3.number_input("السعر", value=500)
        
        if st.form_submit_button("إضافة للمنظومة"):
            new_row = {'Product': name, 'Sales': s_val, 'Stock': stk_val, 'Price': prc_val, 'Cost_S': 200, 'Cost_H': 10, 'Lead_Time': 7}
            st.session_state.products_df = pd.concat([st.session_state.products_df, pd.DataFrame([new_row])], ignore_index=True)
            st.success("تمت إضافة المنتج بنجاح!")
    
    st.dataframe(st.session_state.products_df, use_container_width=True)

# --- القائمة 3: تحليل ABC المتقدم ---
elif menu == "📉 تحليل ABC المتقدم":
    st.header("📉 تصنيف المخزون حسب القيمة المضافة")
    df = st.session_state.products_df.copy()
    df['Annual_Value'] = df['Sales'] * 365 * df['Price']
    df = df.sort_values('Annual_Value', ascending=False)
    df['Cumulative_Value'] = df['Annual_Value'].cumsum()
    total = df['Annual_Value'].sum()
    df['Percentage'] = (df['Cumulative_Value'] / total) * 100
    
    def classify(p):
        if p <= 70: return 'A (حرج - قيمة عالية)'
        elif p <= 90: return 'B (متوسط الأهمية)'
        else: return 'C (قيمة منخفضة)'
    
    df['Category'] = df['Percentage'].apply(classify)
    
    st.plotly_chart(px.scatter(df, x='Product', y='Annual_Value', color='Category', size='Annual_Value', title="توزيع ABC لموارد الشركة"), use_container_width=True)
    st.table(df[['Product', 'Annual_Value', 'Category']])

# --- القائمة 6: مركز دعم القرار (الذكاء الاصطناعي) ---
elif menu == "🧠 مركز دعم القرار":
    st.header("🧠 مستشار دعم القرار الآلي")
    selected = st.selectbox("اختر المنتج للتحليل العميق:", st.session_state.products_df['Product'])
    p_data = st.session_state.products_df[st.session_state.products_df['Product'] == selected].iloc[0]
    
    st.info(f"تحليل المنتج: **{selected}**")
    
    # حسابات EOQ
    eoq = np.sqrt((2 * p_data['Sales'] * 365 * p_data['Cost_S']) / p_data['Cost_H'])
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🔍 تحليل الأسباب")
        if p_data['Stock'] < (p_data['Sales'] * 3):
            st.error(f"**سبب الخطر:** استنزاف سريع للمخزون. السحب اليومي يمثل {(p_data['Sales']/p_data['Stock']*100):.1f}% من إجمالي المتوفر.")
        else:
            st.success("المخزون الحالي مستقر وضمن الحدود الآمنة.")
            
    with c2:
        st.markdown("### 🛠️ الحلول المقترحة")
        st.write(f"1. **الشراء الأمثل:** اطلب كمية {int(eoq)} قطعة لتقليل تكلفة التخزين.")
        st.write(f"2. **الاستراتيجية:** بما أن المنتج فئة A، يُنصح بتطبيق نظام الشراء JIT (في الوقت المحدد).")

# بقية القوائم (الموردين والاستدامة) تتبع نفس النمط...
