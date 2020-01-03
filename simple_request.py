#-*- coding:utf-8 -*-

import requests

# 실행중인 Flask endpoint url 및 POST 전송할 이미지 PATH
KERAS_REST_API_URL = "http://localhost:5000/predict"
IMAGE_PATH = "dog.jpg"
# 전송할 이미지 로드 및 POST 전송 payload 설정
image = open(IMAGE_PATH, "rb").read()
payload = {"image": image}

# POST 요청 실행
r = requests.post(KERAS_REST_API_URL, files=payload).json()

# 요청이 성공적으로 실행됬는지
if r["success"]:
    # 예측 결과 출력
    for (i, result) in enumerate(r["predictions"]):
        print("{}. {}: {:.4f}".format(i + 1, result["label"],
                                      result["probability"]))
# 아니라면 실패
else:
    print("Request failed")