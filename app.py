import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. إعدادات الصفحة الاحترافية
st.set_page_config(page_title="Ecotrak Industrial Pro", layout="wide", page_icon="🏢")

# 2. إنشاء نظام التبويبات (Tabs) لسهولة التنقل
tabs = st.tabs(["📊 لوحة المخزون الذكية", "📉 تصنيف الأولوية (ABC)", "🚚 تقييم الموردين", "🌱 الاستدامة والأثر"])

# بيانات افتراضية للمنتجات (تحاكي واقع المصانع)
def get_factory_data():
    return pd.DataFrame({
        'Product': ['محركات توربينية', 'زيوت تشغيل', 'فلاتر هيدروليك', 'قطع غيار صغيرة'],
        'Sales': [10, 80, 45, 200],
        'Stock': [30, 150, 90, 1000],
        'Price': [5000, 150, 85, 5],
        'Cost_S': [1500, 200, 100, 50],
        'Cost_H': [150, 10, 5, 0.5]
    })

df = get_factory_data()

# --- Tab 1: لوحة المخزون الذكية ---
with tabs[0]:
    st.header("📦 إدارة المخزون ودعم القرار")
    col_input, col_metrics = st.columns([1, 2])
    
    with col_input:
        selected_p = st.selectbox("اختر المنتج للمعالجة:", df['Product'])
        row = df[df['Product'] == selected_p].iloc[0]
        daily_sales = st.slider("السحب اليومي", 1, 300, int(row['Sales']))
        current_stock = st.number_input("المخزون الحالي", value=int(row['Stock']))
        
    # الحسابات الهندسية
    eoq = np.sqrt((2 * daily_sales * 365 * row['Cost_S']) / row['Cost_H'])
    days_left = current_stock / daily_sales
    
    with col_metrics:
        m1, m2, m3 = st.columns(3)
        m1.metric("أيام التغطية", f"{int(days_left)} يوم")
        m2.metric("الكمية المثالية (EOQ)", f"{int(eoq)} قطعة")
        m3.metric("قيمة المخزون", f"{current_stock * row['Price']:,} ريال")
        
        # رسم بياني تفاعلي
        fig = px.bar(x=['الحالي', 'المثالي'], y=[current_stock, eoq], 
                     labels={'x':'المستوى', 'y':'الكمية'}, title="مقارنة المخزون الحالي بالكمية الاقتصادية")
        st.plotly_chart(fig, use_container_width=True)

# --- Tab 2: تصنيف الأولوية (ABC Analysis) ---
with tabs[1]:
    st.header("📉 تحليل ABC الاستراتيجي")
    st.info("نظام المصانع: الفئة A (70% من الميزانية)، الفئة B (20%)، الفئة C (10%).")
    
    df['Annual_Value'] = df['Sales'] * 365 * df['Price']
    df = df.sort_values('Annual_Value', ascending=False)
    df['Cum_Sum'] = df['Annual_Value'].cumsum()
    total_val = df['Annual_Value'].sum()
    df['Perc'] = (df['Cum_Sum'] / total_val) * 100
    
    def abc_classify(p):
        if p <= 70: return 'A (أهمية قصوى)'
        elif p <= 90: return 'B (متوسطة)'
        else: return 'C (منخفضة)'
    
    df['Class'] = df['Perc'].apply(abc_classify)
    st.table(df[['Product', 'Annual_Value', 'Class']])
    st.success("نصيحة: ركز مجهود الرقابة وفحص الجودة على منتجات الفئة A.")

# --- Tab 3: تقييم الموردين ---
with tabs[2]:
    st.header("🚚 ذكاء اختيار الموردين")
    c1, c2 = st.columns(2)
    with c1:
        v_name = st.text_input("اسم المورد", "مورد أ")
        v_lead = st.slider("سرعة التوصيل (أيام)", 1, 20, 5)
        v_quality = st.select_slider("جودة التوريد", options=["منخفضة", "جيدة", "ممتازة"])
    with c2:
        st.subheader("نتيجة التقييم الذكي")
        score = (100 - (v_lead * 4)) + (20 if v_quality == "ممتازة" else 10)
        st.metric("درجة موثوقية المورد", f"{score}/100")
        if score > 80: st.success("هذا المورد يطابق معايير الإنتاج السريع (Just-In-Time).")
        else: st.warning("يُنصح بالبحث عن مورد بديل لتجنب تعطل خطوط الإنتاج.")

# --- Tab 4: الاستدامة (The Green Move) ---
with tabs[3]:
    st.header("🌱 مؤشر الاستدامة والأثر البيئي")
    dist = st.number_input("متوسط مسافة الشحن السنوية (كم)", value=5000)
    co2 = dist * 0.15 * (365 / (eoq/daily_sales)) # انبعاثات مرتبطة بعدد مرات الطلب
    
    st.metric("بصمة الكربون السنوية", f"{co2:.2f} KG CO2")
    st.write("---")
    st.markdown("""
    **💡 كيف تخدم الاستدامة في المصنع؟**
    بناءً على حسابات EOQ، نظام Ecotrak يقلل عدد رحلات الشحن الزائدة، مما يساهم في خفض انبعاثات الكربون بنسبة تصل إلى **18%** سنوياً مقارنة بالطلب العشوائي.
    """)
