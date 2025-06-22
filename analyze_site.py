import requests
from bs4 import BeautifulSoup
import re

def analyze_new_site():
    """새로운 카라반파크 파트너센터 사이트 구조 분석"""
    
    # 1. 메인 페이지 확인
    print("=== 메인 페이지 분석 ===")
    try:
        response = requests.get("https://partner.caravanpark.kr/", allow_redirects=True)
        print(f"최종 URL: {response.url}")
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 로그인 폼 찾기
            login_form = soup.find('form')
            if login_form:
                print(f"로그인 폼 action: {login_form.get('action', 'N/A')}")
                print(f"로그인 폼 method: {login_form.get('method', 'N/A')}")
                
                # 입력 필드 찾기
                inputs = login_form.find_all('input')
                for inp in inputs:
                    print(f"입력 필드: name='{inp.get('name', 'N/A')}', type='{inp.get('type', 'N/A')}', id='{inp.get('id', 'N/A')}'")
            
            # 페이지 제목 확인
            title = soup.find('title')
            if title:
                print(f"페이지 제목: {title.text}")
                
            # 모든 링크 확인
            links = soup.find_all('a', href=True)
            print(f"\n발견된 링크들:")
            for link in links[:10]:  # 처음 10개만 출력
                print(f"  {link.get('href')} - {link.text.strip()}")
                
    except Exception as e:
        print(f"메인 페이지 분석 중 오류: {e}")
    
    print("\n" + "="*50)
    
    # 2. 로그인 페이지 직접 확인
    print("=== 로그인 페이지 분석 ===")
    try:
        response = requests.get("https://partner.caravanpark.kr/auth/signin")
        print(f"로그인 페이지 URL: {response.url}")
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 폼 찾기
            forms = soup.find_all('form')
            print(f"발견된 폼 개수: {len(forms)}")
            
            for i, form in enumerate(forms):
                print(f"\n폼 {i+1}:")
                print(f"  action: {form.get('action', 'N/A')}")
                print(f"  method: {form.get('method', 'N/A')}")
                print(f"  class: {form.get('class', 'N/A')}")
                
                inputs = form.find_all('input')
                for inp in inputs:
                    print(f"    입력: name='{inp.get('name', 'N/A')}', type='{inp.get('type', 'N/A')}', id='{inp.get('id', 'N/A')}'")
                    
    except Exception as e:
        print(f"로그인 페이지 분석 중 오류: {e}")

def test_login_and_navigate():
    """로그인 후 예약 관리 페이지 탐색"""
    print("\n" + "="*50)
    print("=== 로그인 테스트 및 페이지 탐색 ===")
    
    with requests.Session() as session:
        # 1. 로그인 시도
        login_data = {
            'masterId': 'elpark4',  # info.py에서 가져온 아이디
            'masterPass': '1234'    # info.py에서 가져온 비밀번호
        }
        
        try:
            # 로그인 페이지 접속
            response = session.get("https://partner.caravanpark.kr/auth/signin")
            print(f"로그인 페이지 접속: {response.status_code}")
            
            # 로그인 시도
            response = session.post("https://partner.caravanpark.kr/auth/signin", data=login_data)
            print(f"로그인 시도: {response.status_code}")
            print(f"로그인 후 URL: {response.url}")
            
            # 로그인 성공 여부 확인
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 로그인 성공 후 메인 페이지 확인
                if "로그인" not in response.text and "signin" not in response.url:
                    print("로그인 성공!")
                    
                    # 메인 페이지에서 예약 관련 링크 찾기
                    links = soup.find_all('a', href=True)
                    print("\n발견된 링크들:")
                    for link in links:
                        href = link.get('href')
                        text = link.text.strip()
                        if any(keyword in href.lower() or keyword in text.lower() 
                               for keyword in ['reservation', '예약', 'calendar', '달력', 'manage', '관리']):
                            print(f"  예약 관련 링크: {href} - {text}")
                    
                    # 대시보드나 메인 페이지에서 예약 정보 확인
                    tables = soup.find_all('table')
                    print(f"\n발견된 테이블 개수: {len(tables)}")
                    
                    for i, table in enumerate(tables[:3]):  # 처음 3개 테이블만 확인
                        print(f"\n테이블 {i+1}:")
                        print(f"  class: {table.get('class', 'N/A')}")
                        print(f"  id: {table.get('id', 'N/A')}")
                        
                        # 테이블 내용 일부 출력
                        rows = table.find_all('tr')
                        for j, row in enumerate(rows[:3]):  # 처음 3행만 출력
                            cells = row.find_all(['td', 'th'])
                            cell_texts = [cell.text.strip() for cell in cells]
                            print(f"    행 {j+1}: {cell_texts}")
                else:
                    print("로그인 실패 또는 로그인 페이지에 머물러 있음")
                    
        except Exception as e:
            print(f"로그인 테스트 중 오류: {e}")

if __name__ == "__main__":
    analyze_new_site()
    test_login_and_navigate() 