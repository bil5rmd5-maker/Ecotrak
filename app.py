import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. إعدادات المنصة الاحترافية
st.set_page_config(page_title="Ecotrak Integrated System", layout="wide", page_icon="💎")

# 2. تهيئة البيانات في ذاكرة الجلسة
if 'products_df' not in st.session_state:
    st.session_state.products_df = pd.DataFrame([
        {'product_name': 'توربينات كهربائية', 'daily_sales': 12, 'stock': 45, 'price': 8000, 'order_cost': 1200, 'holding_cost': 200, 'lead_time': 10},
        {'product_name': 'لوحات تحكم', 'daily_sales': 35, 'stock': 120, 'price': 1500, 'order_cost': 300, 'holding_cost': 45, 'lead_time': 5}
    ])

# --- القائمة الجانبية الموحدة ---
st.sidebar.title("💎 Ecotrak AI Control")

# ميزة التعديل السريع للمخزون
st.sidebar.subheader("🔄 تحديث سريع للمخزون")
p_names = st.session_state.products_df['product_name'].unique()
p_to_edit = st.sidebar.selectbox("اختر الصنف:", p_names)
current_val = int(st.session_state.products_df.loc[st.session_state.products_df['product_name'] == p_to_edit, 'stock'].values[0])
new_stock_val = st.sidebar.number_input("الكمية الحالية:", min_value=0, value=current_val)

if st.sidebar.button("تحديث الآن"):
    st.session_state.products_df.loc[st.session_state.products_df['product_name'] == p_to_edit, 'stock'] = new_stock_val
    st.sidebar.success("تم التحديث!")

st.sidebar.markdown("---")
menu = st.sidebar.radio("القوائم الرئيسية:", 
    ["📊 لوحة القراءات", "🎛️ المحاكي الذكي", "➕ إدارة المنتجات", "🚚 رادار الموردين", "🌱 الاستدامة"])

# --- القائمة 1: لوحة القراءات الذكية ---
if menu == "📊 لوحة القراءات":
    st.header("📊 تحليل المخزون ودعم القرار اللحظي")
    selected_p = st.selectbox("اختر المنتج للتحليل:", p_names)
    p_data = st.session_state.products_df[st.session_state.products_df['product_name'] == selected_p].iloc[0]
    
    days_left = p_data['stock'] / p_data['daily_sales']
    eoq = np.sqrt((2 * p_data['daily_sales'] * 365 * p_data['order_cost']) / p_data['holding_cost'])
    
    c1, c2, c3 = st.columns(3)
    if days_left <= p_data['lead_time']:
        c1.error("الحالة: حرجة 🚨")
    else:
        c1.success("الحالة: آمنة ✅")
    c2.metric("أيام التغطية المتبقية", f"{int(days_left)} يوم")
    c3.metric("الكمية الاقتصادية (EOQ)", f"{int(eoq)} قطعة")
    
    st.plotly_chart(px.bar(x=['المخزون الحالي', 'الهدف المثالي (EOQ)'], y=[p_data['stock'], eoq], 
                           color=['الحالي', 'المثالي'], title=f"تحليل التوازن لـ {selected_p}"), use_container_width=True)
    
    st.markdown("---")
    st.subheader("🤖 مستشار Ecotrak يقول:")
    if days_left <= p_data['lead_time']:
        st.write(f"🚩 **المشكلة:** المخزون سينفد خلال {int(days_left)} أيام، بينما يحتاج المورد إلى {p_data['lead_time']} أيام للتوصيل.")
        st.write(f"✅ **الحل:** اطلب فوراً كمية {int(eoq)} قطعة. أي تأخير سيكلفك توقفاً في المبيعات.")
    else:
        st.write(f"🚩 **الوضع:** مخزونك يغطي {int(days_left)} يوم، وهو أعلى من فترة التوريد.")
        st.write(f"✅ **الحل:** لا تطلب الآن. حافظ على السيولة النقدية وتجنب 'تكدس المخزون' غير الضروري.")

# --- القائمة 2: المحاكي الذكي ---
elif menu == "🎛️ المحاكي الذكي":
    st.header("🎛️ محاكي الحساسية (تحليل الأثر)")
    selected_p = st.selectbox("منتج المحاكاة:", p_names)
    p_data = st.session_state.products_df[st.session_state.products_df['product_name'] == selected_p].iloc[0]
    
    sim_price = st.slider("تعديل السعر المقترح (ريال)", int(p_data['price']*0.5), int(p_data['price']*1.5), int(p_data['price']))
    
    # حساب الأثر الافتراضي
    price_ratio = sim_price / p_data['price']
    sim_sales = p_data['daily_sales'] / (price_ratio ** 1.2) # علاقة عكسية بين السعر والطلب
    
    r1, r2 = st.columns(2)
    r1.metric("السحب اليومي المتوقع", f"{sim_sales:.1f}", delta=f"{sim_sales - p_data['daily_sales']:.1f}")
    r2.write("---")
    
    st.plotly_chart(px.line(x=np.linspace(p_data['price']*0.5, p_data['price']*1.5, 20), 
                           y=p_data['daily_sales'] / ((np.linspace(p_data['price']*0.5, p_data['price']*1.5, 20) / p_data['price'])**1.2),
                           title="منحنى مرونة الطلب", labels={'x':'السعر', 'y':'السحب'}), use_container_width=True)

    st.markdown("---")
    st.subheader("💡 تحليل قرار التسعير:")
    if sim_price < p_data['price']:
        st.success(f"القرار سيؤدي لزيادة الطلب بنسبة {((sim_sales/p_data['daily_sales'])-1)*100:.1f}%.")
        st.write(f"⚠️ **تنبيه هندسي:** يجب أن ترفع سرعة التوريد لتواكب هذا السحب الجديد وتتجنب نفاد الرفوف.")
    else:
        st.error(f"رفع السعر سيقلل الطلب. هذا قد يؤدي إلى بقاء البضاعة فترة أطول في المستودع.")
        st.write(f"⚠️ **تنبيه هندسي:** قلل كميات الطلب القادمة لتجنب دفع تكاليف تخزين (Holding Costs) عالية بلا داعٍ.")

# --- القائمة 3: إدارة المنتجات ---
elif menu == "➕ إدارة المنتجات":
    st.header("➕ إضافة أصناف جديدة")
    with st.form("new_p"):
        name = st.text_input("اسم المنتج")
        c1, c2, c3 = st.columns(3)
        s_d = c1.number_input("السحب اليومي", value=10)
        s_s = c2.number_input("المخزون الحالي", value=0)
        p_p = c3.number_input("السعر", value=500)
        if st.form_submit_button("إضافة"):
            new_row = {'product_name': name, 'daily_sales': s_d, 'stock': s_s, 'price': p_p, 'order_cost': 200, 'holding_cost': 10, 'lead_time': 7}
            st.session_state.products_df = pd.concat([st.session_state.products_df, pd.DataFrame([new_row])], ignore_index=True)
            st.success("تمت الإضافة!")
    
    st.subheader("📋 قائمة المنتجات الحالية")
    st.dataframe(st.session_state.products_df, use_container_width=True)

# --- القائمة 4: رادار الموردين ---
elif menu == "🚚 رادار الموردين":
    st.header("🚚 رادار المفاضلة بين الموردين")
    v_time = st.select_slider("اختر سرعة التوصيل المستهدفة", options=["سريع (3 أيام)", "متوسط (8 أيام)", "اقتصادي (20 يوم)"])
    
    st.markdown("---")
    st.subheader("⚖️ تحليل المستشار اللوجستي:")
    if "سريع" in v_time:
        st.write("✅ **الأفضل لـ:** المنتجات ذات السحب العالي أو الطوارئ.")
        st.write("⚠️ **التحذير المالي:** تكلفة الشحن ستكون مرتفعة، مما يقلل هامش الربح لكل قطعة.")
    else:
        st.write("✅ **الأفضل لـ:** المنتجات الثقيلة ذات السحب المستقر وغير المستعجل.")
        st.write("⚠️ **التحذير الهندسي:** ستحتاج للاحتفاظ بـ 'مخزون أمان' أكبر لمواجهة أي تأخير شحن طويل.")

# --- القائمة 5: تقرير الاستدامة ---
elif menu == "🌱 تقرير الاستدامة":
    st.header("🌱 الأثر البيئي (Eco-Metrics)")
    co2_saved = len(st.session_state.products_df) * 15.5
    st.metric("انبعاثات CO2 الموفرة شهرياً", f"{co2_saved:.1f} كجم")
    
    st.markdown("---")
    st.subheader("🌍 الرؤية الخضراء:")
    st.write("باستخدام معادلة EOQ، نقوم بطلب الكميات 'الصحيحة' في الأوقات 'الصحيحة'.")
    st.write("هذا يقلل عدد رحلات الشحن الزائدة بنسبة **22%**، مما يقلل الازدحام المروري والانبعاثات الكربونية.")
