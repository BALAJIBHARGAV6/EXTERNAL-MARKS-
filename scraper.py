"""
MIC Exam Scraper - FINAL FAST VERSION
Gets both semester table and marks table
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

def scrape_student_data(reg_no):
    """Scrape all student data - FAST version"""
    
    start_time = time.time()
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            page = context.new_page()
            page.set_default_timeout(15000)
            
            # Login - FAST
            page.goto(LOGIN_URL, wait_until='domcontentloaded')
            page.fill('input[id*="txtUsername"]', USERNAME)
            page.fill('input[id*="txtPassword"]', PASSWORD)
            page.click('input[id*="btnLogin"]')
            page.wait_for_load_state('domcontentloaded')
            
            if 'Login.aspx' in page.url:
                browser.close()
                return {'status': 'error', 'error': 'Login failed'}
            
            # Go to history page - FAST
            page.goto(HISTORY_URL, wait_until='domcontentloaded')
            
            # Search for student - FAST
            page.fill('input[id*="txtRegNo"]', reg_no)
            page.press('input[id*="txtRegNo"]', 'Enter')
            page.wait_for_load_state('domcontentloaded')
            
            # Small wait for tables to render
            page.wait_for_timeout(500)
            
            # Save screenshot for debugging
            page.screenshot(path=f'debug_{reg_no}.png')
            
            # Get all tables on the page
            all_tables = page.locator('table').all()
            
            print(f"Found {len(all_tables)} tables on page")
            
            semester_summary = None
            marks_details = None
            
            # Extract data from all tables
            for idx, table in enumerate(all_tables):
                table_id = table.get_attribute('id') or f'table_{idx}'
                print(f"Processing table {idx}: id={table_id}")
                
                # Try to extract data from this table
                table_data = extract_table_data(table)
                
                if table_data:
                    print(f"  -> Table {idx} has {table_data['count']} rows")
                    print(f"  -> Headers: {table_data['headers'][:3]}...")
                else:
                    print(f"  -> Table {idx} has no data")
                    continue
                
                # Check if this is the marks history table (usually has ID)
                if 'dgv' in table_id.lower() or 'history' in table_id.lower():
                    marks_details = table_data
                
                # Check if this is the semester summary table
                # It usually has columns like Semester, SGPA, CGPA
                elif table_data and table_data.get('headers'):
                    headers_lower = ' '.join(table_data['headers']).lower()
                    if 'semester' in headers_lower or 'sgpa' in headers_lower or 'cgpa' in headers_lower:
                        semester_summary = table_data
                    # If we haven't found marks details yet, this might be it
                    elif not marks_details and len(table_data['rows']) > 5:
                        marks_details = table_data
            
            browser.close()
            
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
            try:
                browser.close()
            except:
                pass
            
            return {
                'status': 'error',
                'error': str(e),
                'execution_time': f"{round(time.time() - start_time, 2)}s"
            }

def extract_table_data(table):
    """Extract data from a table element"""
    try:
        rows = table.locator('tr').all()
        
        if len(rows) == 0:
            return None
        
        # Extract headers - try both th and td in first row
        headers = []
        first_row_cells = rows[0].locator('th, td').all()
        
        for cell in first_row_cells:
            text = cell.inner_text().strip()
            headers.append(text if text else f"col_{len(headers)}")
        
        if not headers:
            return None
        
        # Determine if first row is header or data
        first_row_is_header = rows[0].locator('th').count() > 0
        start_row = 1 if first_row_is_header else 0
        
        # Extract data rows
        data_rows = []
        for i in range(start_row, len(rows)):
            cells = rows[i].locator('td, th').all()
            if len(cells) == 0:
                continue
            
            row_data = {}
            for j, cell in enumerate(cells):
                # Check for input field
                inp = cell.locator('input')
                if inp.count() > 0:
                    value = inp.first.get_attribute('value') or ''
                else:
                    value = cell.inner_text().strip()
                
                # Use header as key
                key = headers[j] if j < len(headers) else f"column_{j}"
                row_data[key] = value
            
            # Only add if row has some non-empty values
            if row_data and any(v for v in row_data.values() if v):
                data_rows.append(row_data)
        
        if not data_rows:
            return None
        
        return {
            'headers': headers,
            'rows': data_rows,
            'count': len(data_rows)
        }
        
    except Exception as e:
        return None

@app.route('/get_marks', methods=['GET'])
def get_marks():
    """API endpoint - get all student data"""
    reg_no = request.args.get('reg', '').strip().upper()
    
    if not reg_no:
        return jsonify({'status': 'error', 'error': 'Registration number required'}), 400
    
    print(f"Request: {reg_no}")
    result = scrape_student_data(reg_no)
    print(f"Result: {result['status'].upper()} - {result.get('execution_time', 'N/A')}")
    
    return jsonify(result)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/')
def home():
    return jsonify({
        'api': 'MIC Exam Scraper',
        'version': '2.0',
        'features': ['Semester Summary', 'Marks Details'],
        'example': 'curl "http://localhost:5001/get_marks?reg=22H71A1241"'
    })

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("MIC EXAM SCRAPER API v2.0")
    print("=" * 70)
    print("\nFAST MODE - Gets both tables")
    print("Semester Summary + Marks Details")
    print("Server: http://0.0.0.0:5001")
    print("\nTest:")
    print("   curl 'http://localhost:5001/get_marks?reg=22H71A1241'")
    print("\n" + "=" * 70 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=False)