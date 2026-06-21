import streamlit as st
import pandas as pd
from datetime import datetime
import io

# ۱. مدیریت وضعیت مرکزی برنامه (Central State Management)
if "files" not in st.session_state:
    st.session_state.files = {}  # {file_name: DataFrame}
if "history" not in st.session_state:
    st.session_state.history = []

def log_action(action_text):
    """ثبت گام‌به‌گام عملیات همراه با زمان دقیق"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.history.append(f"[{now}] {action_text}")

# تنظیمات هدر صفحه
st.set_page_config(page_title="مدیریت و پالایش هوشمند اکسل", layout="wide")
st.title("📊 سیستم گزارش‌گیری و پالایش متقاطع داده‌های Excel")
st.caption("توسعه یافته بر پایه معماری داده‌محور Streamlit و محاسبات برداری Pandas")

# ۲. بخش بارگذاری فایل‌ها
st.header("📂 بارگذاری فایل‌های اکسل")
uploaded_files = st.file_uploader(
    "فایل‌های اکسل خود را انتخاب کنید (امکان انتخاب همزمان چند فایل)", 
    type=["xlsx", "xls"], 
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.name not in st.session_state.files:
            try:
                # خواندن تمام سلول‌ها به عنوان رشته (String) برای جلوگیری از خطای تغییر تایپ
                df = pd.read_excel(uploaded_file, dtype=str).fillna("")
                st.session_state.files[uploaded_file.name] = df
                log_action(f"فایل '{uploaded_file.name}' با موفقیت بارگذاری شد (تعداد ردیف: {len(df)}).")
            except Exception as e:
                st.error(f"خطا در بارگذاری فایل {uploaded_file.name}: {e}")

# ۳. بدنه اصلی لایوت برنامه
if st.session_state.files:
    col_sidebar, col_main = st.columns([1, 2])

    # ---- ستون راست (مدیریت فایل‌ها و دانلودها) ----
    with col_sidebar:
        st.subheader("🗂 مدیریت فایل‌ها و خروجی‌ها")
        
        for file_name, df in st.session_state.files.items():
            with st.container():
                st.markdown(f"**📄 {file_name}** ({len(df)} ردیف)")
                
                # تبدیل دیتافریم اصلاح شده به باینری اکسل جهت دانلود سریع
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
                processed_data = output.getvalue()
                
                st.download_button(
                    label=f"⬇ دانلود نسخه ویرایش شده",
                    data=processed_data,
                    file_name=f"modified_{file_name}",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"dl_{file_name}"
                )
                st.markdown("---")
        
        # بخش دانلود تاریخچه تغییرات
        st.subheader("📜 گزارش تاریخچه سیستم")
        if st.session_state.history:
            st.write(f"امتیازات ثبت شده: {len(st.session_state.history)} گام")
            history_text = "گزارش گام‌به‌گام تغییرات سیستم\n=================================\n\n" + "\n\n".join(st.session_state.history)
            st.download_button(
                label="📂 دانلود تاریخچه تغییرات (TXT)",
                data=history_text,
                file_name=f"excel_history_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                key="download_history_btn"
            )
        else:
            st.info("هنوز عملیاتی ثبت نشده است.")

    # ---- ستون چپ (عملیات اصلی و فیلتر متقاطع) ----
    with col_main:
        st.subheader("🛠 پنل پالایش و حذف مقادیر مشترک (Set Difference)")
        
        # انتخاب فایل و ستون مبدا (ستون ۱ - مثلاً test)
        src_file = st.selectbox("۱. فایل مبدا را انتخاب کنید:", list(st.session_state.files.keys()), key="src_file_select")
        src_df = st.session_state.files[src_file]
        src_col = st.selectbox("۲. ستون مبدا (که مقادیر از آن پاک شوند) را انتخاب کنید:", src_df.columns, key="src_col_select")
        
        st.markdown("#### تنظیم فیلترهای لیست سیاه (ستون‌های ۲ و ۳...)")
        
        # انتخاب فایل مقصد برای فیلتر
        filter_file = st.selectbox("۳. فایل حاوی ستون‌های فیلترکننده را انتخاب کنید:", list(st.session_state.files.keys()), key="filter_file_select")
        filter_df = st.session_state.files[filter_file]
        
        # انتخاب چندگانه ستون‌های فیلتر کننده (مثلاً test2 و test3 به صورت همزمان)
        filter_cols = st.multiselect("۴. ستون‌های فیلتر کننده (لیست سیاه) را انتخاب کنید:", filter_df.columns, key="filter_cols_select")
        
        # دکمه اجرای عملیات منطقی
        if st.button("🧹 اجرای عملیات حذف مقادیر مشترک", type="primary"):
            if not filter_cols:
                st.warning("لطفاً حداقل یک ستون را به عنوان فیلتر کننده انتخاب کنید.")
            else:
                # مکانیسم اثر اصلاح شده:
                # ۱. جمع‌آوری تمام مقادیر موجود در ستون‌های فیلتر به صورت یک مجمومه یکتا (Set)
                blacklist = set()
                for col in filter_cols:
                    # پاکسازی فاصله‌های خالی و یکدست‌سازی ساختار رشته‌ها
                    values = filter_df[col].astype(str).str.strip().tolist()
                    blacklist.update(values)
                
                # حذف مقادیر تهی از لیست سیاه تا سلول‌های خالی مبدا بیخود دستکاری نشوند
                blacklist.discard("")
                
                # ۲. اعمال فیلتر بر روی ستون مبدا بدون آسیب زدن به سایر ردیف‌ها
                # بررسی می‌کنیم کدام ردیف‌ها در ستون مبدا، مقدارشان درون لیست سیاه وجود دارد
                target_series = src_df[src_col].astype(str).str.strip()
                
                # پیدا کردن ردیف‌های مشترک
                matches_mask = target_series.isin(blacklist)
                affected_rows_count = matches_mask.sum()
                
                if affected_rows_count > 0:
                    # اصلاح دقیق: فقط مقدار سلول در آن ستون خاص به رشته خالی تبدیل می‌شود، نه حذف کل ردیف!
                    src_df.loc[matches_mask, src_col] = ""
                    
                    # ذخیره وضعیت جدید در Session State
                    st.session_state.files[src_file] = src_df
                    
                    # ثبت در لاگ سیستم
                    log_msg = (f"حذف مقادیر مشترک: ستون '{src_col}' از فایل '{src_file}' بر اساس ستون‌های {filter_cols} "
                               f"از فایل '{filter_file}' پالایش شد. تعداد {affected_rows_count} سلول مشترک پاکسازی شدند.")
                    log_action(log_msg)
                    
                    st.success(f"🥳 عملیات با موفقیت انجام شد! تعداد {affected_rows_count} مقدار مشترک در ستون '{src_col}' تخلیه (Clear) شدند.")
                else:
                    st.info("هیچ مقدار مشترکی بین ستون مبدا و ستون‌های فیلتر انتخاب شده پیدا نشد.")
        
        # نمایش زنده خروجی داده‌ها جهت بررسی عینی صحت ساختار
        st.subheader("👀 نمای زنده ۱۰ سطر اول فایل مبدا")
        st.dataframe(st.session_state.files[src_file].head(10), use_container_width=True)

else:
    st.info("💡 برای شروع، فایل‌های اکسل خود را در کادر بالا بارگذاری نمایید.")
