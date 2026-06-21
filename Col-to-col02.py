<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ابزار هوشمند ویرایش و همگام‌سازی اکسل</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700&display=swap');
        body { font-family: 'Vazirmatn', sans-serif; }
    </style>
</head>
<body class="bg-gray-50 text-gray-800 min-h-screen flex flex-col">

    <header class="bg-indigo-600 text-white shadow-md py-6 px-8 mb-8">
        <div class="max-w-7xl mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-bold">مبدل و همگام‌ساز داده‌های اکسل</h1>
            <span class="text-sm bg-indigo-500 px-3 py-1 rounded-full text-indigo-100">نسخه حرفه‌ای v1.0</span>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 w-full flex-grow flex flex-col gap-6">
        
        <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 class="text-lg font-bold mb-4 text-gray-700 flex items-center gap-2">
                <span>۱. بارگذاری فایل ورودی</span>
            </h2>
            <div class="flex items-center justify-center w-full">
                <label class="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition">
                    <div class="flex flex-col items-center justify-center pt-5 pb-6">
                        <svg class="w-8 h-8 mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                        <p class="mb-2 text-sm text-gray-500"><span class="font-bold">برای آپلود کلیک کنید</span> یا فایل را بکشید و رها کنید</p>
                        <p class="text-xs text-gray-400">فقط فایل‌های XLSX یا XLS</p>
                    </div>
                    <input id="excel-file" type="file" class="hidden" accept=".xlsx, .xls" />
                </label>
            </div>
            <div id="file-info" class="mt-3 text-sm text-green-600 hidden font-medium"></div>
        </section>

        <section id="operations-section" class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hidden">
            <h2 class="text-lg font-bold mb-4 text-gray-700">۲. تنظیمات نگاشت و ستون هدف</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-end">
                <div>
                    <label class="block mb-2 text-sm font-medium text-gray-600">انتخاب ستونی که باید تغییر کند (ستون مبدأ):</label>
                    <select id="target-column" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block w-full p-2.5">
                        </select>
                </div>
                
                <div class="flex gap-3">
                    <button id="btn-process" class="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 px-5 rounded-lg transition shadow-sm cursor-pointer text-center">
                        اعمال الگوریتم جایگزینی
                    </button>
                    <button id="btn-export" class="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2.5 px-5 rounded-lg transition shadow-sm cursor-pointer text-center hidden">
                        استخراج اکسل اصلاح‌شده (Export)
                    </button>
                </div>
            </div>
        </section>

        <section id="preview-section" class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex-grow hidden flex flex-col">
            <h2 class="text-lg font-bold mb-4 text-gray-700">پیش‌نمایش داده‌ها</h2>
            <div class="overflow-x-auto border border-gray-200 rounded-lg flex-grow max-h-[400px]">
                <table id="data-table" class="w-full text-sm text-right text-gray-500">
                    <thead id="table-head" class="text-xs text-gray-700 uppercase bg-gray-100 sticky top-0 z-10">
                        </thead>
                    <tbody id="table-body" class="divide-y divide-gray-200">
                        </tbody>
                </table>
            </div>
        </section>
    </main>

    <footer class="bg-gray-100 text-center py-4 text-xs text-gray-500 border-t border-gray-200 mt-8">
        طراحی شده با ساختار تفکر الگوریتمی و متدولوژی مهندسی علّی.
    </footer>

    <script>
        // آبجکت مرکزی برای مدیریت وضعیت داده‌ها در اپلیکیشن
        const AppState = {
            rawData: [],       // داده‌های خام اولیه دریافتی از اکسل
            processedData: [], // داده‌های اصلاح شده بعد از محاسبات
            headers: [],       // نام ستون‌های فایل اکسل
            fileName: ""       // نام فایل آپلود شده
        };

        // عناصر DOM
        const fileInput = document.getElementById('excel-file');
        const fileInfo = document.getElementById('file-info');
        const operationsSection = document.getElementById('operations-section');
        const previewSection = document.getElementById('preview-section');
        const targetColumnSelect = document.getElementById('target-column');
        const btnProcess = document.getElementById('btn-process');
        const btnExport = document.getElementById('btn-export');
        const tableHead = document.getElementById('table-head');
        const tableBody = document.getElementById('table-body');

        // لیسنر آپلود فایل
        fileInput.addEventListener('change', handleFileUpload);
        // لیسنر پردازش داده‌ها
        btnProcess.addEventListener('click', processMapping);
        // لیسنر خروجی گرفتن اکسل
        btnExport.addEventListener('click', exportToExcel);

        function handleFileUpload(e) {
            const file = e.target.files[0];
            if (!file) return;

            AppState.fileName = file.name;
            fileInfo.textContent = `فایل بارگذاری شده: ${file.name}`;
            fileInfo.classList.remove('hidden');

            const reader = new FileReader();
            reader.onload = function(e) {
                const data = new Uint8Array(e.target.result);
                const workbook = XLSX.read(data, { type: 'array' });
                
                // فرض بر این است که اولین Sheet مد نظر کاربر است
                const firstSheetName = workbook.SheetNames[0];
                const worksheet = workbook.Sheets[firstSheetName];
                
                // تبدیل داده‌ها به فرمت JSON (آرایه‌ای از آبجکت‌ها)
                const jsonData = XLSX.utils.sheet_to_json(worksheet, { defval: "" });
                
                if (jsonData.length === 0) {
                    alert("فایل اکسل خالی است یا ساختار نامعتبر دارد.");
                    return;
                }

                AppState.rawData = JSON.parse(JSON.stringify(jsonData)); // Deep Copy
                AppState.processedData = JSON.parse(JSON.stringify(jsonData));
                AppState.headers = Object.keys(jsonData[0]);

                populateSelectOptions();
                renderTable(AppState.rawData);

                operationsSection.classList.remove('hidden');
                previewSection.classList.remove('hidden');
                btnExport.classList.add('hidden'); // مخفی کردن دکمه اکسپورت تا زمان اعمال پردازش
            };
            reader.readAsArrayBuffer(file);
        }

        // پر کردن داینامیک دراپ‌داون ستون‌ها
        function populateSelectOptions() {
            targetColumnSelect.innerHTML = '';
            AppState.headers.forEach(header => {
                const option = document.createElement('option');
                option.value = header;
                option.textContent = header;
                targetColumnSelect.appendChild(option);
            });
        }

        // رندر کردن پیش‌نمایش جدول در صفحه HTML
        function renderTable(data) {
            // رندر هدر
            tableHead.innerHTML = '<tr>';
            AppState.headers.forEach(header => {
                tableHead.innerHTML += `<th scope="col" class="px-6 py-3 font-bold text-gray-700">${header}</th>`;
            });
            tableHead.innerHTML += '</tr>';

            // رندر بدنه
            tableBody.innerHTML = '';
            data.forEach(row => {
                let rowHtml = '<tr class="bg-white hover:bg-gray-50 transition border-b border-gray-100">';
                AppState.headers.forEach(header => {
                    rowHtml += `<td class="px-6 py-4 text-gray-900 font-medium">${row[header] !== undefined ? row[header] : ''}</td>`;
                });
                rowHtml += '</tr>';
                tableBody.innerHTML += rowHtml;
            });
        }

        // هسته منطقی الگوریتم نگاشت علّی و همگام‌سازی جفت‌ها
        function processMapping() {
            const selectedCol = targetColumnSelect.value;
            
            // یافتن ستون مکمل (ستونی که قرار نیست تغییر کند)
            // در سناریوی شما اگر ۲ ستون وجود داشته باشد، ستون دوم مشخص می‌شود. 
            // اگر بیش از دو ستون وجود داشته باشد، ستون مجاور یا اولین ستون غیرمنتخب مبنا قرار می‌گیرد.
            const companionCol = AppState.headers.find(h => h !== selectedCol);
            
            if (!companionCol) {
                alert("برای اجرای این فرآیند، فایل اکسل شما باید حداقل دارای ۲ ستون باشد.");
                return;
            }

            // گام ۱: ساخت دیکشنری یا مپ از تناظرها (نقشه همگام‌سازی)
            // بر اساس ایده شما: یافتن اینکه مقدار ستون هدف به چه مقداری در ستون مکمل نظیر شده است.
            const relationMap = {};
            
            AppState.rawData.forEach(row => {
                const sourceVal = String(row[selectedCol]).trim();
                const companionVal = String(row[companionCol]).trim();
                
                if (sourceVal && companionVal) {
                    // ذخیره تناظر: مقدار ستون منتخب کلید می‌شود و مقدار ستون دیگر ارزش (Value) آن می‌شود.
                    relationMap[sourceVal] = companionVal;
                }
            });

            // گام ۲: اعمال دگرگونی روی ستون انتخابی با حفظ پایداری سایر داده‌ها
            AppState.processedData = AppState.rawData.map(row => {
                const newRow = { ...row };
                const currentVal = String(newRow[selectedCol]).trim();
                
                // اگر برای این مقدار تناظری در مپ پیدا شد، جایگزین می‌شود؛ در غیر این صورت خود مقدار باقی می‌ماند
                if (relationMap[currentVal]) {
                    newRow[selectedCol] = relationMap[currentVal];
                }
                return newRow;
            });

            // بروزرسانی جدول پیش‌نمایش با داده‌های جدید
            renderTable(AppState.processedData);
            
            // نمایش دکمه دانلود خروجی
            btnExport.classList.remove('hidden');
            
            // یک نوتیفیکیشن کوچک برای تایید اعمال موفق
            alert(`تغییرات با موفقیت روی ستون "${selectedCol}" بر اساس روابط زوجی اعمال شد.`);
        }

        // خروجی گرفتن نهایی به فرمت فایل اکسل اصلی
        function exportToExcel() {
            if (AppState.processedData.length === 0) return;

            // تبدیل مجدد آرایه JSON پردازش شده به شیت اکسل
            const worksheet = XLSX.utils.json_to_sheet(AppState.processedData);
            const workbook = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(workbook, worksheet, "ModifiedData");

            // تولید نام فایل خروجی متمایز
            const outputFileName = `modified_${AppState.fileName || 'data.xlsx'}`;

            // دانلود فایل در سیستم کاربر
            XLSX.writeFile(workbook, outputFileName);
        }
    </script>
</body>
</html>
