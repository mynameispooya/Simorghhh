import streamlit as st
import pandas as pd
from datetime import datetime
import io

# ۱. مدیریت وضعیت مرکزی برنامه (Central State Management)
if "files" not in st.session_state:
    st.session_state.files = {}  # ساختار داده مرکزی: {file_name: DataFrame}
if "history" not in st.session_state:
    st.session_state.history = []
if "clipboard" not in st.session_state:
    st.session_state.clipboard = {
        "action": None,          # 'copy' یا 'cut'
        "source_file": None,
        "source_row_idx": None,  # شماره ردیف فیزیکی اکسل
        "row_data": None
    }

def log_action(action_text):
    """ثبت گام‌به‌گام و مکانیکی عملیات همراه با زمان دقیق در هاب سیستم"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.history.append(f"[{now}] {action_text}")

# تنظیمات اصلی رابط کاربری Streamlit
st.set_page_config(page_title="سیستم هوشمند مدیریت و پالایش اکسل", layout="wide")
st.title("📊 سیستم جامع مدیریت، انتقال و پالایش متقاطع داده‌های Excel")
st.caption("پیاده‌سازی ساختاریافته فشرده‌سازی سلول‌ها (Shift Up)، جابجایی ردیف کامل و ثبت سوابق در پایتون")

# ۲. هاب بارگذاری فایل‌ها
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
                # خواندن لایو سلول‌ها به صورت رشته جهت جلوگیری از تداخل تایپ داده‌ها
                df = pd.read_excel(uploaded_file, dtype=str).fillna("")
                st.session_state.files[uploaded_file.name] = df
                log_action(f"فایل '{uploaded_file.name}' بارگذاری شد (تعداد ردیف اولیه: {len(df)}).")
            except Exception as e:
                st.error(f"خطا در بارگذاری فایل {uploaded_file.name}: {e}")

# ۳. بدنه اجرایی موتور برنامه
if st.session_state.files:
    # ساختار دو ستونه: سایدبار مدیریتی و پنل فرآیندها
    col_sidebar, col_main = st.columns([1, 2])

    # ---------------- ستون راست (سایدبار: دانلود فایل‌ها و نوتیفیکیشن‌ها) ----------------
    with col_sidebar:
        st.subheader("🗂 فایل‌های سیستم و خروجی‌ها")
        
        for file_name, df in st.session_state.files.items():
            with st.container():
                st.markdown(f"**📄 {file_name}** ({len(df)} ردیف)")
                
                # تبدیل حافظه موقت دیتافریم به باینری اکسل جهت دانلود مستقیم
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
        
        # بخش هاب نوتیفیکیشن و گزارش تغییرات ساختاری (TXT)
        st.subheader("📜 گزارش تاریخچه و تغییرات")
        if st.session_state.history:
            st.write(f"تعداد تغییرات ثبت شده: {len(st.session_state.history)} گام")
            history_text = "گزارش گام‌به‌گام تغییرات سیستم مدیریت اکسل\n=================================\n\n" + "\n\n".join(st.session_state.history)
            st.download_button(
                label="📂 دانلود تاریخچه تغییرات (TXT)",
                data=history_text,
                file_name=f"excel_history_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                key="download_history_txt"
            )
            
            # نمایش ۳ نوتیفیکیشن آخر سیستم به صورت زنده
            st.markdown("**🔔 آخرین نوتیفیکیشن‌های سیستم:**")
            for log in reversed(st.session_state.history[-3:]):
                st.info(log)
        else:
            st.info("هنوز عملیاتی ثبت نشده است.")

    # ---------------- ستون چپ (پنل عملیات اصلی، انتقال ردیف و پالایش زنده) ----------------
    with col_main:
        
        tab_cleanup, tab_move, tab_view = st.tabs([
            "🧹 پاکسازی متقاطع ستون‌ها (با شیفت به بالا)", 
            "✂ انتقال ردیف کامل (Copy/Cut/Paste)", 
            "👀 نمای زنده، جستجو و فراوانی"
        ])

        # ================= TAB 1: پاکسازی متقاطع ستون‌ها همراه با مکانیسم شیفت به بالا =================
        with tab_cleanup:
            st.subheader("🧹 پاکسازی ستون و شیفت خودکار ردیف‌های پایینی به بالا")
            st.markdown("مقادیر مشترک حذف شده و ردیف‌های پایینی **همان ستون** فوراً بالا می‌آیند تا جای خالی پر شود (بدون تغییر در داده‌های سایر ستون‌ها).")
            
            c1, c2 = st.columns(2)
            with c1:
                src_file_cl = st.selectbox("انتخاب فایل مبدا:", list(st.session_state.files.keys()), key="src_file_cl")
                src_df_cl = st.session_state.files[src_file_cl].copy() # ساخت کپی برای کارکرد امن روی حافظه
                src_col_cl = st.selectbox("انتخاب ستون مبدا جهت فشرده‌سازی:", src_df_cl.columns, key="src_col_cl")
            with c2:
                filter_file_cl = st.selectbox("انتخاب فایل حاوی فیلترها (لیست سیاه):", list(st.session_state.files.keys()), key="filter_file_cl")
                filter_df_cl = st.session_state.files[filter_file_cl]
                filter_cols_cl = st.multiselect("انتخاب ستون‌های فیلتر کننده:", filter_df_cl.columns, key="filter_cols_cl")
            
            if st.button("شروع عملیات فیلتر و فشرده‌سازی ستون", type="primary", key="run_cleanup_btn"):
                if not filter_cols_cl:
                    st.warning("لطفاً حداقل یک ستون را به عنوان فیلتر کننده انتخاب کنید.")
                else:
                    # جمع‌آوری تمام مقادیر ستون‌های فیلتر به عنوان لیست سیاه (بدون فضاهای خالی تکراری)
                    blacklist = set()
                    for col in filter_cols_cl:
                        cleaned_vals = filter_df_cl[col].astype(str).str.strip().tolist()
                        blacklist.update(cleaned_vals)
                    
                    blacklist.discard("") # حذف فیلدهای تهی از لیست سیاه
                    
                    # تحلیل و عارضه‌یابی مقادیر ستون مبدا
                    target_series = src_df_cl[src_col_cl].astype(str).str.strip()
                    matches_mask = target_series.isin(blacklist) & (target_series != "")
                    
                    if matches_mask.any():
                        # استخراج مقادیری که قرار است حذف شوند جهت چاپ گزارش فیزیکی به کاربر
                        deleted_values_series = src_df_cl.loc[matches_mask, src_col_cl]
                        total_deleted_cells = len(deleted_values_series)
                        value_counts = deleted_values_series.value_counts()
                        
                        # 💥 پیاده‌سازی مکانیسم لایه‌ای شیفت به بالا (Shift Up)
                        # فقط مقادیری که در لیست سیاه نیستند را استخراج می‌کنیم
                        valid_values = src_df_cl.loc[~matches_mask, src_col_cl].tolist()
                        
                        # برای پر کردن جای خالی انتهای ستون، رشته خالی اضافه می‌کنیم تا طول کل ستون حفظ شود
                        padding_needed = len(src_df_cl) - len(valid_values)
                        valid_values.extend([""] * padding_needed)
                        
                        # تزریق ستون فشرده‌شده جدید به ساختار جدول اصلی
                        src_df_cl[src_col_cl] = valid_values
                        st.session_state.files[src_file_cl] = src_df_cl
                        
                        # فرمت نویسی گزارش نهایی جهت ثبت در نوتیفیکیشن و فایل متنی تاریخچه
                        details_list = [f"مقدار '{val}' ({count} بار)" for val, count in value_counts.items()]
                        log_msg = (f"پاکسازی و شیفت‌آپ: ستون '{src_col_cl}' از فایل '{src_file_cl}' فیلتر شد. "
                                   f"تعداد {total_deleted_cells} سلول مشترک حذف و ردیف‌های پایینی به بالا شیفت داده شدند. "
                                   f"جزئیات آیتم‌های حذف شده: [{', '.join(details_list)}]")
                        log_action(log_msg)
                        
                        st.success(f"🥳 عملیات با موفقیت پایان یافت! مقادیر مشترک حذف و ردیف‌های پایینی جایگزین شدند.")
                        
                        # نمایش دقیق مقادیری که پاکسازی شده‌اند به کاربر
                        st.markdown("**📋 لیست مقادیر (Value) مشترکی که حذف و جابجا شدند:**")
                        for val, count in value_counts.items():
                            st.write(f"🔹 مقدار: `{val}` ➜ {count} بار تکرار و از ستون حذف شد.")
                        
                        st.rerun()
                    else:
                        st.info("هیچ مقدار مشترکی بین ستون مبدا و ستون‌های فیلتر انتخاب شده پیدا نشد.")

        # ================= TAB 2: کپی / کات و جابجایی ردیف کامل بر اساس فرمول درخواستی =================
        with tab_move:
            st.subheader("✂ عملیات مدیریت و انتقال ردیف کامل بین فایل‌ها")
            st.markdown("وقتی ردیفی را کات (Cut) می‌کنید، کل ردیف حذف شده و ردیف‌های زیرین کل جدول یک گام بالا می‌آیند.")
            
            src_file_mv = st.selectbox("۱. انتخاب فایل مبدا ردیف:", list(st.session_state.files.keys()), key="src_file_mv")
            src_df_mv = st.session_state.files[src_file_mv]
            
            row_idx = st.number_input(
                f"۲. شماره ردیف فیزیکی اکسل را وارد کنید (بین ۲ تا {len(src_df_mv) + 1}):", 
                min_value=2, 
                max_value=len(src_df_mv) + 1, 
                step=1
            )
            
            # تبدیل آدرس فیزیکی اکسل به ایندکس پانداس (ردیف ۲ اکسل یعنی ایندکس ۰)
            pandas_idx = row_idx - 2
            
            if pandas_idx < len(src_df_mv):
                current_row_data = src_df_mv.iloc[pandas_idx].to_dict()
                st.markdown("**📋 ساختار داده‌های ردیف انتخاب شده:**")
                st.json(current_row_data)
                
                c_act1, c_act2 = st.columns(2)
                with c_act1:
                    if st.button("کپی کردن ردیف کامل (Copy)", use_container_width=True):
                        st.session_state.clipboard = {
                            "action": "copy",
                            "source_file": src_file_mv,
                            "source_row_idx": row_idx,
                            "row_data": current_row_data
                        }
                        st.toast("📋 ردیف کامل در حافظه کپی شد.")
                with c_act2:
                    if st.button("برش دادن ردیف کامل (Cut)", use_container_width=True):
                        st.session_state.clipboard = {
                            "action": "cut",
                            "source_file": src_file_mv,
                            "source_row_idx": row_idx,
                            "row_data": current_row_data
                        }
                        st.toast("✂ ردیف کامل برش داده شد.")
            
            # بررسی پر بودن کلیپ‌بورد جهت فعال‌سازی لایه فیزیکی Paste
            if st.session_state.clipboard["action"]:
                st.markdown("---")
                clip = st.session_state.clipboard
                st.info(f"📥 آماده برای نشاندن ردیف انتقالی از فایل '{clip['source_file']}' (ردیف {clip['source_row_idx']}) به روش {clip['action'].upper()}")
                
                dest_file = st.selectbox("۳. فایل مقصد را تعیین کنید:", list(st.session_state.files.keys()), key="dest_file_select")
                dest_df = st.session_state.files[dest_file].copy()
                dest_col = st.selectbox("۴. ستونی که می‌خواهید بررسی تکرار روی آن انجام شود انتخاب کنید:", dest_df.columns, key="dest_col_select")
                
                # استخراج مقدار کلیدی ردیف در حال انتقال براساس ستون انتخابی شما
                key_value = clip["row_data"].get(dest_col, "")
                
                # چک کردن مکانیکی تکراری بودن این مقدار در ستون مقصد
                is_duplicate = dest_df[dest_col].astype(str).str.strip().eq(str(key_value).strip()).any()
                
                paste_mode = "الحاق به عنوان ردیف جدید (Append)"
                if is_duplicate:
                    st.warning(f"⚠️ تذکر: مقدار کلیدی '{key_value}' در ستون '{dest_col}' فایل مقصد تکراری است!")
                    paste_mode = st.radio("چگونه مایلید عملیات ادامه پیدا کند؟", ["الحاق به عنوان ردیف جدید (Append)", "جایگزینی و اوررایت روی ردیف قبلی (Replace)"])
                
                if st.button("تثبیت و اعمال نهایی در پایین‌ترین ردیف (Paste)", type="primary"):
                    # ساخت یک دیکشنری تمیز هماهنگ با ستون‌های فایل مقصد
                    new_row = {col: clip["row_data"].get(col, "") for col in dest_df.columns}
                    
                    log_msg = ""
                    if is_duplicate and "جایگزینی" in paste_mode:
                        # پیدا کردن اولین ردیف تکراری و بازنویسی مقادیر روی آن ردیف
                        dup_idx = dest_df[dest_df[dest_col].astype(str).str.strip() == str(key_value).strip()].index[0]
                        dest_df.iloc[dup_idx] = pd.Series(new_row)
                        log_msg = f"انتقال [{clip['action'].upper()} -> REPLACE]: داده‌های ردیف {clip['source_row_idx']} فایل '{clip['source_file']}' به دلیل تکراری بودن مقدار '{key_value}' روی ردیف {dup_idx + 2} فایل '{dest_file}' جایگزین شدند."
                    else:
                        # اضافه کردن به پایین‌ترین ردیف فایل مقصد (Append)
                        dest_df = pd.concat([dest_df, pd.DataFrame([new_row])], ignore_index=True)
                        log_msg = f"انتقال [{clip['action'].upper()} -> APPEND]: ردیف {clip['source_row_idx']} فایل '{clip['source_file']}' به پایین‌ترین سطر فایل مقصد '{dest_file}' الحاق شد."
                    
                    # اگر عملیات کات بود، ردیف فیزیکی مبدا را کلاً حذف کن (ردیف‌های زیرین جدول شیفت آپ می‌شوند)
                    if clip["action"] == "cut":
                        src_df_to_modify = st.session_state.files[clip["source_file"]].copy()
                        # حذف سطر مبدا و ریست کردن اندیس پانداس برای شیفت فیزیکی سطرها به بالا
                        src_df_to_modify = src_df_to_modify.drop(src_df_to_modify.index[clip["source_row_idx"] - 2]).reset_index(drop=True)
                        st.session_state.files[clip["source_file"]] = src_df_to_modify
                        log_msg += f" ضمناً ردیف {clip['source_row_idx']} از فایل مبدا کلاً حذف و ردیف‌های پایینی آن به بالا منتقل شدند."
                    
                    # بروزرسانی حافظه نشست
                    st.session_state.files[dest_file] = dest_df
                    log_action(log_msg)
                    st.success("انتقال و بازچیدمان ردیف‌ها با موفقیت اعمال شد.")
                    
                    # ریست کردن وضعیت کلپ‌بورد سیستم
                    st.session_state.clipboard = {"action": None, "source_file": None, "source_row_idx": None, "row_data": None}
                    st.rerun()

        # ================= TAB 3: نمای زنده، سیستم گلچین کردن با سرچ و فراوانی مقادیر =================
        with tab_view:
            st.subheader("🔍 فیلتر زنده و آنالیز توزیع فراوانی ستون‌ها")
            src_file_vi = st.selectbox("انتخاب فایل جهت بررسی:", list(st.session_state.files.keys()), key="src_file_vi")
            df_vi = st.session_state.files[src_file_vi]
            src_col_vi = st.selectbox("انتخاب ستون برای تحلیل فراوانی و سرچ (مثلاً شغل):", df_vi.columns, key="src_col_vi")
            
            search_query = st.text_input("🔍 عبارت مورد نظر را برای گلچین کردن بنویسید (مثلاً راننده):")
            
            # منطق فیلتر و پیدا کردن ردیف‌ها براساس جستجو
            if search_query:
                # ایجاد یک کپی همراه با ستون آدرس فیزیکی ردیف اکسل جهت نمایش مختصات دقیق به کاربر
                display_df = df_vi.copy()
                display_df["مختصات فیزیکی (ردیف اکسل)"] = [i + 2 for i in range(len(df_vi))]
                
                filtered_df = display_df[display_df[src_col_vi].astype(str).str.contains(search_query, case=False, na=False)]
            else:
                display_df = df_vi.copy()
                display_df["مختصات فیزیکی (ردیف اکسل)"] = [i + 2 for i in range(len(df_vi))]
                filtered_df = display_df
            
            # ۱. محاسبه و نمایش توزیع فراوانی مقادیر به فرمت درخواستی شما (راننده: ۲۰، خواننده: ۱۰)
            st.markdown(f"**📊 توزیع فراوانی مقادیر در ستون `{src_col_vi}` (نتایج فیلتر شده):**")
            value_counts_analysis = filtered_df[src_col_vi].value_counts()
            
            if not value_counts_analysis.empty:
                # ایجاد چیپ یا تکست باکس‌های کوچک برای نمایش خوانای فراوانی‌ها
                cols_count = st.columns(4)
                for idx, (val, count) in enumerate(value_counts_analysis.items()):
                    if val.strip() != "":
                        with cols_count[idx % 4]:
                            st.metric(label=f"مقدار: {val}", value=f"{count} بار")
            else:
                st.info("هیچ داده‌ای یافت نشد.")
            
            # ۲. نمایش دیتا به همراه مختصات ردیف (۱۰ ردیف اول در حالت عادی / یا کل نتایج سرچ)
            if search_query:
                st.markdown(f"**🎯 ردیف‌های گلچین شده بر اساس عبارت '{search_query}' (تعداد: {len(filtered_df)} ردیف):**")
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.markdown(f"**📄 نمای پیش‌فرض ۱۰ سطر اول فایل (جهت جلوگیری از شلوغی):**")
                st.dataframe(filtered_df.head(10), use_container_width=True)

else:
    st.info("💡 برای شروع، فایل‌های اکسل خود را در کادر بالا بارگذاری نمایید.")
