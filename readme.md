# ⛅ תחזית מזג אוויר  — שרת MCP

<div dir="rtl">

[![MCP](https://img.shields.io/badge/Protocol-MCP-6366f1?style=flat-square)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)]()
[![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)]()

**פרויקט לימוד בפיתוח MCP (Model Context Protocol)** — סוכן (Agent) המבוסס LLM שיודע לשלוף תחזית מזג אוויר לערים בישראל ובארה"ב, ולענות עליה בשפה חופשית בצ'אט טרמינל.

</div>

---

## 🎯 מטרת הפרויקט

<div dir="rtl">

לבנות שרת MCP ייעודי שי"מלמד" את ה־LLM לבצע משימה שהוא אינו יודע לבצע באופן טבעי משל עצמו: לשלוף תחזית מזג אוויר עדכנית מאתר ישראלי, כזה שאין לו ממשק API רשמי וזמין.

הסוכן פותר את הבעיה בשתי דרכים משלימות:

| # | מקור | שיטת פעולה | תיאור |
|---|------|-------------|--------|
| 1 | **שרת ישראל** (`weather-Israel`) | אוטומציית דפדפן אמיתי באמצעות **Playwright** | פותח את [weather2day.co.il/forecast](https://weather2day.co.il/forecast), מחפש את העיר המבוקשת, בוחר אותה, ואז מחלץ את תוכן דף התחזית — כדי שה־LLM ינתח אותו בעצמו (גישת **RAG**) |
| 2 | **שרת ארה"ב** (`weather-USA`) | קריאת API רשמית | שולף תחזית והתרעות ישירות דרך ה־API הרשמי של **NWS** (National Weather Service) |

ה־**Host** מחבר את כל השרתים ל־LLM (Gemini, דרך ה־API התואם ל־OpenAI), מעניק להם את כל ה־Tools באופן אוטומטי, ומריץ לולאת שיחה שבה ה־LLM בוחר בעצמו אילו כלי להפעיל ומתי — עד שהמשימה מתקבלת ומתקבלת תשובה סופית.

</div>

---

## 🧩 איך זה עובד (תרשים זרימה)

```text
"משתמש → "מה התחזית בתל אביב?
    │
    ▼
Host  →  LLM (Gemini) בוחר להפעיל Tools
    │
    ▼
(שרת ישראל, בזה אחר זה)
open → enter("תל אביב") → select → get_content
    │
    ▼
LLM (RAG) — חוזר לתוכן התחזית
    │
    ▼
✨ LLM כותב תשובה בשפה חופשית בצ'אט
```

---

## 💬 דוגמאות שימוש

<div dir="rtl">

### תחזית ישראלית (Playwright + RAG)

- `"מה התחזית בתל אביב?"`
- `"תגידי לי אם צריך מטריה מחר בחיפה"`
- `"תפתחי לי את התחזית לבאר שבע"`

### תחזית והתרעות בארה"ב (NWS API)

</div>

- `"What's the weather forecast for San Francisco?"` *(latitude/longitude)*
- `"Are there any weather alerts in California?"`
- `"Show me active weather alerts for NY"`

---

## 🛠️ ארכיטקטורה טכנית

<div dir="rtl">

| רכיב | תפקיד |
|------|-------|
| **Host** | מרכז את השיחה, מחבר בין ה־LLM לשני שרתי ה־MCP, ומנהל את לולאת ה־Tool-Calling |
| **LLM (Gemini)** | מקבל את רשימת ה־Tools הזמינים ומחליט אוטונומית אילו להפעיל, באיזה סדר, ועם אילו פרמטרים |
| **weather-Israel** | שרת MCP שמפעיל Playwright, מדמה משתמש אמיתי בדפדפן, וממיר את תוכן הדף לטקסט הניתן לניתוח |
| **weather-USA** | שרת MCP קליל שמבצע קריאות REST ישירות ל־API של NWS |

</div>

---

## 📝 הערות ולקחים מהפרויקט

<div dir="rtl">

- ה־LLM הוא זה שמחליט אילו Tools להפעיל ובאיזו סדר — לא נכתבה לוגיקת שיחה ידנית וקשיחה; הבחירה נעשית דינמית בזמן ריצה בהתאם לכוונת המשתמש.
- שני קבצי השרת = שני תהליכים נפרדים, ולכן כל מצב משותף (כמו הדפדפן הפתוח) חי בתוך שרת אחד בלבד ואינו משותף בין השניים.
- הגישה המשולבת (Browser Automation + API רשמי) מדגימה כיצד ניתן להעניק ל־LLM יכולות "עולם אמיתי" גם כאשר לא קיים מקור מידע רשמי וזמין.

</div>

---

<div dir="rtl" align="center">

נבנה כפרויקט לימוד ל־**Model Context Protocol** 🔌

</div>
