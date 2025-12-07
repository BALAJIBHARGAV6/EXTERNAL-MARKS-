"""
MIC Scraper - NUCLEAR OPTION
Uses pure requests (no browser) - 2-3 seconds!
Only works if website doesn't use heavy JavaScript
"""

import requests
from bs4 import BeautifulSoup
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

# Persistent session
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

def login_session():
    """Login and maintain session"""
    try:
        # Get login page
        resp = session.get(LOGIN_URL, timeout=5)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Get ASP.NET fields
        viewstate = soup.find('input', {'name': '__VIEWSTATE'})
        viewstate_gen = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
        event_validation = soup.find('input', {'name': '__EVENTVALIDATION'})
        
        # Prepare login data
        login_data = {
            '__VIEWSTATE': viewstate['value'] if viewstate else '',
            '__VIEWSTATEGENERATOR': viewstate_gen['value'] if viewstate_gen else '',
            '__EVENTVALIDATION': event_validation['value'] if event_validation else '',
        }
        
        # Find actual field names
        username_field = soup.find('input', {'type': 'text', 'id': lambda x: x and 'username' in x.lower()})
        password_field = soup.find('input', {'type': 'password', 'id': lambda x: x and 'password' in x.lower()})
        submit_button = soup.find('input', {'type': 'submit'})
        
        if username_field:
            login_data[username_field['name']] = USERNAME
        if password_field:
            login_data[password_field['name']] = PASSWORD
        if submit_button:
            login_data[submit_button['name']] = submit_button.get('value', 'Login')
        
        # Submit login
        resp = session.post(LOGIN_URL, data=login_data, timeout=5)
        
        return 'Login.aspx' not in resp.url
        
    except Exception as e:
        print(f"Login error: {e}")
        return False

def scrape_with_requests(reg_no):
    """Try pure requests first (fastest)"""
    start_time = time.time()
    
    try:
        # Get history page
        resp = session.get(HISTORY_URL, timeout=5)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Get form fields
        viewstate = soup.find('input', {'name': '__VIEWSTATE'})
        viewstate_gen = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
        event_validation = soup.find('input', {'name': '__EVENTVALIDATION'})
        
        # Prepare search data
        search_data = {
            '__VIEWSTATE': viewstate['value'] if viewstate else '',
            '__VIEWSTATEGENERATOR': viewstate_gen['value'] if viewstate_gen else '',
            '__EVENTVALIDATION': event_validation['value'] if event_validation else '',
        }
        
        # Find reg no field and search button
        reg_field = soup.find('input', {'type': 'text', 'id': lambda x: x and 'regno' in x.lower()})
        search_btn = soup.find('input', {'type': 'submit', 'id': lambda x: x and 'search' in x.lower() if x else False})
        
        if not search_btn:
            search_btn = soup.find('input', {'type': 'button', 'value': lambda x: x and 'search' in x.lower() if x else False})
        
        if reg_field:
            search_data[reg_field['name']] = reg_no
        if search_btn:
            search_data[search_btn['name']] = search_btn.get('value', 'Search')
        
        # Submit search
        resp = session.post(HISTORY_URL, data=search_data, timeout=5)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Parse tables
        tables = soup.find_all('table')
        
        semester_summary = None
        marks_details = None
        
        for table in tables:
            table_data = parse_table_html(table)
            if not table_data:
                continue
            
            table_id = (table.get('id', '')).lower()
            headers = ' '.join(table_data['headers']).lower()
            
            if 'dgv' in table_id or 'history' in table_id:
                marks_details = table_data
            elif 'semester' in headers and ('sgpa' in headers or 'cgpa' in headers):
                semester_summary = table_data
            elif not marks_details and ('subject' in headers or 'marks' in headers):
                marks_details = table_data
            
            if semester_summary and marks_details:
                break
        
        execution_time = round(time.time() - start_time, 2)
        
        if not marks_details and not semester_summary:
            return None  # Fall back to Playwright
        
        return {
            'status': 'success',
            'reg_no': reg_no,
            'execution_time': f"{execution_time}s",
            'method': 'requests',
            'data': {
                'semester_summary': semester_summary,
                'marks_details': marks_details
            }
        }
        
    except Exception as e:
        return None  # Fall back to Playwright

def parse_table_html(soup):
    """Parse table from BeautifulSoup (faster than Playwright)"""
    try:
        rows = soup.find_all('tr')
        if len(rows) < 2:
            return None
        
        # Get headers
        first_row = rows[0]
        header_cells = first_row.find_all('th')
        
        if header_cells:
            headers = [cell.get_text(strip=True) or f"col_{i}" for i, cell in enumerate(header_cells)]
            start_row = 1
        else:
            header_cells = first_row.find_all('td')
            headers = [cell.get_text(strip=True) or f"col_{i}" for i, cell in enumerate(header_cells)]
            start_row = 0
        
        if not headers:
            return None
        
        # Get data
        data_rows = []
        for row in rows[start_row:]:
            cells = row.find_all(['td', 'th'])
            if not cells:
                continue
            
            row_data = {}
            has_content = False
            
            for j, cell in enumerate(cells):
                # Check for input
                inp = cell.find('input')
                if inp and inp.get('value'):
                    value = inp['value']
                else:
                    value = cell.get_text(strip=True)
                
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
    """API endpoint - tries requests first, falls back to Playwright"""
    reg_no = request.args.get('reg', '').strip().upper()
    
    if not reg_no:
        return jsonify({'status': 'error', 'error': 'Registration number required'}), 400
    
    # Try pure requests first (2-3 seconds!)
    result = scrape_with_requests(reg_no)
    
    if result:
        return jsonify(result)
    
    # Fallback: Use Playwright (slower but reliable)
    # Import here to avoid startup overhead
    from playwright.sync_api import sync_playwright
    
    # Add your Playwright fallback code here
    return jsonify({
        'status': 'error',
        'error': 'Requests failed, implement Playwright fallback',
        'suggestion': 'Website likely requires JavaScript'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'method': 'requests'})

@app.route('/')
def home():
    return jsonify({
        'api': 'MIC Scraper v5.0 - NUCLEAR',
        'speed': '2-3 seconds (if website allows)',
        'method': 'Pure requests (no browser)'
    })

if __name__ == '__main__':
    print("\nMIC Scraper v5.0 - NUCLEAR OPTION")
    print("Pure requests - 2-3 seconds!")
    print("Server: http://0.0.0.0:5001\n")
    
    print("Logging in...")
    if login_session():
        print("Login successful!\n")
    else:
        print("Login may have failed - trying anyway\n")
    
    app.run(host='0.0.0.0', port=5001, debug=False)