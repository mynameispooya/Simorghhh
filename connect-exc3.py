import streamlit as st
import pandas as pd
from datetime import datetime
import io

# ۱. مدیریت وضعیت مرکزی برنامه (Central State Management)
if "files" not in st.session_state:
    st.session_state.files = {}  # ساختار داده: {file_name: DataFrame}
if "history" not in st.session_state:
    st.session_state.history = []
if "clipboard" not in st.session_state:
    st.session_state.clipboard = {
        "action": None,          # 'copy' یا 'cut'
        "source_file": None,
        "source_row_idx": None,
        "row_data": None
    }

def log_action(action_text):
    """ثبت گام‌به‌گام عملیات همراه با زمان دقیق در هاب مرکزی"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.history.append(f"[{now}] {action_text}")

# تنظیمات اصلی رابط کاربری Streamlit
st.set_page_config(page_title="سیستم هوشمند مدیریت و پالایش اکسل", layout="wide")
st.title("📊 سیستم جامع مدیریت، انتقال و پالایش متقاطع داده‌های Excel")
st.caption("انتقال کامل منطق فرانت‌بند به لایه مکانیکی و بهینه‌سازی شده Python & Pandas")

# ۲. بارگذاری فایل‌ها
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
                df = pd.read_excel(uploaded_file, dtype=str).fillna("")
                st.session_state.files[uploaded_file.name] = df
                log_action(f"فایل '{uploaded_file.name}' بارگذاری شد (تعداد ردیف: {len(df)}).")
            except Exception as e:
                st.error(f"خطا در بارگذاری فایل {uploaded_file.name}: {e}")

# ۳. اجرای بدنه اصلی اپلیکیشن پس از بارگذاری فایل‌ها
if st.session_state.files:
    # تقسیم صفحه به دو بخش: سایدبار مدیریتی و پنل عملیات اصلی
    col_sidebar, col_main = st.columns([1, 2])

    # ---------------- ستون راست (سایدبار: دانلود فایل‌ها و تاریخچه) ----------------
    with col_sidebar:
        st.subheader("🗂 فایل‌های سیستم و دانلود خروجی")
        
        for file_name, df in st.session_state.files.items():
            with st.container():
                st.markdown(f"**📄 {file_name}** ({len(df)} ردیف)")
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
                processed_data = output.getvalue()
                
                st.download_button(
                    label="⬇ دانلود نسخه ویرایش شده",
                    data=processed_data,
                    file_name=f"modified_{file_name}",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"dl_{file_name}"
                )
                st.markdown("---")
        
        st.subheader("📜 گزارش تاریخچه سیستم")
        if st.session_state.history:
            st.write(f"گام‌های ثبت شده: {len(st.session_state.history)}")
            history_text = "گزارش گام‌به‌گام تغییرات سیستم مدیریت اکسل\n=================================\n\n" + "\n\n".join(st.session_state.history)
            st.download_button(
                label="📂 دانلود تاریخچه تغییرات (TXT)",
                data=history_text,
                file_name=f"excel_history_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                key="download_history_txt"
            )
        else:
            st.info("هنوز عملیاتی ثبت نشده است.")

    # ---------------- ستون چپ (پنل عملیات اصلی، انتقال ردیف و پالایش) ----------------
    with col_main:
        
        tab_cleanup, tab_move, tab_view = st.tabs(["🧹 پاکسازی متقاطع ستون‌ها", "✂ انتقال ردیف‌ها (Copy/Cut)", "👀 نمای زنده و فیلتر"])

        # ================= TAB 1: پاکسازی متقاطع ستون‌ها با جابجایی ردیف به بالا =================
        with tab_cleanup:
            st.subheader("🧹 پاکسازی ستون و شیفت ردیف‌های پایینی به بالا")
            st.markdown("مقادیر مشترک حذف شده و ردیف‌های پایینی **همان ستون** فوراً به سمت بالا جابجا (Shift Up) می‌شوند تا جای خالی پر شود.")
            
            c1, c2 = st.columns(2)
            with c1:
                src_file_cl = st.selectbox("انتخاب فایل مبدا:", list(st.session_state.files.keys()), key="src_file_cl")
                src_df_cl = st.session_state.files[src_file_cl].copy() # ساخت کپی برای ویرایش امن
                src_col_cl = st.selectbox("انتخاب ستون مبدا جهت پاکسازی:", src_df_cl.columns, key="src_col_cl")
            with c2:
                filter_file_cl = st.selectbox("انتخاب فایل حاوی فیلترها:", list(st.session_state.files.keys()), key="filter_file_cl")
                filter_df_cl = st.session_state.files[filter_file_cl]
                filter_cols_cl = st.multiselect("انتخاب ستون‌های فیلتر کننده (لیست سیاه):", filter_df_cl.columns, key="filter_cols_cl")
            
            if st.button("شروع عملیات حذف مقادیر مشترک", type="primary", key="run_cleanup_btn"):
                if not filter_cols_cl:
                    st.warning("لطفاً حداقل یک ستون فیلترکننده انتخاب کنید.")
                else:
                    # ساخت ساختار مجموعه (Set) از لیست سیاه
                    blacklist = set()
                    for col in filter_cols_cl:
                        cleaned_vals = filter_df_cl[col].astype(str).str.strip().tolist()
                        blacklist.update(cleaned_vals)
                    
                    blacklist.discard("") # حذف رشته‌های خالی از فیلتر
                    
                    # بررسی داده‌های ستون مبدا
                    target_series = src_df_cl[src_col_cl].astype(str).str.strip()
                    matches_mask = target_series.isin(blacklist) & (target_series != "")
                    
                    if matches_mask.any():
                        # استخراج و شمارش مقادیری که قرار است حذف شوند
                        deleted_values_series = src_df_cl.loc[matches_mask, src_col_cl]
                        total_deleted_cells = len(deleted_values_series)
                        value_counts = deleted_values_series.value_counts()
                        
                        # 💥 لایه مکانیکی اصلاح شده: شیفت دادن داده‌ها به سمت بالا (Shift Up)
                        # ابتدا مقادیر ستون مبدا را که جزو لیست سیاه نیستند استخراج می‌کنیم
                        valid_values = src_df_cl.loc[~matches_mask, src_col_cl].tolist()
                        
                        # برای اینکه طول ستون تغییر نکند، به تعداد سلول‌های حذف شده، انتهای لیست را با رشته خالی پر می‌کنیم
                        padding_needed = len(src_df_cl) - len(valid_values)
                        valid_values.extend([""] * padding_needed)
                        
                        # جایگزینی ستون جدیدِ فشرده‌سازی شده در دیتافریم اصلی
                        src_df_cl[src_col_cl] = valid_values
                        st.session_state.files[src_file_cl] = src_df_cl
                        
                        # فرمت‌نویسی گزارش تاریخچه
                        details_list = [f"مقدار '{val}' (تعداد حذف: {count} بار)" for val, count in value_counts.items()]
                        log_msg = (f"پاکسازی متقاطع و فشرده‌سازی: ستون '{src_col_cl}' از فایل '{src_file_cl}' پالایش شد. "
                                   f"تعداد {total_deleted_cells} سلول مشترک حذف و ردیف‌های پایینی به بالا منتقل شدند. "
                                   f"جزئیات مقادیر حذف شده: [{', '.join(details_list)}]")
                        log_action(log_msg)
                        
                        # نمایش نتایج در اپلیکیشن
                        st.success(f"🥳 عملیات با موفقیت انجام شد! ردیف‌های پایینی جایگزین ردیف‌های پاک شده شدند.")
                        
                        st.markdown("**📋 لیست مقادیر (Value) مشترکی که حذف و جابجا شدند:**")
                        for val, count in value_counts.items():
                            st.write(f"🔹 مقدار: `{val}` ➜ {count} بار تکرار و حذف شد.")
                        
                        st.rerun()
                    else:
                        st.info("هیچ مقدار مشترکی بین ستون مبدا و ستون‌های فیلتر انتخاب شده یافت نشد.")

        # ================= TAB 2: انتقال ردیف‌ها (Copy / Cut / Paste) =================
        with tab_move:
            st.subheader("✂ عملیات انتقال و مدیریت ردیف‌ها")
            
            src_file_mv = st.selectbox("۱. انتخاب فایل مبدا:", list(st.session_state.files.keys()), key="src_file_mv")
            src_df_mv = st.session_state.files[src_file_mv]
            
            row_idx = st.number_input(
                f"۲. شماره ردیف مورد نظر را وارد کنید (بین ۲ تا {len(src_df_mv) + 1}):", 
                min_value=2, 
                max_value=len(src_df_mv) + 1, 
                step=1
            )
            
            pandas_idx = row_idx - 2
            
            if pandas_idx < len(src_df_mv):
                current_row_data = src_df_mv.iloc[pandas_idx].to_dict()
                st.json(current_row_data)
                
                c_act1, c_act2 = st.columns(2)
                with c_act1:
                    if st.button("کپی کردن کل ردیف (Copy)", use_container_width=True):
                        st.session_state.clipboard = {
                            "action": "copy",
                            "source_file": src_file_mv,
                            "source_row_idx": row_idx,
                            "row_data": current_row_data
                        }
                        st.toast("📋 ردیف در حافظه موقت کپی شد.")
                with c_act2:
                    if st.button("برش دادن کل ردیف (Cut)", use_container_width=True):
                        st.session_state.clipboard = {
                            "action": "cut",
                            "source_file": src_file_mv,
                            "source_row_idx": row_idx,
                            "row_data": current_row_data
                        }
                        st.toast("✂ ردیف در حافظه موقت برش داده شد.")
            
            if st.session_state.clipboard["action"]:
                st.markdown("---")
                clip = st.session_state.clipboard
                st.info(f"📥 آماده برای قراردهی ردیف بازخوانی شده از فایل '{clip['source_file']}' (ردیف {clip['source_row_idx']}) به روش {clip['action'].upper()}")
                
                dest_file = st.selectbox("۳. فایل مقصد را انتخاب کنید:", list(st.session_state.files.keys()), key="dest_file_select")
                dest_df = st.session_state.files[dest_file]
                dest_col = st.selectbox("۴. ستون کلیدی مقصد (برای بررسی تکراری بودن):", dest_df.columns, key="dest_col_select")
                
                key_value = clip["row_data"].get(dest_col, list(clip["row_data"].values())[0])
                is_duplicate = dest_df[dest_col].astype(str).str.strip().eq(str(key_value).strip()).any()
                
                paste_mode = "Append"
                if is_duplicate:
                    st.warning(f"هشدار: مقدار '{key_value}' در ستون '{dest_col}' فایل مقصد تکراری است.")
                    paste_mode = st.radio("نحوه رفتار با داده تکراری:", ["افزودن به عنوان ردیف جدید (Append)", "جایگزینی روی ردیف تکراری قبلی (Replace)"])
                
                if st.button("اعمال و تثبیت نهایی (Paste)", type="primary"):
                    new_row = {col: clip["row_data"].get(col, "") for col in dest_df.columns}
                    
                    if is_duplicate and "جایگزینی" in paste_mode:
                        dup_idx = dest_df[dest_df[dest_col].astype(str).str.strip() == str(key_value).strip()].index[0]
                        dest_df.iloc[dup_idx] = pd.Series(new_row)
                        log_msg = f"عملیات [{clip['action'].upper()} -> REPLACE]: ردیف {clip['source_row_idx']} از فایل '{clip['source_file']}' روی ردیف تکراری با مقدار '{key_value}' در فایل '{dest_file}' جایگزین شد."
                    else:
                        dest_df = pd.concat([dest_df, pd.DataFrame([new_row])], ignore_index=True)
                        log_msg = f"عملیات [{clip['action'].upper()} -> APPEND]: ردیف {clip['source_row_idx']} از فایل '{clip['source_file']}' به انتهای فایل '{dest_file}' پیوست شد."
                    
                    if clip["action"] == "cut":
                        src_df_to_modify = st.session_state.files[clip["source_file"]]
                        src_df_to_modify = src_df_to_modify.drop(src_df_to_modify.index[clip["source_row_idx"] - 2]).reset_index(drop=True)
                        st.session_state.files[clip["source_file"]] = src_df_to_modify
                        log_msg += f" ضمناً ردیف مبدا حذف فیزیکی گردید."
                    
                    st.session_state.files[dest_file] = dest_df
                    log_action(log_msg)
                    st.success("انتقال داده با موفقیت اعمال شد.")
                    st.session_state.clipboard = {"action": None, "source_file": None, "source_row_idx": None, "row_data": None}
                    st.rerun()

        # ================= TAB 3: نمای زنده، جستجو و فراوانی ستون‌ها =================
        with tab_view:
            st.subheader("👀 فیلتر زنده و آنالیز فراوانی")
            src_file_vi = st.selectbox("انتخاب فایل:", list(st.session_state.files.keys()), key="src_file_vi")
            df_vi = st.session_state.files[src_file_vi]
            src_col_vi = st.selectbox("انتخاب ستون برای آنالیز:", df_vi.columns, key="src_col_vi")
            
            search_query = st.text_input("🔍 عبارت مورد نظر برای فیلتر ستون:")
            
            if search_query:
                filtered_df = df_vi[df_vi[src_col_vi].astype(str).str.contains(search_query, case=False, na=False)]
            else:
                filtered_df = df_vi
            
            st.markdown(f"**📊 جدول فراوانی مقادیر ستون `{src_col_vi}` (نتایج فیلتر شده):**")
            freq_df = filtered_df[src_col_vi].value_counts().reset_index()
            freq_df.columns = ["مقدار (Value)", "تعداد تکرار (Frequency)"]
            st.dataframe(freq_df, use_container_width=True)
            
            st.markdown(f"**📄 نمای ۱۰ سطر اول دیتای جاری:**")
            st.dataframe(filtered_df.head(10), use_container_width=True)

else:
    st.info("💡 برای شروع، فایل‌های اکسل خود را در کادر بالا بارگذاری نمایید.")
