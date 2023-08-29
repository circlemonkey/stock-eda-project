import requests as req
import pandas as pd
import re
import datetime
import time
from bs4 import BeautifulSoup
from marcap import marcap_data
from tqdm import tqdm

class dataCollectionCls:
    def discussionData(self, codes):
        headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}

        title_code = ''
        pages = range(1, 10000) # 페이지 가져오기
        codes = codes[0:2] # 종목 50개만 추출(네이버 크롤링 보안정책상)
        df = pd.DataFrame(columns=range(4))  # 빈 데이터프레임 생성
        df.columns = ['code', 'date', 'title', 'contents']  # 데이터 프레임 컬럼 지정
        end_date = datetime.datetime.strptime('2023-07-31', '%Y-%m-%d')
        for code in tqdm(codes):
            title_code = code
            for page in pages:
                urls = f'https://finance.naver.com/item/board.naver?code={str(code)}&page={str(page)}'
                res = req.get(urls, headers=headers)
                soup = BeautifulSoup(res.text, 'html.parser')

                aa = soup.select("tr[onmouseover='mouseOver(this)'] td:nth-child(1) span")
                bb = soup.find_all(href=re.compile("/item/board_read.naver"))

                for a, b in zip(aa, bb):
                    dt = datetime.datetime.strptime(a.contents[0].split(' ')[0].replace('.','-'), '%Y-%m-%d')
                    link = b['href']
                    title = b['title']

                    # 본문의 내용 가져오기
                    res2 = req.get('https://finance.naver.com' + link, headers=headers)
                    soup2 = BeautifulSoup(res2.text, 'html.parser')

                    # 데이터프레임에 행 추가
                    df.loc[len(df)] = [code, dt, title, soup2.find(id="body").find_all(text=True)]

                    # 종료일 페이지를 크롤링하면 다음 페이지로 이동
                    if end_date >= dt:
                        break
                    # 네이버 크롤링 정책 상 0.5초 sleep (제목 넘어갈 때)
                    time.sleep(0.5)
                # 종료일 페이지를 크롤링하면 다음 종목으로 이동
                if end_date >= dt:
                    break
                # 네이버 크롤링 정책 상 1초 sleep (페이지 넘어갈 때)
                time.sleep(1)
            # 네이버 크롤링 정책 상 10초 sleep (종목코드 넘어갈 때)
            time.sleep(10)

        # csv 파일로 저장
        df.to_csv("output_pd"+str(title_code)+".csv")

    def stockData(self, stday):
        today = datetime.datetime.today().strftime('%Y-%m-%d')

        # 특정 기간 전종목 가져오기 (시간 형식 : %Y-%m-%d)
        df = marcap_data(stday, today)  # 2015.06.15부터 상하한가폭 변경

    def codeData(self): # 종목 코드 모두 추출
        today = datetime.datetime.today()
        dayago = today - datetime.timedelta(days=7)
        df = marcap_data(dayago.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
        df = df.loc[df["Market"] != 'KONEX'] # KONEX 제거
        df = df.loc[df["Market"] != 'KOSPI']  # KOSPI 제거

        arr_code = df.Code.unique() # <class 'numpy.ndarray'>
        print(arr_code)
        return arr_code

start = dataCollectionCls()
start.codeData()