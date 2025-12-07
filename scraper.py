"""
MIC Exam Scraper - ULTRA OPTIMIZED (<10s target)
Stripped down for maximum speed
"""

from playwright.sync_api import sync_playwright
from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

BASE_URL = 'https://exams.mictech.ac.in'
LOGIN_URL = f'{BASE_URL}/Login.aspx'
HISTORY_URL = f'{BASE_URL}/StudentHistory.aspx'
USERNAME = 'hodit'
PASSWORD = 'hodit@#@!'

# Global browser context for reuse (MASSIVE speed improvement)
_browser = None
_context = None

def get_browser():
    """Get or create browser instance"""
    global _browser, _context
    
    if _browser is None or not _browser.is_connected():
        from playwright.sync_api import sync_playwright
        p = sync_playwright().start()
        
        _browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-extensions',
                '--disable-background-networking',
                '--disable-default-apps',
                '--disable-sync',
                '--no-first-run',
                '--no-zygote'
            ]
        )
        
        _context = _browser.new_context(
            viewport={'width': 1280, 'height': 720},
            java_script_enabled=True,
            bypass_csp=True,
            ignore_https_errors=True
        )
        
        # Block resources
        _context.route('**/*', lambda route: route.abort() if route.request.resource_type in 
                      ['image', 'stylesheet', 'font', 'media'] else route.continue_())
    
    return _context

def scrape_student_data(reg_no):
    """Scrape student data - ULTRA FAST"""
    
    start_time = time.time()
    
    try:
        context = get_browser()
        page = context.new_page()
        page.set_default_timeout(10000)
        
        # Login FAST
        page.goto(LOGIN_URL, wait_until='domcontentloaded', timeout=8000)
        page.fill('input[id*="txtUsername"]', USERNAME)
        page.fill('input[id*="txtPassword"]', PASSWORD)
        
        # Submit and wait for navigation
        page.click('input[id*="btnLogin"]')
        page.wait_for_url(lambda url: 'Login.aspx' not in url, timeout=8000)
        
        # Go to history
        page.goto(HISTORY_URL, wait_until='domcontentloaded', timeout=8000)
        
        # Search student
        page.fill('input[id*="txtRegNo"]', reg_no)
        page.press('input[id*="txtRegNo"]', 'Enter')
        
        # Wait for table only
        page.wait_for_selector('table', timeout=8000)
        page.wait_for_timeout(300)  # Minimal wait
        
        # Extract tables
        all_tables = page.locator('table').all()
        
        semester_summary = None
        marks_details = None
        
        for table in all_tables:
            if table.locator('tr').count() < 2:
                continue
            
            table_data = extract_table_fast(table)
            if not table_data:
                continue
            
            table_id = (table.get_attribute('id') or '').lower()
            headers = ' '.join(table_data['headers']).lower()
            
            # Identify tables
            if 'dgv' in table_id or 'history' in table_id:
                marks_details = table_data
            elif 'semester' in headers and ('sgpa' in headers or 'cgpa' in headers):
                semester_summary = table_data
            elif not marks_details and ('subject' in headers or 'marks' in headers):
                marks_details = table_data
            
            # Exit early
            if semester_summary and marks_details:
                break
        
        page.close()
        
        execution_time = round(time.time() - start_time, 2)
        
        if not marks_details and not semester_summary:
            return {
                'status': 'error',
                'error': 'No data found',
                'execution_time': f"{execution_time}s"
            }
        
        return {
            'status': 'success',
            'reg_no': reg_no,
            'execution_time': f"{execution_time}s",
            'data': {
                'semester_summary': semester_summary,
                'marks_details': marks_details
            }
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'execution_time': f"{round(time.time() - start_time, 2)}s"
        }

def extract_table_fast(table):
    """Fast table extraction"""
    try:
        rows = table.locator('tr').all()
        if len(rows) < 2:
            return None
        
        # Headers
        first_row = rows[0]
        has_th = first_row.locator('th').count() > 0
        
        if has_th:
            headers = [cell.inner_text().strip() or f"col_{i}" 
                      for i, cell in enumerate(first_row.locator('th').all())]
            start_row = 1
        else:
            headers = [cell.inner_text().strip() or f"col_{i}" 
                      for i, cell in enumerate(first_row.locator('td').all())]
            start_row = 0
        
        if not headers:
            return None
        
        # Data rows
        data_rows = []
        for i in range(start_row, len(rows)):
            cells = rows[i].locator('td, th').all()
            if not cells:
                continue
            
            row_data = {}
            has_content = False
            
            for j, cell in enumerate(cells):
                # Check input field first
                inp = cell.locator('input')
                if inp.count() > 0:
                    value = inp.first.get_attribute('value') or ''
                else:
                    value = cell.inner_text().strip()
                
                if value:
                    has_content = True
                
                key = headers[j] if j < len(headers) else f"column_{j}"
                row_data[key] = value
            
            if has_content:
                data_rows.append(row_data)
        
        return {
            'headers': headers,
            'rows': data_rows,
            'count': len(data_rows)
        } if data_rows else None
        
    except:
        return None

@app.route('/get_marks', methods=['GET'])
def get_marks():
    """API endpoint"""
    reg_no = request.args.get('reg', '').strip().upper()
    
    if not reg_no:
        return jsonify({'status': 'error', 'error': 'Registration number required'}), 400
    
    result = scrape_student_data(reg_no)
    return jsonify(result)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/')
def home():
    return jsonify({
        'api': 'MIC Exam Scraper v3.0',
        'optimizations': ['Browser reuse', 'Minimal waits', 'Fast extraction'],
        'usage': '/get_marks?reg=22H71A1241'
    })

if __name__ == '__main__':
    print("\nMIC Exam Scraper v3.0 - Running on http://0.0.0.0:5001")
    print("Target: <10s | Browser reuse enabled\n")
    app.run(host='0.0.0.0', port=5001, debug=False)