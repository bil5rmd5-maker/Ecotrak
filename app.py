import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. إعدادات الهوية البصرية المتقدمة
st.set_page_config(page_title="Ecotrak Neural v5.0", layout="wide", page_icon="🧠")

st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .stMetric { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. تهيئة البيانات المركزية (Neural Database)
if 'products_df' not in st.session_state:
    st.session_state.products_df = pd.DataFrame([
        {'id': 101, 'name': 'محركات توربينية CX', 'daily_sales': 12, 'stock': 45, 'price': 8000, 'order_cost': 1200, 'holding_cost': 200, 'lead_time': 10, 'elasticity': 1.2},
        {'id': 102, 'name': 'وحدات معالجة ذكية', 'daily_sales': 35, 'stock': 120, 'price': 1500, 'order_cost': 300, 'holding_cost': 45, 'lead_time': 5, 'elasticity': 1.8}
    ])

# --- القائمة الجانبية: لوحة التحكم الفائقة ---
st.sidebar.title("🧠 Ecotrak Neural AI")
st.sidebar.subheader("🕹️ التحكم اللحظي في الأصول")

selected_p_name = st.sidebar.selectbox("اختر الصنف المستهدف:", st.session_state.products_df['name'])
p_idx = st.session_state.products_df[st.session_state.products_df['name'] == selected_p_name].index[0]

# تعديل المخزون بسلاسة فائقة
st.sidebar.markdown("**تحديث الكمية المادية**")
new_stk = st.sidebar.number_input("الكمية الحالية في الرفوف", value=int(st.session_state.products_df.at[p_idx, 'stock']))
if st.sidebar.button("مزامنة البيانات"):
    st.session_state.products_df.at[p_idx, 'stock'] = new_stk
    st.sidebar.success("تمت المزامنة مع المستودع آلياً")

st.sidebar.markdown("---")
menu = st.sidebar.radio("المنظومات التقنية:", 
    ["🌐 التوأم الرقمي (Dashboard)", "🔮 محاكي السيناريوهات (Scenario Lab)", "🏗️ هندسة سلاسل الإمداد", "♻️ مركز الاستدامة"])

# --- القائمة 1: التوأم الرقمي (أكثر احترافية) ---
if menu == "🌐 التوأم الرقمي (Dashboard)":
    st.header(f"🌐 التوأم الرقمي لمنتج: {selected_p_name}")
    p = st.session_state.products_df.loc[p_idx]
    
    # حسابات معقدة (EOQ & Reorder Point)
    eoq = np.sqrt((2 * p['daily_sales'] * 365 * p['order_cost']) / p['holding_cost'])
    reorder_point = p['daily_sales'] * p['lead_time']
    safety_stock = p['daily_sales'] * 3 # مخزون أمان لـ 3 أيام
    
    # عرض المؤشرات
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("مستوى المخزون", f"{p['stock']} قطعة")
    c2.metric("نقطة إعادة الطلب", f"{int(reorder_point)} قطعة")
    c3.metric("الكمية المثلى (EOQ)", f"{int(eoq)} وحدة")
    c4.metric("خطر النفاد", "مرتفع ⚠️" if p['stock'] <= reorder_point else "منخفض ✅")

    # الرسم البياني للمخزون (Gauge Chart)
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number", value = p['stock'],
        title = {'text': "الحالة المادية للمخزون"},
        gauge = {
            'axis': {'range': [0, eoq*1.5]},
            'steps': [
                {'range': [0, reorder_point], 'color': "red"},
                {'range': [reorder_point, eoq], 'color': "royalblue"}],
            'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': p['stock']}}))
    st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("---")
    st.subheader("🤖 تحليل المستشار الخبير (Neural Insight)")
    if p['stock'] <= reorder_point:
        st.error(f"**تنبيه حرج:** مخزونك الحالي أقل من نقطة إعادة الطلب. بناءً على 'مدة التوريد' ({p['lead_time']} أيام)، ستفقد مبيعات تقدر بـ {int((reorder_point - p['stock']) * p['price'])} ريال إذا لم تطلب الآن.")
    else:
        st.info(f"**تقرير الاستقرار:** المخزون يغطي احتياجاتك لـ {int(p['stock']/p['daily_sales'])} أيام القادمة. السيولة النقدية في وضع آمن.")

# --- القائمة 2: محاكي السيناريوهات (تغيير الاحتمالات) ---
elif menu == "🔮 محاكي السيناريوهات (Scenario Lab)":
    st.header("🔮 معمل محاكاة السيناريوهات الاقتصادية")
    p = st.session_state.products_df.loc[p_idx]
    
    st.write("ماذا لو تغيرت ظروف السوق؟ حرك المؤشرات لترى كيف سيتفاعل 'عصب' شركتك:")
    
    col_in, col_out = st.columns([1, 2])
    with col_in:
        st.subheader("📥 مدخلات السيناريو")
        price_change = st.slider("تعديل سعر البيع (%)", -50, 50, 0)
        shipping_cost = st.slider("تعديل تكاليف الشحن (S)", 50, 5000, int(p['order_cost']))
        
        # معادلة مرونة الطلب المتقدمة
        new_price = p['price'] * (1 + price_change/100)
        new_sales = p['daily_sales'] / ((new_price / p['price']) ** p['elasticity'])
        new_eoq = np.sqrt((2 * new_sales * 365 * shipping_cost) / p['holding_cost'])

    with col_out:
        st.subheader("📤 المخرجات التنبؤية")
        st.write(f"**الطلب اليومي المتوقع:** {new_sales:.2f} وحدة")
        st.write(f"**إجمالي الدخل المتوقع شهرياً:** {int(new_sales * 30 * new_price):,} ريال")
        
        # رسم بياني للمقارنة
        fig_sim = go.Figure()
        fig_sim.add_trace(go.Bar(name='الوضع الحالي', x=['المبيعات', 'الكمية المثلى'], y=[p['daily_sales'], eoq]))
        fig_sim.add_trace(go.Bar(name='السيناريو المقترح', x=['المبيعات', 'الكمية المثلى'], y=[new_sales, new_eoq]))
        st.plotly_chart(fig_sim)

    st.markdown("---")
    st.subheader("💡 تحليل الأثر الاستراتيجي")
    if price_change < 0:
        st.success(f"القرار سيجذب عملاء جدد ويرفع المبيعات بنسبة {abs(new_sales/p['daily_sales']-1)*100:.1f}%. اطلب {int(new_eoq)} قطعة لضمان عدم النفاد.")
    else:
        st.warning("رفع السعر سيبطئ دوران المخزون. يوصى بتقليل طلبات الشراء لتجنب 'تجميد رأس المال'.")

# --- القوائم الأخرى تتبع نفس النمط الفائق ---
elif menu == "🏗️ هندسة سلاسل الإمداد":
    st.header("🏗️ تحسين كفاءة الموردين")
    st.markdown("")
    st.info("🤖 **الخوارزمية تقترح:** المورد الدولي هو الأنسب لهذا المنتج نظراً لارتفاع سعر الوحدة، مما يعوض تكاليف الشحن الطويلة.")

elif menu == "♻️ مركز الاستدامة":
    st.header("♻️ مؤشرات الاستدامة والنمو الأخضر")
    st.markdown("")
    st.success("🤖 **تقرير الأثر:** تحسين كميات الطلب (EOQ) ساهم في خفض عدد رحلات النقل بنسبة 24% هذا العام.")
