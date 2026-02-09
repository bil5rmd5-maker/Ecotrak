import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. إعدادات المنصة (يجب أن يكون أول سطر دائماً)
st.set_page_config(page_title="Ecotrak Final ERP", layout="wide", page_icon="🧬")

# 2. تهيئة البيانات بأسماء ثابتة (Standard Schema) لتجنب الـ KeyError
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame([
        {
            'id': 1, 
            'p_name': 'صابون لافندر عضوي', 
            'daily_demand': 50, 
            'current_stock': 400, 
            'sale_price': 25.0, 
            'base_cost': 12.0, 
            'shipping_s': 150.0, 
            'storage_h': 2.0, 
            'waste_rate': 3.0, 
            'lead_time': 3,
            'comp_price': 27.0
        },
        {
            'id': 2, 
            'p_name': 'منظف أواني ليمون', 
            'daily_demand': 120, 
            'current_stock': 150, 
            'sale_price': 15.0, 
            'base_cost': 7.0, 
            'shipping_s': 80.0, 
            'storage_h': 1.0, 
            'waste_rate': 1.5, 
            'lead_time': 2,
            'comp_price': 14.5
        }
    ])

# دالة حساب EOQ
def calc_eoq(d, s, h):
    return np.sqrt((2 * d * 365 * s) / h) if h > 0 else 0

# --- القائمة الجانبية للتنقل ---
st.sidebar.title("🧬 Ecotrak Intelligence")
menu = st.sidebar.radio("المنظومات المدمجة:", 
    ["📋 إدارة الأصول والتكاليف", "📊 التوأم الرقمي (المحاكاة)", "📑 الفواتير والربحية اللحظية", "💡 رادار السوق و AI"],
    key="nav_final")

# --- 1. إدارة الأصول والتكاليف (المصدر الرئيسي للبيانات) ---
if menu == "📋 إدارة الأصول والتكاليف":
    st.header("📋 هندسة التكاليف والبيانات الأساسية")
    st.info("💡 تعديل 'تكلفة الشحن' أو 'التلف' هنا سيغير فوراً من نتائج التوأم الرقمي والأرباح.")
    
    # قاموس لترجمة الأسماء البرمجية للعربية في الجدول لراحة المستخدم
    col_translation = {
        'p_name': 'المنتج', 'daily_demand': 'السحب اليومي', 'current_stock': 'المخزون',
        'sale_price': 'سعر البيع', 'base_cost': 'التكلفة الأساسية', 'shipping_s': 'تكلفة الشحن (S)',
        'storage_h': 'تكلفة التخزين (H)', 'waste_rate': 'نسبة التلف %', 'lead_time': 'مدة التوريد',
        'comp_price': 'سعر المنافس'
    }
    
    display_df = st.session_state.db.rename(columns=col_translation)
    edited_df = st.data_editor(display_df, num_rows="dynamic", use_container_width=True, key="main_editor")
    
    if st.button("💾 حفظ وتحديث النظام بالكامل"):
        # إعادة التسمية للأصل البرمجي للحفاظ على استقرار الكود
        reverse_map = {v: k for k, v in col_translation.items()}
        st.session_state.db = edited_df.rename(columns=reverse_map)
        st.success("تم تحديث المحرك المالي بنجاح!")
        st.rerun()

# --- 2. التوأم الرقمي (يتأثر بتكلفة الشحن والتخزين) ---
elif menu == "📊 التوأم الرقمي (المحاكاة)":
    st.header("📊 التوأم الرقمي: تأثير التكاليف على الكميات")
    df = st.session_state.db
    sel_p_name = st.selectbox("اختر المنتج للمعينة:", df['p_name'].unique())
    p = df[df['p_name'] == sel_p_name].iloc[0]
    
    # الحسابات الهندسية
    eoq = calc_eoq(p['daily_demand'], p['shipping_s'], p['storage_h'])
    rop = p['daily_demand'] * p['lead_time']
    
    c1, c2, c3 = st.columns(3)
    c1.metric("الكمية الاقتصادية (EOQ)", f"{int(eoq)} وحدة", help="تتأثر مباشرة بتكلفة الشحن S")
    c2.metric("نقطة إعادة الطلب", f"{int(rop)} وحدة", help="تتأثر بمدة التوريد والسحب")
    c3.metric("مؤشر التغطية", f"{int(p['current_stock']/p['daily_demand'])} أيام")

    # رسم بياني لحالة المخزون
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = p['current_stock'],
        gauge = {'axis': {'range': [0, max(eoq, p['current_stock'])*1.2]},
                 'steps': [{'range': [0, rop], 'color': "red"}],
                 'threshold': {'line': {'color': "black", 'width': 4}, 'value': rop}}))
    st.plotly_chart(fig, use_container_width=True)
    
    
# --- 3. الفواتير والربحية اللحظية (تأثير التلف والسحب) ---
elif menu == "📑 الفواتير والربحية اللحظية":
    st.header("📑 نظام الفواتير والتحليل المالي اليومي")
    df = st.session_state.db.copy()
    
    # معادلات الربحية الواقعية
    df['total_revenue'] = df['daily_demand'] * df['sale_price']
    df['total_cost_sold'] = df['daily_demand'] * df['base_cost']
    df['waste_loss'] = df['total_revenue'] * (df['waste_rate'] / 100)
    df['net_profit'] = df['total_revenue'] - df['total_cost_sold'] - df['waste_loss']
    
    m1, m2, m3 = st.columns(3)
    m1.metric("إجمالي الإيرادات اليومية", f"{df['total_revenue'].sum():,.2f} ريال")
    m2.metric("صافي الربح اليومي", f"{df['net_profit'].sum():,.2f} ريال")
    m3.metric("خسائر التلف المباشرة", f"-{df['waste_loss'].sum():,.2f} ريال", delta_color="inverse")
    
    st.subheader("تفاصيل فواتير السحب اليومي")
    st.dataframe(df[['p_name', 'daily_demand', 'sale_price', 'waste_loss', 'net_profit']], use_container_width=True)

# --- 4. رادار السوق و AI (قراءة المنافسين والتوصيات) ---
elif menu == "💡 رادار السوق و AI":
    st.header("💡 رادار السوق وتوصيات الذكاء الاصطناعي")
    df = st.session_state.db
    
    # تحديد المنتج الأكثر طلباً
    top_p = df.loc[df['daily_demand'].idxmax()]
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📊 المنتجات الأكثر طلباً في السوق")
        fig_bar = px.bar(df, x='p_name', y='daily_demand', color='daily_demand', title="ترتيب الأصناف حسب السحب")
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_right:
        st.subheader("🤖 نصائح AI الاستباقية")
        for index, row in df.iterrows():
            with st.expander(f"تحليل المنتج: {row['p_name']}"):
                # نصيحة بناءً على المنافسة
                if row['sale_price'] > row['comp_price']:
                    st.error(f"⚠️ سعرك أعلى من المنافس. السحب قد ينخفض بنسبة {((row['sale_price']/row['comp_price'])-1)*100:.1f}%.")
                else:
                    st.success("✅ سعرك تنافسي. توقع زيادة في السحب اليومي.")
                
                # نصيحة التكاليف
                if row['waste_rate'] > 2:
                    st.warning(f"📉 التلف مرتفع ({row['waste_rate']}%). هذا يقلل ربحك بمقدار {row['daily_demand']*row['sale_price']*(row['waste_rate']/100):.1f} ريال يومياً.")
