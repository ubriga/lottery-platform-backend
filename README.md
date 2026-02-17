# Israeli Lottery Platform - Backend

## תיאור המערכת

מערכת מתקדמת לניתוח נתוני הגרלות ישראליות עם עדכון אוטומטי יומי ממקורות רשמיים.

### תכונות עיקריות

- 📊 **איסוף נתונים היסטורי מלא** - כל ההגרלות מיום הקמתן
- 🔄 **עדכון אוטומטי** - GitHub Actions מעדכן נתונים פעם ביום (או לפי הגדרות)
- 🎲 **אנליזה סטטיסטית מתקדמת** - התפלגויות, סימולציות, זיהוי דפוסים
- 🔐 **Admin Panel מלא** - ניהול מקורות, תזמון, ומעקב
- 📈 **REST API** - גישה לכל הנתונים והאנליטיקה

### משחקים נתמכים

- **מפעל הפיס**: לוטו, צ'אנס, 777, 123, מנוי פיס
- **ספורטוטו**: טוטו Winner 16, ווינר עולמי, ווינר מיליונר
- **מרוצי סוסים**: ווינר מרוצים
- **כדורסל וכדורגל**: טוטו צ'אנס

## התקנה מקומית

```bash
# Clone the repository
git clone https://github.com/ubriga/lottery-platform-backend.git
cd lottery-platform-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# ערוך .env והגדר את המשתנים

# Initialize database
python scripts/init_db.py

# Run development server
python app.py
```

## שימוש

### הרצת ETL ידנית
```bash
python scripts/etl_runner.py --game lotto --mode full
python scripts/etl_runner.py --game all --mode incremental
```

### API Endpoints

- `GET /api/games` - רשימת כל המשחקים
- `GET /api/draws/{game_id}` - תוצאות הגרלות
- `GET /api/stats/{game_id}` - סטטיסטיקה מתקדמת
- `GET /api/recommendations/{game_id}` - המלצות על בסיס ניתוח
- `POST /api/admin/trigger-etl` - הפעלת ETL ידנית (דורש אימות)

## GitHub Actions - עדכון אוטומטי

המערכת מעדכנת נתונים אוטומטית כל יום ב-03:00 בלילה.
ניתן לשנות תזמון ב-`.github/workflows/daily-update.yml`

## מבנה הפרויקט

```
lottery-platform-backend/
├── app.py                 # Flask application
├── config.py             # Configuration
├── requirements.txt      # Dependencies
├── models/
│   ├── database.py      # Database models
│   └── games.py         # Game definitions
├── etl/
│   ├── base.py         # Base ETL class
│   ├── pais.py         # מפעל הפיס scrapers
│   └── sportoto.py     # ספורטוטו scrapers
├── analytics/
│   ├── statistics.py   # Statistical analysis
│   ├── patterns.py     # Pattern detection
│   └── recommendations.py  # Recommendation engine
├── api/
│   ├── routes.py       # API endpoints
│   └── auth.py         # Authentication
├── scripts/
│   ├── init_db.py      # Database initialization
│   └── etl_runner.py   # ETL orchestration
└── tests/              # Unit tests
```

## רישיון

MIT License - ראה קובץ LICENSE
