<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>همگام‌ساز هوشمند ستون‌ها</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700&display=swap');
        body { font-family: 'Vazirmatn', sans-serif; }
    </style>
</head>
<body class="bg-gray-50 text-gray-800 min-h-screen flex flex-col justify-between" x-data="dataAligner()">

    <header class="bg-white border-b border-gray-200 py-6 px-8 shadow-sm">
        <div class="max-w-6xl mx-auto flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-bold text-indigo-600">همگام‌ساز هوشمند داده‌ها</h1>
                <p class="text-sm text-gray-500 mt-1">جایگزینی هوشمند مقادیر متناظر بر اساس روابط ستونی</p>
            </div>
            <button @click="resetData()" class="bg-gray-100 hover:bg-gray-200 text-gray-600 px-4 py-2 rounded-lg text-sm font-medium transition">
                بازنشانی داده‌ها
            </button>
        </div>
    </header>

    <main class="max-w-6xl mx-auto p-8 flex-grow w-full grid grid-cols-1 md:grid-cols-3 gap-8">
        
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-between">
            <div>
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-lg font-bold text-gray-700 flex items-center gap-2">
                        <span class="w-3 h-3 rounded-full bg-blue-500"></span> ستون ۱ (متنی)
                    </h2>
                    <span class="text-xs bg-blue-50 text-blue-600 px-2.5 py-1 rounded-full font-medium" x-text="`${col1.length} ردیف`"></span>
                </div>
                <div class="space-y-2 max-h-[400px] overflow-y-auto pr-1">
                    <template x-for="(item, index) in col1" :key="index">
                        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-xl border border-gray-200 hover:border-blue-300 transition">
                            <span class="text-xs text-gray-400 font-mono" x-text="`ردیف ${index + 1}`"></span>
                            <span class="font-semibold text-gray-700 font-mono" x-text="item"></span>
                        </div>
                    </template>
                </div>
            </div>
            <button @click="syncColumn(1)" class="w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-xl shadow-md shadow-blue-100 transition flex justify-center items-center gap-2">
                <span>انتخاب ستون ۱</span>
                <span class="text-xs opacity-80">(جایگزینی مقادیر ستون ۲ در ۱)</span>
            </button>
        </div>

        <div class="bg-gradient-to-br from-indigo-900 to-slate-900 text-white p-6 rounded-2xl shadow-xl flex flex-col justify-between">
            <div>
                <h3 class="text-xl font-bold mb-4 border-b border-indigo-800 pb-3">مکانیزم اثر اثرور (Mechanism)</h3>
                <p class="text-sm text-indigo-200 leading-relaxed mb-6">
                    این ابزار آناتومی روابط بین دو ستون را تحلیل می‌کند. اگر ستون ۱ را انتخاب کنید، سیستم به دنبال مقادیری در ستون ۲ می‌گردد که با ردیف‌های متناظر در ستون ۱ رابطه دارند (مثل رابطه <span class="font-mono text-yellow-300">b ↔ 22</span>)؛ سپس تمام تکرارهای آن مقدار را در ستون هدف اصلاح می‌کند.
                </p>
                
                <div class="bg-indigo-950/50 p-4 rounded-xl border border-indigo-800">
                    <h4 class="text-xs font-bold uppercase tracking-wider text-indigo-400 mb-2">آخرین عملیات سیستمی:</h4>
                    <p class="text-sm font-mono text-emerald-400" x-text="logMessage"></p>
                </div>
            </div>

            <div class="text-xs text-indigo-300 border-t border-indigo-800 pt-4 mt-6">
                طراحی شده بر اساس ساختار منطقی نگاشت داده‌ها.
            </div>
        </div>

        <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-between">
            <div>
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-lg font-bold text-gray-700 flex items-center gap-2">
                        <span class="w-3 h-3 rounded-full bg-emerald-500"></span> ستون ۲ (عددی)
                    </h2>
                    <span class="text-xs bg-emerald-50 text-emerald-600 px-2.5 py-1 rounded-full font-medium" x-text="`${col2.length} ردیف`"></span>
                </div>
                <div class="space-y-2 max-h-[400px] overflow-y-auto pr-1">
                    <template x-for="(item, index) in col2" :key="index">
                        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-xl border border-gray-200 hover:border-emerald-300 transition">
                            <span class="text-xs text-gray-400 font-mono" x-text="`ردیف ${index + 1}`"></span>
                            <span class="font-semibold text-gray-700 font-mono" x-text="item"></span>
                        </div>
                    </template>
                </div>
            </div>
            <button @click="syncColumn(2)" class="w-full mt-6 bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-3 px-4 rounded-xl shadow-md shadow-emerald-100 transition flex justify-center items-center gap-2">
                <span>انتخاب ستون ۲</span>
                <span class="text-xs opacity-80">(جایگزینی مقادیر ستون ۱ در ۲)</span>
            </button>
        </div>

    </main>

    <footer class="bg-white border-t border-gray-200 py-4 text-center text-xs text-gray-400">
        سیستم یکپارچه‌سازی متناظر داده‌ها - توسعه یافته با Alpine.js im
    </footer>

    <script>
        function dataAligner() {
            return {
                // داده‌های اولیه بر اساس سناریوی فرضی شما
                col1: ['a', 'b', 'c', 'd', 'e', 'b'],
                col2: [1, 22, 2, 3, 4, 22],
                logMessage: 'آماده برای پردازش داده‌ها...',

                // تابع اصلی همگام‌سازی ستون‌ها
                syncColumn(selectedCol) {
                    let updatedCount = 0;
                    
                    if (selectedCol === 1) {
                        // شبیه‌سازی دقیق خواسته شما:
                        // ستون ۱ انتخاب شده -> مقادیر دیگر ثابت می‌مانند، اما جایی که b نظیر 22 است، b تبدیل به 22 می‌شود.
                        
                        // ۱. ساخت نقشه نگاشت (Mapping) از ستون ۲ به ستون ۱ برای پیدا کردن روابط متناظر
                        let mapping = {}; // کلید: مقدار ستون ۱ ، مقدار: مقدار ستون ۲
                        
                        for (let i = 0; i < this.col1.length; i++) {
                            let val1 = this.col1[i];
                            let val2 = this.col2[i];
                            // ثبت رابطه (مثلاً b نگاشت می‌شود به 22)
                            if (!mapping[val1]) {
                                mapping[val1] = val2;
                            }
                        }

                        // ۲. اعمال دگرگونی روی ستون ۱ بر اساس نقشه‌ی کشف شده
                        // آرایه جدیدی می‌سازیم تا تغییرات واکنشی اعمال شوند
                        this.col1 = this.col1.map(item => {
                            if (mapping[item] !== undefined) {
                                updatedCount++;
                                return mapping[item].toString(); // b تبدیل به 22 می‌شود
                            }
                            return item;
                        });

                        this.logMessage = `ستون ۱ با موفقیت همگام شد. مقادیر متناظر اصلاح شدند.`;

                    } else if (selectedCol === 2) {
                        // معکوس سناریو: ستون ۲ انتخاب شده و مقادیر ستون ۱ جایگزین تکرارها می‌شوند
                        let mapping = {};
                        for (let i = 0; i < this.col2.length; i++) {
                            let val1 = this.col1[i];
                            let val2 = this.col2[i];
                            if (!mapping[val2]) {
                                mapping[val2] = val1;
                            }
                        }

                        this.col2 = this.col2.map(item => {
                            if (mapping[item] !== undefined) {
                                updatedCount++;
                                return mapping[item];
                            }
                            return item;
                        });

                        this.logMessage = `ستون ۲ با موفقیت همگام شد. مقادیر متناظر اصلاح شدند.`;
                    }
                },

                // بازنشانی به داده‌های اولیه برای تست دوباره
                resetData() {
                    this.col1 = ['a', 'b', 'c', 'd', 'e', 'b'];
                    this.col2 = [1, 22, 2, 3, 4, 22];
                    this.logMessage = 'داده‌ها به حالت اولیه بازگشتند.';
                }
            }
        }
    </script>
</body>
</html>
