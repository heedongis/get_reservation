# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import requests
from bs4 import BeautifulSoup
import re
import datetime
import pandas as pd
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
import info

def get_reservation():

    # today = datetime.datetime.today().strftime("%Y-%m-%d")
    today='2024-01-29'
    user_id = info.user_id
    user_password = info.user_password

    root_url = info.root_url
    login_url = root_url + info.login_url
    calendar_url = info.calendar_url
    today_reserve_url = root_url + info.today_reserve_url+today
    today_room_detail_url = root_url + info.today_room_detail_url

    form_data = {
        'pid': user_id,
        'ppw': user_password,
        'm_chk': 'N'  # 이 값은 폼에 있는 체크박스의 기본값입니다.
    }

    with requests.Session() as session:
        # POST 요청으로 로그인을 시도합니다.
        response = session.post(login_url, data=form_data)

        # 전체 달력 가져오기
        response = session.get(calendar_url)
        # 오늘 날짜 예약 가져오기
        response = session.get(today_reserve_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # reservation_rows = soup.find_all('tr', class_='has-background-success-light')
        reservation_table = soup.find('table',
                                      class_='table table-p-rsv-list is-size-7 is-fullwidth is-hoverable has-text-centered')
        reservation_tbody = reservation_table.find('tbody') if reservation_table else None
        if reservation_tbody:
            reservation_rows = reservation_tbody.find_all('tr')
        # calendar_div = soup.find('div', class_='cal-td-title')
        reservations = []

        # 각 행에 대해 반복
        for row in reservation_rows:
            cells = row.find_all('td')

            if len(cells) < 10:
                continue
            detail_info = {
                'type': '',
                'room_type':'',
                'name':'',
                'phone':'',
                'total_count':'',
                'bbq' :'',
                'campFire' :'',
                'etc':''
            }
            # 예약자 정보와 객실명 추출

            if cells[9].get_text(strip=True) =='예약완료' or cells[9].get_text(strip=True) =='입금대기':
                reservation_number = cells[0].get_text(strip=True)
                response = session.get(today_room_detail_url + reservation_number)
                soup = BeautifulSoup(response.text, 'html.parser')

                client_detail_table = soup.find('table', class_='table table-p-rsv-detail is-size-6 is-bordered is-fullwidth')
                reservation_detail_table = soup.find('table', id='tbody-rsv-plain')
                option_detail_tables = soup.find_all('table', class_='table table-p-rsv-detail is-size-7 is-bordered is-fullwidth has-text-centered')

                # "옵션상품 이용"이 포함된 테이블만을 저장할 리스트
                option_detail_table = []

                # 각 테이블에 대해 반복
                for html_table in option_detail_tables:
                    # 테이블에서 "옵션상품 이용" 텍스트를 포함하는 th 태그 찾기
                    if html_table.find('th', string="옵션상품 이용"):
                        option_detail_table.append(html_table)

                # client_detail_table를 이용한 이름, 전화번호 가져오기
                name_input = client_detail_table.find('input', {'name': 'name'})
                phone_input = client_detail_table.find('input', {'name': 'hphone'})

                name = name_input['value'] if name_input else '이름 정보 없음'
                phone = phone_input['value'] if phone_input else '전화번호 정보 없음'
                detail_info['name'] = name
                detail_info['phone'] = phone
            if cells[9].get_text(strip=True) =='입금대기':
                detail_info['etc'] = '예약대기'


            # revervation_detail_table를 이용한 예약인원, 바베큐, 캠프파이어 정보 가져오기

            tbody = reservation_detail_table.find('tbody')
            print(tbody)
            if tbody:
                # 첫 번째 행 찾기
                row = tbody.find('tr')

                # 각각의 수를 추출하기 위한 td 태그 찾기
                room_type = row.find_all('td')[1].get_text(strip=True).split('\n')[0].split('(')[0] # 룸타입
                if '카라반' in room_type:
                    detail_info['type']='caravan'
                else:
                    detail_info['type']='pension'

                adult = row.find_all('td')[3].get_text(strip=True)   # "성인" 수
                child = row.find_all('td')[4].get_text(strip=True)   # "아동" 수
                infant = row.find_all('td')[5].get_text(strip=True)  # "유아" 수
                detail_info['room_type']=room_type
                detail_info['total_count'] = '성인 : '+str(adult)+ ', 아동 : '+str(child) + ', 유아 : '+str(infant) +'\n (추가인원) 성인:   명, 유아:   명'


            else:
                print("테이블 내용이 없습니다.")


            if len(option_detail_table) != 0:
                #테이블 내의 모든 텍스트 가져오기
                table_text = option_detail_table[0].get_text()

                # "바베큐"와 "불멍" 단어 존재 여부 확인
                bbq_exists = '결제 완료' if '바베큐' in table_text else ''
                firepit_exists = '결제 완료' if '불멍' in table_text else ''

                detail_info['bbq'] = bbq_exists
                detail_info['campFire'] = firepit_exists
            # break

            reservations.append(detail_info)
    return reservations, today




def make_daily_paper():
    column_mapping = {
        'type': '종류',
        'room_type':'객실명',
        'name':'예약자',
        'phone':'전화번호',
        'total_count':'인원수',
        'bbq' :'바베큐',
        'campFire' :'불멍',
        'etc':'특이사항'
    }

    room_list = {
        'caravan': ['럭셔리스파카라반1', '럭셔리vip스파카라반2', '럭셔리스파카라반3', '럭셔리vip스파카라반4', '럭셔리스파카라반5', '럭셔리카라반1', '럭셔리vip카라반2', '럭셔리카라반3', '럭셔리vip카라반4', '스카이vip카라반','vip커플카라반'],
        'pension': ['그린1', '그린2', '그린3', '펜션-커플룸', '강뷰-화이트1','강뷰-오렌지', '강뷰-옐로우1', '강뷰-옐로우2','강뷰-레드','강뷰-화이트2']
    }

    custom_order = room_list['caravan'] + room_list['pension']

    reservations, today = get_reservation()
    print('res : ',reservations)
    save_path = 'C:/Users/heedo/Desktop/입실일지/'+today[:-3]+'/'



    if len(reservations) ==0:
        print('금일 예약이 없습니다.')
        with open(save_path+today+'_null.txt', 'w'):
            pass
    else:
        try:
            # room_list에 있는 각 객실이 reservations에 있는지 확인하고, 없으면 추가
            for reservation_type, rooms in room_list.items():
                for room in rooms:
                    if not any(reservation['room_type'] == room for reservation in reservations if
                               reservation['type'] == reservation_type):
                        # 새로운 예약 항목 추가
                        new_reservation = {
                            'type': reservation_type,
                            'room_type': room,
                            'name': '',
                            'phone': '',
                            'total_count': '',
                            'bbq': '',
                            'campFire': '',
                            'etc':''
                        }
                        reservations.append(new_reservation)
            df = pd.DataFrame(reservations)
            df.rename(columns=column_mapping, inplace=True)
            df['객실명'] = pd.Categorical(df['객실명'], categories=custom_order, ordered=True)
            df = df.sort_values(by=['종류','객실명'])

            df.drop('종류', axis=1, inplace=True)

            # openpyxl을 사용하여 Excel 파일 생성
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = 'reservation'

            # 대 제목 추가
            a1_cell = ws['A1']
            a1_cell.value = today + ' 예약현황'
            a1_cell.font = Font(size=24)

            # 테두리 설정
            thin_border = Border(left=Side(style='thin'),
                                 right=Side(style='thin'),
                                 top=Side(style='thin'),
                                 bottom=Side(style='thin'))

            # 열 제목 설정
            header_font = Font(bold=True, size=12)

            for col_num, title in enumerate([col for col in df.columns if col != '종류'], start=1):
                cell = ws.cell(row=3, column=col_num, value=title)
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center')
                cell.border = thin_border

            # 데이터 삽입
            for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=False), start=4):
                ws.append(row)
                cell = ws.cell(row=r_idx, column=5)
                cell.alignment = Alignment(wrap_text=True)

            ws['H3'] = '입실완료'
            ws['H3'].font = header_font
            ws['H3'].alignment = Alignment(horizontal='center')
            ws['H3'].border = thin_border

            ws['I3'] = '결제금액'
            ws['I3'].font = header_font
            ws['I3'].alignment = Alignment(horizontal='center')
            ws['I3'].border = thin_border

            ws['J3'] = '수수료'
            ws['J3'].font = header_font
            ws['J3'].alignment = Alignment(horizontal='center')
            ws['J3'].border = thin_border

            ws['K3'] = '정산금액'
            ws['K3'].font = header_font
            ws['K3'].alignment = Alignment(horizontal='center')
            ws['K3'].border = thin_border

            ws.column_dimensions['A'].width = 21
            ws.column_dimensions['C'].width = 15
            ws.column_dimensions['D'].width = 30
            ws.column_dimensions['E'].width = 9
            ws.column_dimensions['F'].width = 10
            ws.column_dimensions['H'].width = 10
            ws.column_dimensions['I'].width = 10


            for row in ws.iter_rows(min_row=3, min_col=1, max_row=ws.max_row, max_col=ws.max_column):
                for cell in row:
                    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
                    cell.border = thin_border

            # 파일 저장
            wb.save(save_path+today+'.xlsx')
        except Exception as err:
            print(err)
            print('저장에 실패 했습니다.')
# def today_reservation(room_type, client_name, phone_number):

if __name__ == '__main__':
    make_daily_paper()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
