import asyncio
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright

mcp = FastMCP("weather-Israel")

FORECAST_URL = "https://www.weather2day.co.il/forecast"

# משתנים גלובליים לשמירת מצב הדפדפן בין הפונקציות
playwright_instance = None
browser_instance = None
active_page = None

# מילון תרגום אוטומטי למקרה שהמודל שולח אנגלית (כמו Jerusalem)
CITY_TRANSLATION = {
    "jerusalem": "ירושלים",
    "bnei brak": "בני ברק",
    "bney brak": "בני ברק",
    "tel aviv": "תל אביב",
    "haifa": "חיפה",
    "beer sheva": "באר שבע",
    "ashdod": "אשדוד",
    "netanya": "נתניה",
    "eilat": "אילת",
    "petah tikva": "פתח תקווה",
    "rishon lezion": "ראשון לציון"
}

# 1. הפונקציה פותחת את הדפדפן ומנווטת לדף של אתר מזג האויר.
@mcp.tool()
async def open_weather_forecast_israel() -> str:
    """
    Opens the browser and navigates to the Israel weather forecast website.
    """
    global playwright_instance, browser_instance, active_page
    try:
        if not playwright_instance:
            playwright_instance = await async_playwright().start()
        if not browser_instance:
            browser_instance = await playwright_instance.chromium.launch(headless=False)
        if not active_page:
            # הגדרה חיונית למניעת חסימות SSL של נטפרי בדפדפן האוטומטי
            context = await browser_instance.new_context(ignore_https_errors=True)
            active_page = await context.new_page()
            
        await active_page.goto(FORECAST_URL, wait_until="domcontentloaded")
        return "הדפדפן נפתח וניווט בהצלחה לאתר התחזית."
    except Exception as e:
        return f"שגיאה בפתיחת הדפדפן: {str(e)}"


# 2. הפונקציה מקבלת שם עיר ומזינה את העיר בשדה המתאים שבדף.
@mcp.tool()
async def enter_weather_forecast_city_israel(city: str) -> str:
    """
    Enters the specified city name into the search field on the website.
    
    Args:
        city: The name of the city in Israel to search for.
    """
    global active_page
    if not active_page:
        return "שגיאה: הדפדפן אינו פתוח. יש להפעיל תחילה את open_weather_forecast_israel."
        
    # א) תרגום אוטומטי מאנגלית לעברית (אם המודל שלח Jerusalem וכדומה)
    city_lower = city.lower().strip()
    if city_lower in CITY_TRANSLATION:
        city = CITY_TRANSLATION[city_lower]
        
    # ב) תיקון עברית הפוכה או אותיות יחס מהטרמינל (למשל םילשוריב -> ירושלים)
    if city.endswith("םילשוריב") or "םילשורי" in city:
        city = "ירושלים"
    elif "בני ברק" in city or "קרוב ינב" in city:
        city = "בני ברק"
    elif city.startswith("ב") and len(city) > 3: 
        potential = city[1:]
        if potential in ["ירושלים", "בני ברק", "תל אביב", "חיפה"]:
            city = potential

    try:
        # רשימת סלקטורים אפשריים (כולל אלו שהיו בקוד המקורי שלך)
        selectors = [
            "input#city_search_forecast",  # הסלקטור המקורי שלך
            "input#search-station",
            "input[placeholder*='מזג האוויר']",
            "input[placeholder*='עיר']",
            "input[type='text']"
        ]
        
        target_input = None
        for selector in selectors:
            locator = active_page.locator(selector).first
            if await locator.count() > 0 and await locator.is_visible():
                target_input = locator
                break
                
        # גיבוי אחרון: אם לא מצאנו לפי סלקטור ספציפי, ניקח את אינפוט הטקסט הגלוי הראשון בדף
        if not target_input:
            all_inputs = await active_page.locator("input").all()
            for inp in all_inputs:
                if await inp.is_visible() and await inp.get_attribute("type") in ["text", "search", None]:
                    target_input = inp
                    break
                    
        if not target_input:
            return "שגיאה: לא נמצא שדה חיפוש תואם בדף."
            
        # ביצוע הפעולה הויזואלית באינפוט
        await target_input.click(force=True)
        await target_input.focus()
        await target_input.clear()
        await asyncio.sleep(0.5)
        
        # הקלדה תו-אחר-תו (delay של 120 מילישניות) כדי שתראי את זה נכתב על המסך!
        await target_input.press_sequentially(city, delay=120)
        
        # השהיה קלה בסוף כדי לתת ל-Dropdown של האתר זמן להיפתח ויזואלית
        await asyncio.sleep(1.5) 
        return f"העיר '{city}' הוקלדה בהצלחה בשדה החיפוש."
    except Exception as e:
        return f"שגיאה בהקלטת העיר בשדה: {str(e)}"


# 3. הפונקציה בוחרת את הפריט הראשון ברשימת הערים.
@mcp.tool()
async def select_weather_forecast_city_israel() -> str:
    """
    Selects the first item in the list of cities.
    """
    global active_page
    if not active_page:
        return "שגיאה: הדפדפן אינו פתוח. יש להפעיל תחילה את open_weather_forecast_israel."
        
    try:
        # ניווט במקלדת: ArrowDown מסמן את ההצעה הראשונה ברשימה, Enter בוחר אותה
        # זה עובד ללא תלות בשמות המחלקות של האתר
        await active_page.keyboard.press("ArrowDown")
        await asyncio.sleep(0.3)
        await active_page.keyboard.press("Enter")
        await asyncio.sleep(4)
        return "העיר נבחרה בהצלחה מהרשימה והדף נטען."
    except Exception as e:
        return f"שגיאה בבחירת העיר: {str(e)}"

@mcp.tool()
async def get_weather_forecast_data_israel() -> str:
    """
    Extracts and cleans the text content from the current weather page 
    so the LLM can read the actual forecast data.
    """
    global active_page
    if not active_page:
        return "שגיאה: הדפדפן אינו פתוח או שלא נבחרה עיר עדיין."
        
    try:
        # חילוץ כל הכתב הגלוי מתוך תגית ה-body של העמוד
        raw_text = await active_page.locator("body").inner_text()
        
        # ניקוי בסיסי: פיצול לשורות, הסרת רווחים מיותרים, וסינון שורות ריקות
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        
        # הגבלת כמות הטקסט (למשל 150 השורות הראשונות) כדי לא להעמיס על ה-Context של המודל בפרסומות מיותרות
        cleaned_text = "\n".join(lines[:150])
        
        return cleaned_text
    except Exception as e:
        return f"שגיאה בחילוץ נתוני התחזית מהדף: {str(e)}"

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()