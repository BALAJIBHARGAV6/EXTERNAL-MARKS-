# # 🎓 MIC Exam Results Scraper - NUCLEAR EDITION

**Lightning Fast Exam Results Portal** - Get complete student marks in **0.27 seconds**! ⚡

## 🚀 Features

- ⚡ **Ultra Fast**: 0.27 seconds execution time (98% faster than browser-based solutions)
- 🎨 **Beautiful Web Interface**: Modern, responsive design with gradient UI
- 📊 **Complete Data**: Semester summary (SGPA/CGPA) + Detailed marks for all subjects
- 🔒 **No Browser Required**: Uses pure Python `requests` library (no Playwright/Selenium overhead)
- 📱 **Mobile Friendly**: Fully responsive design works on all devices
- 🎯 **Production Ready**: Clean code, error handling, and CORS enabled

## 📸 Screenshots

### Web Interface
- Clean search interface with registration number input
- Real-time loading status
- CGPA/SGPA cards display
- Color-coded grades (A+/A in green, B in blue, C/D in yellow, F in red)
- Two comprehensive tables: Semester Summary + Detailed Marks

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Required Packages

```bash
# Install all required packages
pip install flask flask-cors requests beautifulsoup4 lxml
```

**Package Details:**
- `flask` (3.0.0+) - Web framework for API
- `flask-cors` (4.0.0+) - Cross-Origin Resource Sharing support
- `requests` (2.31.0+) - HTTP library for web scraping
- `beautifulsoup4` (4.12.0+) - HTML parsing library
- `lxml` (5.0.0+) - XML/HTML parser for BeautifulSoup

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/BALAJIBHARGAV6/EXTERNAL-MARKS-.git
cd EXTERNAL-MARKS-
```

### 2. Install Dependencies

```bash
pip install flask flask-cors requests beautifulsoup4 lxml
```

### 3. Start the Server

```bash
python scraper.py
```

**Expected Output:**
```
MIC Scraper v5.0 - NUCLEAR OPTION
Pure requests - 2-3 seconds!
Server: http://0.0.0.0:5001

Logging in...
Login successful!

 * Running on http://127.0.0.1:5001
```

### 4. Open the Web Interface

Open `index.html` in your browser, or visit:
```
file:///path/to/EXTERNAL-MARKS-/index.html
```

Alternatively, double-click `index.html` to open it.

### 5. Get Results

1. Enter a registration number (e.g., `22H71A1241`)
2. Click "Get Results" or press Enter
3. View complete results in **2-3 seconds**!

## 📡 API Usage

### Endpoint

```
GET http://127.0.0.1:5001/get_marks?reg=REGISTRATION_NUMBER
```

### Example Request

```bash
curl "http://127.0.0.1:5001/get_marks?reg=22H71A1241"
```

### Example Response

```json
{
    "status": "success",
    "reg_no": "22H71A1241",
    "execution_time": "0.27s",
    "method": "requests",
    "data": {
        "semester_summary": {
            "count": 7,
            "headers": ["Semester", "SGPA", "CGPA", "Total Credits", "Credits Secured", "BackLogs"],
            "rows": [
                {
                    "Semester": "VI",
                    "SGPA": "8.39",
                    "CGPA": "7.93",
                    "Total Credits": "25.50",
                    "Credits Secured": "25.50",
                    "BackLogs": "0"
                }
            ]
        },
        "marks_details": {
            "count": 72,
            "headers": ["Code", "Course Name", "CR", "GR", "GRPTS", "EXAMMY", "Result"],
            "rows": [
                {
                    "Code": "20IT6T01",
                    "Course Name": "Machine Learning",
                    "CR": "3.00",
                    "GR": "D",
                    "GRPTS": "6",
                    "EXAMMY": "May-2025",
                    "Result": "PASS"
                }
            ]
        }
    }
}
```

### Other Endpoints

- **Health Check**: `GET http://127.0.0.1:5001/health`
- **API Info**: `GET http://127.0.0.1:5001/`

## 🔧 Configuration

Edit `scraper.py` to customize:

```python
BASE_URL = 'https://exams.mictech.ac.in'
USERNAME = 'hodit'
PASSWORD = 'hodit@#@!'
```

## 📊 Performance Comparison

| Version | Method | Execution Time | Improvement |
|---------|--------|----------------|-------------|
| v1.0 | Playwright (per-request login) | ~25-30s | Baseline |
| v2.0 | Playwright optimized | ~14s | 50% faster |
| v3.0 | Playwright + browser reuse | ~14s | 50% faster |
| v4.0 | Playwright + persistent login | ~14s | 50% faster |
| **v5.0** | **Pure requests (NO browser)** | **~0.27s** | **98% faster** ⚡ |

## 🎨 Web Interface Features

- **Gradient Design**: Beautiful purple/blue gradient theme
- **CGPA Cards**: Quick view of CGPA, SGPA, Credits, Backlogs
- **Color-Coded Grades**: 
  - 🟢 Green: A+, A
  - 🔵 Blue: B+, B
  - 🟡 Yellow: C, D
  - 🔴 Red: E, F
- **Responsive Tables**: Horizontal scroll on mobile
- **Loading States**: Real-time status updates
- **Execution Timer**: Shows both frontend and backend timing

## 🛡️ Error Handling

The API handles common errors gracefully:

- Missing registration number
- Invalid registration number
- Network failures
- Server errors
- Session expiration

## 🔐 CORS Configuration

CORS is enabled for all origins. To restrict:

```python
from flask_cors import CORS
CORS(app, origins=['http://localhost:3000'])
```

## 📝 Notes

- The scraper uses the official MIC exam portal credentials
- Session is maintained across requests for speed
- Data is fetched in real-time (no caching)
- Works with ASP.NET ViewState mechanism
- BeautifulSoup handles HTML parsing efficiently

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📜 License

This project is for educational purposes only.

## ⚠️ Disclaimer

This tool is designed to fetch exam results from the official MIC exam portal. Use responsibly and in accordance with institutional policies.

## 👨‍💻 Author

**BALAJIBHARGAV6**

## 🌟 Changelog

### v5.0 (NUCLEAR) - Current
- Pure Python `requests` implementation
- 98% performance improvement (0.27s execution)
- Removed Playwright dependency
- BeautifulSoup HTML parsing
- Persistent session management

### v4.0 (MAXIMUM SPEED)
- Playwright with persistent login
- Browser context reuse
- Thread-safe implementation

### v3.0 (ULTRA OPTIMIZED)
- Browser reuse across requests
- BeautifulSoup integration

### v2.0 (OPTIMIZED)
- Resource blocking
- Reduced timeouts
- Fast wait strategies

### v1.0 (INITIAL)
- Basic Playwright implementation
- Flask API wrapper

---

⭐ **Star this repo if you found it helpful!**
