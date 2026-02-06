import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. إعدادات المنصة
st.set_page_config(page_title="Ecotrak Ultimate", layout="wide", page_icon="💎")

# 2. تهيئة البيانات في ذاكرة الجلسة
if 'products_df' not in st.session_state:
    st.session_state.products_df = pd.DataFrame([
        {'product_name': 'توربينات كهربائية', 'daily_sales': 12, 'stock': 45, 'price': 8000, 'order_cost': 1200, 'holding_cost': 200, 'lead_time': 10},
        {'product_name': 'لوحات تحكم', 'daily_sales': 35, 'stock': 120, 'price': 1500, 'order_cost': 300, 'holding_cost': 45, 'lead_time': 5}
    ])

# 3. القائمة الجانبية للتنقل
st.sidebar.title("💎 Ecotrak Control")
menu = st.sidebar.radio("انتقل إلى:", ["📊 لوحة القراءات الذكية", "➕ إضافة منتجات", "🚚 رادار الموردين", "🌱 تقرير الاستدامة"])

# --- القائمة 1: لوحة القراءات الذكية ---
if menu == "📊 لوحة القراءات الذكية":
    st.header("📊 تحليل حالة المنتج والدعم اللحظي")
    
    if not st.session_state.products_df.empty:
        # اختيار المنتج
        selected_p = st.selectbox("اختر المنتج لتحليله:", st.session_state.products_df['product_name'].unique())
        p_data = st.session_state.products_df[st.session_state.products_df['product_name'] == selected_p].iloc[0]
        
        # الحسابات
        days_left = p_data['stock'] / p_data['daily_sales']
        eoq = np.sqrt((2 * p_data['daily_sales'] * 365 * p_data['order_cost']) / p_data['holding_cost'])
        
        # تحديد الكمية المطلوبة لتغطية الاحتياج فقط
        needed_to_order = int(eoq) if days_left <= p_data['lead_time'] else 0
        
        # عرض المؤشرات
        m1, m2, m3 = st.columns(3)
        if days_left <= p_data['lead_time']:
            m1.error("الحالة: حرجة 🚨 (اطلب الآن)")
        else:
            m1.success("الحالة: آمنة ✅")
            
        m2.metric("أيام التغطية المتبقية", f"{int(days_left)} يوم")
        m3.metric("الكمية المطلوب طلبها", f"{needed_to_order} قطعة")

        st.markdown("---")
        st.subheader("💡 نصيحة المستشار الذكي:")
        if needed_to_order > 0:
            st.warning(f"يجب طلب {needed_to_order} قطعة فوراً لتغطية فترة التوريد القادمة.")
        else:
            st.info("المخزون كافٍ حالياً؛ لا تقم بطلب كميات إضافية لتجنب خسائر التخزين الزائد.")

        # رسم بياني توضيحي
        fig = px.bar(x=['المخزون الحالي', 'الكمية المثالية (EOQ)'], y=[p_data['stock'], eoq], 
                     color=['الحالي', 'المثالي'], title=f"تحليل التوازن لـ {selected_p}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد بيانات، أضف منتجات أولاً.")

# --- القائمة 2: إضافة المنتجات ---
elif menu == "➕ إضافة منتجات":
    st.header("➕ إدارة قاعدة بيانات المنتجات")
    with st.form("add_p_form"):
        p_name = st.text_input("اسم المنتج")
        c1, c2, c3 = st.columns(3)
        s_daily = c1.number_input("السحب اليومي", min_value=1, value=10)
        s_current = c2.number_input("المخزون الحالي", min_value=0, value=100)
        p_price = c3.number_input("سعر الوحدة", min_value=1, value=500)
        
        if st.form_submit_button("حفظ المنتج"):
            new_row = {
                'product_name': p_name, 'daily_sales': s_daily, 'stock': s_current, 
                'price': p_price, 'order_cost': 200, 'holding_cost': 10, 'lead_time': 7
            }
            st.session_state.products_df = pd.concat([st.session_state.products_df, pd.DataFrame([new_row])], ignore_index=True)
            st.success("تمت الإضافة بنجاح!")

# --- القائمة 3: رادار الموردين ---
elif menu == "🚚 رادار الموردين":
    st.header("🚚 رادار اختيار المورد الأمثل")
    vendors = pd.DataFrame({
        'المورد': ['محلي', 'إقليمي', 'دولي'],
        'أيام_التوصيل': [3, 8, 20],
        'تكلفة_الشحن': [1000, 500, 150],
        'الجودة': [80, 90, 98]
    })
    fig_v = px.scatter(vendors, x='أيام_التوصيل', y='تكلفة_الشحن', size='الجودة', text='المورد', title="تحديد المورد الأفضل")
    st.plotly_chart(fig_v, use_container_width=True)

# --- القائمة 4: تقرير الاستدامة ---
elif menu == "🌱 تقرير الاستدامة":
    st.header("🌱 الأثر البيئي (Eco-Metrics)")
    total_saved = len(st.session_state.products_df) * 15.2
    st.metric("انبعاثات CO2 الموفرة (كجم)", f"{total_saved:.1f}")
    st.success("بناءً على تحسين كميات الطلب، قمت بتقليل رحلات الشحن غير الضرورية بنسبة 18%.")
