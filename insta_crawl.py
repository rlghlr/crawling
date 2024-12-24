import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

# 인스타그램 로그인 없이 크롤링을 위한 기본 설정
hashtags = ["쇼핑", "할인"]  # 사용할 해시태그 목록
followers_threshold = 100000  # 팔로워 수 필터
unique_accounts = set()  # 중복 계정 필터링
results = []  # 결과 저장

# 헤더 설정 (인스타그램 요청을 일반 브라우저로 보이게 하여 차단을 우회하기 위함)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 크롤링 시작
for tag in hashtags:
    print(f"검색 중: #{tag}")
    url = f"https://www.instagram.com/explore/tags/{tag}/"
    
    try:
        # 웹 페이지 요청
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # JSON 데이터를 가져오기 위해 스크립트에서 데이터 추출
            shared_data = soup.find("script", {"type": "text/javascript"})
            if shared_data:
                json_data = shared_data.string.split("window._sharedData = ")[1].split(";</script>")[0]
                
                # JSON 파싱
                import json
                data = json.loads(json_data)
                
                # 게시물 추출
                for post in data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']:
                    username = post['node']['owner']['username']
                    followers = post['node']['owner']['edge_owner_to_timeline_media']['count']
                    
                    # 중복 계정과 팔로워 수 필터링
                    if username not in unique_accounts and followers >= followers_threshold:
                        results.append({
                            "username": username,
                            "followers": followers,
                            "url": f"https://www.instagram.com/{username}/"
                        })
                        unique_accounts.add(username)
                        print(f"추가됨: {username} - {followers}")
                    
                    # 100개 이상 수집 시 종료
                    if len(results) >= 100:
                        break
                if len(results) >= 100:
                    break
            time.sleep(3)  # 대기 시간 추가
    except Exception as e:
        print(f"오류 발생: {e}")
        continue

# 결과 저장
df = pd.DataFrame(results)
df.to_csv('insta_results.csv', index=False)
print("크롤링 완료! 결과가 insta_results.csv 파일에 저장되었습니다.")

