"""Arabic edition of the case studies page.

    python make_ar.py        # case-studies.html -> case-studies-ar.html

Builds the Arabic page from the English one: Arabic copy and data, Cairo for
type, the layout mirrored, and the story gestures turned around (swipe right
for the next case, tap the right edge to go back, arrow keys swapped).
Every replacement must find its text; if the English page changed and a
string is gone, the script stops and names it instead of shipping half a page.
Run it after every edit to the English page, then build-site.ps1.

Figures are the English page's figures. Nothing here adds a number.
"""
import io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = os.path.join(HERE, "case-studies.html"), os.path.join(HERE, "case-studies-ar.html")
EN_URL, AR_URL = "https://claude.ai/artifact/GUMuDPecfJkTZaLWBaaiud", "https://claude.ai/artifact/C1uxFXVECptuqe8ki74juS"
LRI, PDI = "⁦", "⁩"  # keep Latin figures like 4.91x in their own order inside Arabic lines

with io.open(SRC, encoding="utf-8", newline="") as f:
    t = f.read()
CRLF = "\r\n" in t
t = t.replace("\r\n", "\n")  # patterns below are written with \n

def R(old, new, n=1):
    """replace text that must occur exactly n times (n=0: at least once)"""
    global t
    c = t.count(old)
    if (n and c != n) or c == 0:
        sys.exit(f"make_ar: expected {n or 'some'} of {old[:90]!r}, found {c}")
    t = t.replace(old, new)

def RX(pat, new, flags=re.S):
    global t
    t2, c = re.subn(pat, lambda m: new, t, count=1, flags=flags)
    if c != 1:
        sys.exit(f"make_ar: pattern not found: {pat[:80]!r}")
    t = t2

iso = lambda s: LRI + s + PDI

# ── document ─────────────────────────────────────────────────────────────
R("<title>Brandita Case Files</title>", "<title>ملفات حالات برانديتا</title>\n<script>document.documentElement.lang = \"ar\"; document.documentElement.dir = \"rtl\";</script>")

# ── header ───────────────────────────────────────────────────────────────
R('aria-label="Brandita, home"', 'aria-label="برانديتا، الرئيسية"')
R('<span class="bh-tag">Digital marketing · Cairo</span>', '<span class="bh-tag">تسويق رقمي · القاهرة</span>')
R('<a href="#reel" data-v="reel" class="on">Stories</a>', '<a href="#reel" data-v="reel" class="on">القصص</a>')
R('<a href="#all" data-v="all">Case studies</a>', '<a href="#all" data-v="all">دراسات الحالة</a>')
R(f'<a class="bh-lang" href="{AR_URL}" lang="ar" hreflang="ar">العربية</a>', f'<a class="bh-lang" href="{EN_URL}" lang="en" hreflang="en">English</a>')
R('<a class="bh-cta" href="#start" data-cursor="Book"><span>Book a call</span>', '<a class="bh-cta" href="#start" data-cursor="احجز"><span>احجز مكالمة</span>')
R('<nav class="bh-mid" id="views" aria-label="Main">', '<nav class="bh-mid" id="views" aria-label="القائمة">')

# ── phone tab bar ────────────────────────────────────────────────────────
R('aria-label="Sections"', 'aria-label="الأقسام"')
R("<b>Stories</b></a>", "<b>القصص</b></a>")
R("<b>Work</b></a>", "<b>الأعمال</b></a>")
R("<b>Talk</b></a>", "<b>تواصل</b></a>")

# ── stories stage ────────────────────────────────────────────────────────
R('aria-label="Case stories">', 'aria-label="قصص الحالات">')
R('aria-label="Choose a case"', 'aria-label="اختر حالة"')
R("<h1>Work, <em>measured.</em></h1>", "<h1>شغل <em>بالأرقام.</em></h1>")
R("Every case plays like a story: the hook, the leak, the fix, the number and what did not work. Tap through, hold to pause.",
  "كل حالة تعرض كقصة: الهوك، التسريب، الحل، الرقم، وما لم ينجح. اضغط للتقدم، واضغط مطولا للإيقاف.")
R('<span class="l">Tap to advance · Hold to pause · Swipe for the next case</span><span class="s">Tap · Hold to pause · Swipe</span>',
  '<span class="l">اضغط للتقدم · مطولا للإيقاف · اسحب للحالة التالية</span><span class="s">اضغط · مطولا للإيقاف · اسحب</span>')
R('aria-label="Chapters of this case"', 'aria-label="فصول هذه الحالة"')
R('id="cPrev" aria-label="Previous case">←</button>', 'id="cPrev" aria-label="الحالة السابقة">→</button>')
R('id="cNext" aria-label="Next case">→</button>', 'id="cNext" aria-label="الحالة التالية">←</button>')
R('data-pause aria-label="Pause story"></button>', 'data-pause aria-label="إيقاف القصة"></button>')
R('Open the full case <span aria-hidden="true">↗</span>', 'افتح الحالة كاملة <span aria-hidden="true">↖</span>')

# ── index ────────────────────────────────────────────────────────────────
R('<span class="label">Brandita · digital marketing agency · Cairo</span>', '<span class="label">برانديتا · وكالة تسويق رقمي · القاهرة</span>')
R('The case <em>studies.</em></h2>', 'دراسات <em>الحالة.</em></h2>')
R("Each one in the same order: the problem, the fix, the number that moved and what did not work. Open any case; the next one is always a tap away.",
  "كل حالة بنفس الترتيب: المشكلة، الحل، الرقم الذي تحرك، وما لم ينجح. افتح أي حالة، والحالة التالية على بعد ضغطة.")
R('aria-label="Filter by service"', 'aria-label="تصفية حسب الخدمة"')
R("Files marked Sample show the format with placeholder figures. A client's name and numbers are published only with their written sign-off.",
  "الملفات المعلمة «نموذج» توضح الشكل بأرقام افتراضية. لا ننشر اسم عميل أو أرقامه إلا بموافقته المكتوبة.")

# ── close + footer ───────────────────────────────────────────────────────
R('<span class="label">Your turn</span>', '<span class="label">دورك</span>')
R('Your number<br>is <em>next.</em></h2>', 'رقمك<br><em>التالي.</em></h2>')
R("Every engagement starts the same way: an audit of your ad account and your store, and the leak counted in orders a month, before any proposal.",
  "كل تعاقد يبدأ بنفس الطريقة: مراجعة لحساب إعلاناتك ومتجرك، وحساب التسريب بعدد الطلبات شهريا، قبل أي عرض.")
R('data-cursor="Book"><span class="t">Book a free call<small>The audit comes first. The proposal comes after.</small>',
  'data-cursor="احجز"><span class="t">احجز مكالمة مجانية<small>المراجعة أولا، والعرض بعدها.</small>')
R('<div class="lines" role="list" aria-label="Direct lines">', '<div class="lines" role="list" aria-label="خطوط مباشرة">')
R('<span class="k">Write</span>', '<span class="k">اكتب لنا</span>')
R('<span class="k">WhatsApp</span>', '<span class="k">واتساب</span>')
R('data-copy="info@brandita.net">Copy</button>', 'data-copy="info@brandita.net">نسخ</button>')
R('href="tel:+201099307190">Call</a>', 'href="tel:+201099307190">اتصل</a>')
R('<span class="k">Studio</span><span class="v">Cairo, Egypt</span>', '<span class="k">المقر</span><span class="v">القاهرة، مصر</span>')
R('<span>local time</span>', '<span>بتوقيت القاهرة</span>')
# the shared footer (header/header.py renders it)
R('<nav class="bf-nav" aria-label="Site"><a href="#reel">Case stories</a><a href="#all">Case studies</a>', '<nav class="bf-nav" aria-label="الموقع"><a href="#reel">قصص الحالات</a><a href="#all">دراسات الحالة</a>')
R('Ny51PSz3Cb51nps8m1j7D6">For online stores</a>', 'Ny51PSz3Cb51nps8m1j7D6">للمتاجر الإلكترونية</a>')
R('6zCn3cMvHCzk9erCcx5T1C">A full client case</a>', '6zCn3cMvHCzk9erCcx5T1C">حالة عميل كاملة</a>')
R('aria-label="Brandita elsewhere"', 'aria-label="برانديتا على المنصات"')
R("© 2026 All rights reserved — Brandita.net | Cairo, Egypt | info@brandita.net", "© 2026 جميع الحقوق محفوظة — Brandita.net | القاهرة، مصر | info@brandita.net")
R(f'<a href="{AR_URL}" lang="ar" hreflang="ar">العربية</a><a href="#reel">', f'<a href="{EN_URL}" lang="en" hreflang="en">English</a><a href="#reel">')
R('Back to top <span aria-hidden="true">↑</span>', 'العودة للأعلى <span aria-hidden="true">↑</span>')

# ── the case sheet (the full cases inside it are the English case pages) ──
R('aria-modal="true" aria-label="Full case">', 'aria-modal="true" aria-label="الحالة كاملة">')
R('<button type="button" id="dPrev" aria-label="Previous case">←</button><button type="button" id="dNext" aria-label="Next case">→</button><button type="button" id="dClose" aria-label="Close case">×</button>',
  '<button type="button" id="dPrev" aria-label="الحالة السابقة">→</button><button type="button" id="dNext" aria-label="الحالة التالية">←</button><button type="button" id="dClose" aria-label="إغلاق الحالة">×</button>')
R('<button type="button" id="dbPrev" aria-label="Previous case">← Prev</button>', '<button type="button" id="dbPrev" aria-label="الحالة السابقة">→ السابق</button>')
R('#start">Book a call <i aria-hidden="true">', '#start">احجز مكالمة <i aria-hidden="true">')
R('<button type="button" id="dbNext" aria-label="Next case">Next →</button>', '<button type="button" id="dbNext" aria-label="الحالة التالية">التالي ←</button>')
R('aria-modal="true" aria-label="Screenshot">', 'aria-modal="true" aria-label="لقطة شاشة">')
R('<button type="button" id="lbX" aria-label="Close">×</button>', '<button type="button" id="lbX" aria-label="إغلاق">×</button>')

# ── data: Lazoomi (figures unchanged) ────────────────────────────────────
RX(r'    audit: \[.*?\],\n', '    audit: ' + json.dumps([
    "لا متابعة من مشتري الإعلانات السابقين", "إرهاق الإعلانات رفع تكلفة الشراء، ولم يتصرف أحد",
    "لا خطة إعلانات، لا خطة محتوى، لا اختبار عروض، لا دراسة أسعار أو منافسين", "تجربة موقع ضعيفة",
    "نصوص إعلانية بلا كتابة إعلانية حقيقية", "لا هيكل للحملات"], ensure_ascii=False) + ',\n')
RX(r'    levers: \[\n.*?\n    \],\n', '    levers: ' + json.dumps([
    ["مسار الإعلانات", "اختبار، تحديد، توسيع، تكرار. كل إعلان ناجح صار الجولة التالية من الاختبارات.", "", "اختبار ← توسع"],
    ["اختبار عروض متعددة", "اختبرنا العروض حتى وصل أحدها لقيمة الطلب التي يحتاجها العائد المستهدف لربح حقيقي.", "won", "خصم 15% فاز"],
    ["السعر الأساسي", "سعر أعلى من 90% من المنافسين، للوصول للعميل الذي بني البراند من أجله.", "", "ضمن أعلى 10% سعرا"],
    ["اختيار المنتج", "اختبرنا فواحات السيارة والمنزل. السيارة جلبت زيارات ومبيعات أكثر، فركزنا عليها.", "won", "السيارة أولا"],
    ["البيع المكمل", "عبوة الريفيل عند الإضافة للسلة وفي الاقتراحات. باعت بقوة.", "won", "الأبرز: الريفيل"],
    ["قيمة الطلب", "المستهدف 1,000 جنيه للطلب. متوسط السنة 969 جنيه.", "", "969 جنيه"],
    ["شحن مجاني", "شحن مجاني فوق 1,500 جنيه لرفع حجم السلة. لم ينجح.", "miss", "أوقفناه"],
    ["الباقات", "الروائح الأنجح، والروائح مع الريفيل، والسيارة مع المنزل في طلب واحد.", "", "3 باقات"],
    ["التوسع", "بعد التحقق من الاختبارات زاد الإنفاق مع الحفاظ على عائد مربح.", "won", "إنفاق " + iso("5.2×")]],
    ensure_ascii=False) + ',\n')
RX(r'    proof: \[\[.*?\]\]\n', '    proof: ' + json.dumps([
    ["lazoomi-meta-account.png", "مدير إعلانات ميتا، 165 حملة"], ["lazoomi-shopify.png", "تحليلات المتجر"],
    ["lazoomi-monthly-table.png", "شيت التشغيل الشهري"], ["lazoomi-quarterly-profit.png", "المبيعات وصافي الربح حسب الربع"],
    ["lazoomi-hook-tests.png", "سجل اختبار الهوكات"], ["lazoomi-creative-briefs.png", "إطار بريف الإعلانات"]], ensure_ascii=False) + '\n')

# ── data: the sample files (same figures as the English page) ─────────────
ST = lambda *p: [list(x) for x in p]
SAMPLES = [
    dict(id="speed", line="تقنية المتاجر", sector="متجر أزياء", title="ست ثوان على شبكة 4G كانت تضيع أربعة من كل عشرة طلبات من الموبايل",
         leak="الزيارات المدفوعة ثابتة، والفريق على وشك زيادة ميزانية الإعلانات. صفحة المنتج كانت تأخذ 6.1 ثانية حتى تظهر أول صورة على شبكة 4G عادية في القاهرة.",
         sub="بدت كمشكلة إعلانات. كانت صورة رئيسية حجمها 4 ميجا، وأداة تقييمات تعطل عرض الصفحة، وثيم يحمل خطوطا لا يستخدمها.",
         metric="−68%", mlabel="زمن ظهور أول صورة",
         steps=ST(("الاستلام", "فحص التتبع على طلب تجريبي حقيقي."), ("التشخيص", "حساب التسريب بعدد الطلبات شهريا."), ("الإصلاح", "ثلاثة تغييرات بلا إعادة تصميم. أحد عشر يوم عمل."), ("التقرير", "صفحة واحدة، أربعة أرقام، قرار واحد.")),
         compare=[["زمن ظهور أول صورة", 6.1, "6.1 ث", 1.9, "1.9 ث", 7], ["جلسات الموبايل التي وصلت للصفحة", 59, "59%", 94, "94%", 100]],
         miss="أعدنا بناء فلتر الأقسام أيضا، ولم يحرك شيئا."),
    dict(id="arabic", line="السوشيال ميديا", sector="المنزل والمعيشة", title="العربي كان يقرأ كإنجليزي مترجم، والتعليقات أظهرت ذلك",
         leak="التفاعل يبدو جيدا والرسائل فارغة. كل كابشن كان يكتب بالإنجليزية أولا ثم يمر على مترجم.",
         sub="التقويم كان سليما. المشكلة في اللغة: عربي صحيح لا يتكلمه أحد في القاهرة، على صفحة تبيع لمن يتكلمونه.",
         metric=iso("3.4×"), mlabel="رسائل مؤهلة أسبوعيا",
         steps=ST(("الاستلام", "قراءة تعليقات ستة أشهر أولا."), ("التشخيص", "المشكلة في اللغة، لا في الوصول."), ("الإنتاج", "العربي يكتب أولا، والإنجليزي منه."), ("المراجعة", "تغيير واحد أسبوعيا، مع السبب.")),
         compare=[["رسائل مؤهلة أسبوعيا", 5, "5", 17, "17", 20], ["ردود داخل ساعات العمل", 38, "38%", 91, "91%", 100]],
         miss="أول أسبوعين من الكابشن الجديد خفضا الوصول بمقدار الخمس قبل أن يتعافى."),
    dict(id="media", line="الإعلانات المدفوعة", sector="خدمات الشركات", title="تسع حملات، جمهور واحد، وتكلفة طلب لا يستطيع أحد تفسيرها",
         leak="الإنفاق تضاعف ثلاث مرات في سنة والطلبات لم تتحرك. تسع حملات تتنافس على نفس الألفي شخص.",
         sub="الحساب كان مشتتا، لا قليل التمويل. الدمج حقق في ثلاثة أسابيع أكثر مما حققته ستة أشهر من اختبار الإعلانات.",
         metric="−41%", mlabel="تكلفة الطلب",
         steps=ST(("الاستلام", "إنفاق اثني عشر شهرا في عرض واحد."), ("التشخيص", "قياس تداخل الجماهير."), ("الإصلاح", "من تسع حملات إلى ثلاث."), ("التقرير", "رقم واحد متفق عليه عند التوقيع.")),
         compare=[["تكلفة الطلب (مؤشر)", 100, "100", 59, "59", 100], ["الحملات النشطة", 9, "9", 3, "3", 10]],
         miss="الدمج الأول كان مبالغا فيه وتوقف التعلم تسعة أيام. تراجعنا عنه."),
    dict(id="seo", line="السيو والمحتوى", sector="التجميل والعناية", title="ظهور في البحث باسم البراند فقط، ولا شيء مما يبحث عنه الناس قبل الشراء",
         leak="94% من الزيارات غير المدفوعة كانت باسم البراند. الموقع ليس فيه صفحة لما يكتبه الناس قبل أن يعرفوا من أين يشترون.",
         sub="أربع صفحات خدمات مكتوبة حسب نية البحث لا حسب عدد الكلمات. النمو التراكمي بدأ في الشهر الثالث.",
         metric=iso("+5.8×"), mlabel="زيارات بغير اسم البراند",
         steps=ST(("الاستلام", "فصل البحث باسم البراند عن غيره."), ("التشخيص", "خريطة لما يبحث عنه الناس قبل البراند."), ("الإنتاج", "أربع صفحات، لكل صفحة نية واحدة."), ("التقرير", "الشهر الثالث معروض ثابتا، مع السبب.")),
         compare=[["حصة غير البراند من البحث المجاني", 6, "6%", 34, "34%", 100], ["صفحات تجلب زيارات", 2, "2", 21, "21", 24]],
         miss="الشهران الأول والثاني لم يحركا شيئا، ولم نوضح هذا التوقع بما يكفي."),
    dict(id="checkout", line="تقنية المتاجر", sector="متجر إلكترونيات", title="الدفع على الموبايل بطريقة واحدة، ونصف السلات توقفت عندها",
         leak="طلبان من كل ثلاثة جاءا من الموبايل، وصفحة الدفع على الموبايل لا تعرض إلا الدفع عند الاستلام.",
         sub="التسريب كان في الخطوة الأخيرة، حيث قرر المشتري بالفعل.",
         metric=iso("+0.9") + " نقطة", mlabel="معدل تحويل المتجر",
         steps=ST(("الاستلام", "تتبع كل خطوة في الدفع."), ("التشخيص", "التسرب عند اختيار طريقة الدفع."), ("الإصلاح", "إضافة البطاقات والمحافظ."), ("التقرير", "الحركة بالنقاط المئوية.")),
         compare=[["من الدفع إلى طلب مدفوع، موبايل", 48, "48%", 71, "71%", 100], ["معدل تحويل المتجر", 1.4, "1.4%", 2.3, "2.3%", 3]],
         miss="اختبار الدفع في صفحة واحدة لم يحدث فرقا يقاس. أوقفناه."),
    dict(id="replies", line="السوشيال ميديا", sector="الأثاث", title="العملاء يراسلون على واتساب الساعة 11 مساء، والرد يصل 11 صباحا",
         leak="أغلب الاستفسارات تأتي بعد ساعات العمل، وأول رد يستغرق معظم اليوم.",
         sub="الفريق احتاج ردودا محفوظة، ومناوبة ليلية لأول رسالة، وقاعدة لتسليم المحادثة للمبيعات.",
         metric="1.2 س", mlabel="متوسط أول رد، من 9.5 ساعة",
         steps=ST(("الاستلام", "توقيت محادثات ثلاثين يوما."), ("التشخيص", "زمن الرد طابق العملاء الضائعين."), ("الإصلاح", "ردود محفوظة ومناوبة ليلية."), ("المراجعة", "خط زمن الرد كل أحد.")),
         compare=[["متوسط أول رد", 9.5, "9.5 س", 1.2, "1.2 س", 10], ["محادثات تحولت لطلبات", 11, "11%", 19, "19%", 30]],
         miss="رسالة الترحيب الآلية سرعت الرد وأضعفت المحادثات. اختصرناها لسطر واحد."),
    dict(id="identity", line="البراند", sector="قهوة مختصة", title="ثلاثة لوجوهات، أربع درجات أخضر، ومنيو لا يقرأ من الطابور",
         leak="كل فرع صنع لافتاته بنفسه. العملاء لم يعرفوا أن الفرع الثاني هو نفس الشركة.",
         sub="علامة واحدة، أخضر واحد، ونظام منيو يقرأ من أربعة أمتار. التطبيق على الفروع كان هو الشغل.",
         metric=iso("+2.1×"), mlabel="حجم البحث باسم البراند",
         steps=ST(("الاستلام", "تصوير كل لافتة وكوب."), ("التشخيص", "إحصاء أحد عشر شكلا للبراند."), ("الإنتاج", "نظام واحد، مختبر من مسافة الطابور."), ("التقرير", "البحث باسم البراند يتابع شهريا.")),
         compare=[["أشكال البراند المستخدمة", 11, "11", 1, "1", 12], ["البحث باسم البراند (مؤشر)", 100, "100", 210, "210", 220]],
         miss="الكوب الجديد أضاف تكلفة لم تكن في الميزانية. الفروع استخدمت المخزون القديم لربع سنة."),
    dict(id="ramadan", line="الإعلانات المدفوعة", sector="الأغذية والبقالة", title="ميزانية رمضان خلصت في الليلة التاسعة، والطلب مستمر ثلاثة أسابيع",
         leak="المنصة وزعت الإنفاق بالتساوي، والمزاد سحبه للبداية رغم ذلك. أكثر الليالي ازدحاما مرت بلا ميزانية.",
         sub="تقويم من طلبات العام الماضي ليلة بليلة، وميزانية محجوزة للعشر الأواخر، وإعلانات تتغير أسبوعيا.",
         metric="+62%", mlabel="الطلبات في العشر الأواخر",
         steps=ST(("الاستلام", "إعادة بناء رمضان الماضي ليلة بليلة."), ("البريف", "الميزانية في ثلاث فترات من عشر ليال."), ("الإنتاج", "الإعلانات تتغير أسبوعيا."), ("التقرير", "خط يومي للعشر الأواخر.")),
         compare=[["الميزانية المتبقية للعشر الأواخر", 8, "8%", 41, "41%", 100], ["الطلبات في العشر الأواخر (مؤشر)", 100, "100", 162, "162", 170]],
         miss="حجز الميزانية قلل الوصول في الأسبوع الأول، والعميل لاحظ ذلك أولا."),
]
for s in SAMPLES:  # a leading sign or a trailing x would jump sides inside an Arabic line
    if not re.search(r"[؀-ۿ]", s["metric"]) and LRI not in s["metric"]:
        s["metric"] = iso(s["metric"])
RX(r"  const SAMPLES = \[\n.*?\n  \];\n", "  const SAMPLES = [\n    " + ",\n    ".join(json.dumps(s, ensure_ascii=False) for s in SAMPLES) + "\n  ];\n")
R('const CASES = [{ id: "lazoomi", real: true, line: "Performance", sector: "Home fragrance", client: "Lazoomi", title: "Lazoomi went from losing money every month to 4.91× ROAS", metric: "4.91×", mlabel: "Blended ROAS, Mar–Dec 2025", tone: "ink" },',
  'const CASES = [{ id: "lazoomi", real: true, line: "الإعلانات المدفوعة", sector: "معطرات المنزل", client: "لازومي", title: "لازومي انتقلت من الخسارة كل شهر إلى عائد ' + iso("4.91×") + ' على الإعلانات", metric: "' + iso("4.91×") + '", mlabel: "العائد على الإنفاق الإعلاني، مارس–ديسمبر 2025", tone: "ink" },')
R('const META = { lazoomi: ["LZ", "Lazoomi"], speed: ["FR", "Fashion"], arabic: ["HL", "Home"], media: ["B2B", "B2B"], seo: ["BC", "Beauty"],\n    checkout: ["ER", "Electronics"], replies: ["FU", "Furniture"], identity: ["SC", "Coffee"], ramadan: ["FG", "Grocery"] };',
  'const META = { lazoomi: ["LZ", "لازومي"], speed: ["FR", "أزياء"], arabic: ["HL", "منزل"], media: ["B2B", "شركات"], seo: ["BC", "تجميل"],\n    checkout: ["ER", "إلكترونيات"], replies: ["FU", "أثاث"], identity: ["SC", "قهوة"], ramadan: ["FG", "بقالة"] };')
# the poster art is chosen by service line
R('case "Performance":', 'case "الإعلانات المدفوعة":')
R('case "Social":', 'case "السوشيال ميديا":')
R('case "SEO & content":', 'case "السيو والمحتوى":')
R('case "Brand":', 'case "البراند":')

# ── index rows, filters ──────────────────────────────────────────────────
R('const lines = ["All", ...', 'const lines = ["الكل", ...')
R('b.dataset.f === "All"', 'b.dataset.f === "الكل"')
R('aria-label="Open the full case: ${c.client}, ${c.title}"', 'aria-label="افتح الحالة كاملة: ${c.client}، ${c.title}"')
R('c.real ? "Real client" : "Sample"', 'c.real ? "عميل حقيقي" : "نموذج"', 2)
R('aria-label="Play the ${c.client} story"', 'aria-label="شغل قصة ${c.client}"')
R('data-cursor="Open"', 'data-cursor="افتح"', 0)
R('data-cursor="Play"', 'data-cursor="تشغيل"')

# ── story frames ─────────────────────────────────────────────────────────
R('label: "The hook"', 'label: "الهوك"', 2)
R('label: "The leak"', 'label: "التسريب"', 2)
R('label: "The fix"', 'label: "الحل"', 2)
R('label: "The result"', 'label: "النتيجة"', 2)
R('label: "The miss"', 'label: "ما لم ينجح"', 2)
R('label: "The proof"', 'label: "الدليل"')
R('K("The hook that held the most viewers")', 'K("الهوك الذي احتفظ بأكبر عدد من المشاهدين")')
R('<small>hook rate</small>', '<small>معدل الهوك</small>')
R('<p class="cap" data-a="up">“Can you imagine? I actually enjoy driving to work in the mornings now.” (translated) A story ad: opening the car door, diffuser in hand.</p>',
  '<p class="cap" data-a="up">إعلان ستوري: فتح باب السيارة والفواحة في اليد.</p>')
R('K("The leak")', 'K("التسريب")', 2)
R('A strong product, held back by its ads.', 'منتج قوي، تعطله إعلاناته.')
R('What the audit found in the ad account, before a single change.', 'ما وجدته المراجعة في حساب الإعلانات، قبل أي تغيير.')
R('K("The fix")', 'K("الحل")', 2)
R('Nine levers, every one tested. These are the ones that won.', 'تسعة محاور، كلها اختبرت. هذه التي فازت.')
R('K("The result")', 'K("النتيجة")', 2)
R('<b>${num("4,653")} orders</b><small>in November 2025</small>', '<b>${num("4,653")} طلب</b><small>في نوفمبر 2025</small>')
R('<b>EGP ${num("4.21")}M in sales</b><small>that month, from EGP 653K in March</small>', '<b>${num("4.21")} مليون جنيه مبيعات</b><small>في نفس الشهر، من 653 ألف جنيه في مارس</small>')
R('<b>EGP ${num("157")} per purchase</b><small>down 34% from EGP 238</small>', '<b>${num("157")} جنيه لكل عملية شراء</b><small>بانخفاض 34% من 238 جنيه</small>')
R('K("What did not work")', 'K("ما لم ينجح")', 2)
R('<b>Free shipping over EGP 1,500 did not lift order value.</b><span>It was meant to push baskets up. It did not, so it was dropped.</span>',
  '<b>الشحن المجاني فوق 1,500 جنيه لم يرفع قيمة الطلب.</b><span>كان الهدف رفع حجم السلة. لم يحدث، فأوقفناه.</span>')
R('<b>Target EGP 1,000 per order. Landed at EGP 969.</b><span>The refill cross-sell and bundles moved it close, not all the way.</span>',
  '<b>المستهدف 1,000 جنيه للطلب. وصلنا إلى 969 جنيه.</b><span>الريفيل والباقات قربتنا من الهدف، لا كله.</span>')
R('We publish the misses. They are how the next test gets chosen.', 'ننشر ما لم ينجح. منه نختار الاختبار التالي.')
R('K("The proof")', 'K("الدليل")')
R('Straight from the accounts.', 'من الحسابات مباشرة.')
R('K(c.sector + " · sample")', 'K(c.sector + " · نموذج")')
R('<span>Before</span>', '<span>قبل</span>')
R('<span>After</span>', '<span>بعد</span>')
R('Sample file. Placeholder figures that show the format.', 'ملف نموذجي. أرقام افتراضية لتوضيح الشكل.')
# the screens where each sample's leak happened
R('<span>Product page · Cairo 4G</span>', '<span>صفحة المنتج · 4G القاهرة</span>')
R('<em>4MB hero image</em>', '<em>صورة رئيسية 4 ميجا</em>')
R('<b>${num("6.1s")}</b><small>to the first image</small>', '<b>${num("6.1")} ث</b><small>حتى أول صورة</small>')
R('<span class="tg">Translated from English</span>', '<span class="tg">مترجم من الإنجليزية</span>')
R('<b>Inbox</b><span>${num("5")} qualified DMs a week</span>', '<b>الرسائل</b><span>${num("5")} رسائل مؤهلة أسبوعيا</span>')
R('<span>Campaign ${pad(n + 1)}</span><em>Same 2,000 people</em>', '<span>حملة ${pad(n + 1)}</span><em>نفس الألفي شخص</em>')
R('<span>What buyers search before they know you</span>', '<span>ما يبحث عنه المشترون قبل أن يعرفوك</span>')
R('<small>of non-paid traffic was the brand name</small>', '<small>من الزيارات غير المدفوعة كانت باسم البراند</small>')
R('<b class="ph">Payment</b><div class="op on"><i></i>Cash on delivery</div><div class="op off"><i></i>Card<small>not offered</small></div><div class="op off"><i></i>Wallet<small>not offered</small></div>',
  '<b class="ph">الدفع</b><div class="op on"><i></i>الدفع عند الاستلام</div><div class="op off"><i></i>بطاقة<small>غير متاح</small></div><div class="op off"><i></i>محفظة<small>غير متاح</small></div>')
R('${num("48%")} of mobile checkouts reached paid', '${num("48%")} من عمليات الدفع على الموبايل اكتملت')
R('<div class="m in">Is this still available?<time>11:04 PM</time></div><div class="gp">Median first reply ${num("9.5")}h</div><div class="m out">Yes, it is. Sorry for the wait.<time>11:02 AM</time></div>',
  '<div class="m in">لسه متاح؟<time>11:04 م</time></div><div class="gp">متوسط أول رد ${num("9.5")} ساعة</div><div class="m out">أيوه متاح. آسفين على التأخير.<time>11:02 ص</time></div>')
R('<small>Branch ${k + 1}</small>', '<small>فرع ${k + 1}</small>')
R('${num("11")} brand variants in use', '${num("11")} شكلا للبراند مستخدما')
R('Budget gone by night 9. ${num("8%")} left for the last ten nights.', 'الميزانية خلصت في الليلة 9. ${num("8%")} فقط للعشر الأواخر.')

# ── story card chrome, the stage text, WhatsApp ──────────────────────────
R('aria-label="Story ${i + 1} of ${N}: ${c.client}${c.real ? "" : ", sample"}"', 'aria-label="القصة ${i + 1} من ${N}: ${c.client}${c.real ? "" : "، نموذج"}"')
R('`${c.client}${c.real ? "" : ", sample"}: ${c.title}`', '`${c.client}${c.real ? "" : "، نموذج"}: ${c.title}`')
R('c.real ? "Real client · Mar–Dec 2025" : "Sample · " + c.line', 'c.real ? "عميل حقيقي · مارس–ديسمبر 2025" : "نموذج · " + c.line')
R('"Play story"', '"تشغيل القصة"', 0)
R('"Pause story"', '"إيقاف القصة"', 0)
R('<span class="l">Message us about this case</span><span class="s">Message us</span>', '<span class="l">راسلنا عن هذه الحالة</span><span class="s">راسلنا</span>')
R('data-open>Full case ${ICON.up}</button>', 'data-open>الحالة كاملة ${ICON.up}</button>')
R('title="${c.client}: full case"', 'title="${c.client}: الحالة كاملة"')
R('b.textContent = "Copied"', 'b.textContent = "تم النسخ"', 2)
R('encodeURIComponent("Hi Brandita, I saw your case studies and want to talk about my store." + (ad ? "\\nAd: " + ad : ""))',
  'encodeURIComponent("أهلا برانديتا، شفت دراسات الحالة وعايز أتكلم عن متجري." + (ad ? "\\nالإعلان: " + ad : ""))')
R('encodeURIComponent(`Hi Brandita, I watched the ${c.real ? c.client : c.short.toLowerCase() + " sample"} case and want to talk about my store.` + (adTag ? "\\nAd: " + adTag : ""))',
  'encodeURIComponent(`أهلا برانديتا، شفت حالة ${c.real ? c.client : c.short + " (نموذج)"} وعايز أتكلم عن متجري.` + (adTag ? "\\nالإعلان: " + adTag : ""))')
# counters read left to right inside the Arabic line
R('$("#sNo").textContent = `${pad(j + 1)} / ${pad(N)}`', '$("#sNo").textContent = `⁦${pad(j + 1)} / ${pad(N)}⁩`')
R('$("#dNo").textContent = `${pad(i + 1)} / ${pad(N)}`', '$("#dNo").textContent = `⁦${pad(i + 1)} / ${pad(N)}⁩`')
R('`${pad(hbCase + 1)} / ${pad(N)} · ${CASES[hbCase].client}` : at("all") ? `The case studies · ${N} files` : at("start") ? "Your number is next"',
  '`⁦${pad(hbCase + 1)} / ${pad(N)}⁩ · ${CASES[hbCase].client}` : at("all") ? `دراسات الحالة · ${N} ملفات` : at("start") ? "رقمك التالي"')

# ── right to left: the cube turns the other way, the gestures follow ─────
R('rotateY(${a.toFixed(2)}deg)', 'rotateY(${(-a).toFixed(2)}deg)')
R('pd.dir = dx < 0 ? 1 : -1;', 'pd.dir = dx > 0 ? 1 : -1;')
R('Math.min(90, -pd.dir * dx / cube.offsetWidth * 110)', 'Math.min(90, pd.dir * dx / cube.offsetWidth * 110)')
R('if (e.clientX - r.left < r.width * .3) prevFrame(); else nextFrame();', 'if (r.right - e.clientX < r.width * .3) prevFrame(); else nextFrame();')
R('label = held ? "" : e.clientX - r.left < r.width * .3 ? "Back" : "Next";', 'label = held ? "" : r.right - e.clientX < r.width * .3 ? "رجوع" : "التالي";')
R('if (e.key === "ArrowRight") openDetail((dI + 1) % N, null, true); if (e.key === "ArrowLeft") openDetail((dI - 1 + N) % N, null, true);',
  'if (e.key === "ArrowLeft") openDetail((dI + 1) % N, null, true); if (e.key === "ArrowRight") openDetail((dI - 1 + N) % N, null, true);')
R('if (e.key === "ArrowRight") { e.preventDefault(); dismissHint(); if (e.shiftKey) goCase(ci + 1, 1); else nextFrame(); }',
  'if (e.key === "ArrowLeft") { e.preventDefault(); dismissHint(); if (e.shiftKey) goCase(ci + 1, 1); else nextFrame(); }')
R('if (e.key === "ArrowLeft") { e.preventDefault(); dismissHint(); if (e.shiftKey) goCase(ci - 1, -1); else prevFrame(); }',
  'if (e.key === "ArrowRight") { e.preventDefault(); dismissHint(); if (e.shiftKey) goCase(ci - 1, -1); else prevFrame(); }')
R('$$("li", el), { x: -18, opacity: 0 }', '$$("li", el), { x: 18, opacity: 0 }')
R('tx = e.clientX + 170;', 'tx = e.clientX - 170;')

# the Arabic wordmark, in the same tone, wherever the English one sits
BR = json.load(open(os.path.join(HERE, "brand", "brand.json"), encoding="utf-8"))
for tone in ("white", "black"):
    R(BR[f"wm_en_{tone}"]["uri"], BR[f"wm_ar_{tone}"]["uri"], 0)
R(BR["wm_en_white_xl"]["uri"] + '" alt="Brandita" width="%d" height="%d"' % (BR["wm_en_white_xl"]["w"], BR["wm_en_white_xl"]["h"]),
  BR["wm_ar_white_xl"]["uri"] + '" alt="برانديتا" width="%d" height="%d"' % (BR["wm_ar_white_xl"]["w"], BR["wm_ar_white_xl"]["h"]))
AR_W = round(26 * BR["wm_ar_white"]["w"] / BR["wm_ar_white"]["h"])
t = re.sub(r'(class="wm [bw]" src="[^"]+" alt="[^"]*") width="\d+" height="\d+"', lambda m: m.group(1) + f' width="{AR_W}" height="26"', t)
R('alt="Brandita"', 'alt="برانديتا"', 0)
R('alt="Brandita team"', 'alt="فريق برانديتا"')

# phone numbers keep their digit order inside Arabic lines
R(">+20 109 930 7190<", "><span dir=\"ltr\">+20 109 930 7190</span><")
R(">+20 109 986 7256<", "><span dir=\"ltr\">+20 109 986 7256</span><")

# ── right to left: type and the physical sides in the stylesheet ─────────
RTL_CSS = r'''
/* ── Arabic edition: Cairo for type, no tracking (it breaks the joins), room
   for Arabic ascenders, and every physical side mirrored ─────────────────── */
html[dir=rtl] body{font-family:"Cairo","Inter",system-ui,sans-serif}
html[dir=rtl] .bh-logo{--bh-wm-w:69px;--bh-wm-h:24px}
html[dir=rtl] .bf .bf-mark{width:min(100%,640px);margin-inline-end:auto}
html[dir=rtl] body *{letter-spacing:0!important}
html[dir=rtl] :is(h1,h2,h3,.big,.mid,.ix-t,.ix-c b,.missc b,.pc .ch){line-height:1.3}
html[dir=rtl] :is(.chaps button::after,.segs b,.cbr .tr i,.hk .tr i,.qrow .tr i,.cmp .tr i,.agl button::after,.mj-line i){transform-origin:100% 50%}
html[dir=rtl] .chaps button::after{left:0;right:30px}
html[dir=rtl] .hd{left:8px;right:12px}
html[dir=rtl] .pp,html[dir=rtl] .py .op small{margin-left:0;margin-right:auto}
html[dir=rtl] .br .bt span{margin-left:0;margin-right:6px}
html[dir=rtl] .ix-play{margin-right:0;margin-left:12px}
html[dir=rtl] .ix-c b::before{margin-right:0;margin-left:8px}
html[dir=rtl] .lb button{right:auto;left:18px}
html[dir=rtl] .book::before{right:auto;left:11px}
html[dir=rtl] svg:has(> path[d="M7 17 17 7M8 7h9v9"]){transform:scaleX(-1)}
@media (hover:hover) and (pointer:fine){html[dir=rtl] .nav .cta:hover i{transform:rotate(-45deg)}}
'''
R("@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;", RTL_CSS.strip() + "\n@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;")

left = [s for s in re.findall(r">([A-Z][a-z]+(?: [a-z]+){1,})<", t) if s not in ("Brandita",)]
with io.open(OUT, "w", encoding="utf-8", newline="") as f:
    f.write(t.replace("\n", "\r\n") if CRLF else t)
print("wrote case-studies-ar.html" + (f"; English left in markup: {left[:8]}" if left else ""))
