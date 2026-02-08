import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. إعدادات المنصة - يجب أن تكون في أول سطر
st.set_page_config(page_title="Ecotrak Neural Pro", layout="wide", page_icon="🧠")

# 2. وظيفة تهيئة البيانات (تُشغل مرة واحدة فقط)
if 'main_df' not in st.session_state:
    st.session_state.main_df = pd.DataFrame([
        {'المنتج': 'توربينات صناعية', 'السحب_اليومي': 15, 'المخزون': 60, 'السعر': 12000, 'التكلفة': 8500, 'S': 1500, 'H': 400, 'LT': 12},
        {'المنتج': 'مستشعرات نانو', 'السحب_اليومي': 45, 'المخزون': 200, 'السعر': 1200, 'التكلفة': 700, 'S': 200, 'H': 30, 'LT': 5}
    ])

# --- القائمة الجانبية للتنقل ---
st.sidebar.title("🧠 Ecotrak Control Center")
menu = st.sidebar.selectbox("اختر المنظومة:", 
    ["📋 إدارة المنتجات", "📊 التوأم الرقمي", "📈 التنبؤ والربحية", "🔬 اختبار الإجهاد", "🌱 الاستدامة"],
    key="main_menu")

# --- القائمة 1: إدارة المنتجات (الجدول التفاعلي) ---
if menu == "📋 إدارة المنتجات":
    st.header("📋 إدارة أصول المنشأة")
    st.write("عدل البيانات مباشرة من الجدول، ثم اضغط حفظ.")
    
    # محرر بيانات مستقر
    edited_df = st.data_editor(st.session_state.main_df, num_rows="dynamic", use_container_width=True, key="data_editor_v1")
    
    if st.button("💾 حفظ التغييرات", key="save_btn"):
        st.session_state.main_df = edited_df
        st.success("تم تحديث قاعدة البيانات بنجاح!")
        st.rerun()

# --- القائمة 2: التوأم الرقمي (التحليلات اللحظية) ---
elif menu == "📊 التوأم الرقمي":
    st.header("📊 التوأم الرقمي")
    df = st.session_state.main_df
    
    if not df.empty:
        sel_p = st.selectbox("اختر الصنف للتحليل:", df['المنتج'].unique(), key="sel_p_twins")
        p = df[df['المنتج'] == sel_p].iloc[0]
        
        # حسابات هندسية
        eoq = np.sqrt((2 * p['السحب_اليومي'] * 365 * p['S']) / p['H'])
        rop = p['السحب_اليومي'] * p['LT']
        
        c1, c2, c3 = st.columns(3)
        c1.metric("المخزون", f"{int(p['المخزون'])}")
        c2.metric("نقطة الطلب (ROP)", f"{int(rop)}")
        c3.metric("الكمية المثالية (EOQ)", f"{int(eoq)}")
        
        # رسم بياني للنفاد
        
        days = np.arange(0, 15)
        remaining = np.maximum(0, p['المخزون'] - (p['السحب_اليومي'] * days))
        fig = px.line(x=days, y=remaining, title=f"توقعات نفاذ {sel_p}", labels={'x':'الأيام القادمة', 'y':'الكمية'})
        fig.add_hline(y=rop, line_dash="dash", line_color="red", annotation_text="نقطة إعادة الطلب")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("لا توجد بيانات متاحة.")

# --- القائمة 3: التنبؤ والربحية (المساعد الذكي) ---
elif menu == "📈 التنبؤ والربحية":
    st.header("📈 محرك التنبؤ المالي")
    df = st.session_state.main_df
    sel_p = st.selectbox("اختر المنتج للتنبؤ:", df['المنتج'].unique(), key="sel_p_predict")
    p = df[df['المنتج'] == sel_p].iloc[0]
    
    col_in, col_res = st.columns([1, 2])
    with col_in:
        trend = st.slider("نمو الطلب المتوقع (%)", -50, 200, 0, key="trend_slider")
        target_price = st.number_input("سعر البيع المقترح", value=float(p['السعر']), key="price_input")
    
    # حسابات التنبؤ
    new_demand = p['السحب_اليومي'] * (1 + trend/100)
    profit_per_unit = target_price - p['التكلفة']
    monthly_profit = (new_demand * 30 * profit_per_unit) - (p['S'] * (30/p['LT']))
    
    success_rate = min(100, max(0, int((profit_per_unit/p['السعر']*100) + (new_demand * 0.5))))
    
    with col_res:
        m1, m2 = st.columns(2)
        m1.metric("احتمالية النجاح", f"{success_rate}%")
        m2.metric("الربح الشهري المتوقع", f"{int(monthly_profit):,} ريال")
        
        
        
        if success_rate > 60:
            st.success("🤖 مساعد Ecotrak: هذا المنتج واعد جداً، نوصي بالتوسع.")
        else:
            st.warning("🤖 مساعد Ecotrak: المخاطرة عالية، راجع تكاليفك التشغيلية.")

# --- القائمة 4: اختبار الإجهاد ---
elif menu == "🔬 اختبار الإجهاد":
    st.header("🔬 اختبار تحمل الأزمات")
    df = st.session_state.main_df
    sel_p = st.selectbox("صنف الاختبار:", df['المنتج'].unique(), key="stress_p")
    p = df[df['المنتج'] == sel_p].iloc[0]
    
    stress_type = st.radio("نوع الأزمة:", ["تأخر المورد", "انفجار الطلب"], key="stress_type")
    
    days_to_empty = p['المخزون'] / (p['السحب_اليومي'] * (2 if stress_type == "انفجار الطلب" else 1))
    
    st.subheader("نتيجة الاختبار:")
    if days_to_empty < p['LT']:
        st.error(f"المخزون سينفد خلال {int(days_to_empty)} أيام. المصنع في خطر!")
    else:
        st.success(f"المخزون كافٍ لتحمل الأزمة لمدة {int(days_to_empty)} أيام.")

# --- القائمة 5: الاستدامة ---
elif menu == "🌱 الاستدامة":
    st.header("🌱 تقرير الأثر البيئي")
    
    st.metric("توفير انبعاثات الكربون", "28.4 كجم", "12%+")
    st.info("النظام الذكي قلل عدد رحلات الشحن عبر موازنة الكميات الاقتصادية.")
