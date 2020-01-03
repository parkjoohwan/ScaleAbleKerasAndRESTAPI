#-*- coding:utf-8 -*-

# 필요 패키지 import
# 사이트에서는 keras를 이용했는데, tensorflow 2.0 에 keras가 포함되어있어서 tensorflow 2.0 를 사용하기로함
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications import imagenet_utils
from threading import Thread
from PIL import Image
import numpy as np
import base64
import flask
import redis
import uuid
import time
import json
import sys
import io

# 이미지 size, demension, datatype 설정
# data type
IMAGE_WIDTH = 224
IMAGE_HEIGHT = 224
IMAGE_CHANS = 3
IMAGE_DTYPE = "float32"

# 서버 queue/delay 설정
IMAGE_QUEUE = "image_queue"
BATCH_SIZE = 32
SERVER_SLEEP = 0.25
CLIENT_SLEEP = 0.25

# 사용할 Flask application, Redis server, and Keras model 초기화
app = flask.Flask(__name__)
db = redis.StrictRedis(host="localhost", port=6379, db=0)	# port는 redis 실행시 기본으로 설정된 포트
model = None

# NumPy 배열에 넣기위해 base64 인코딩
def base64_encode_image(image):
	return base64.b64encode(image).decode("utf-8")


def base64_decode_image(image, dtype, shape):
	# python3 인 경우, serialize 된 NumPy string을 byte object로 인코딩 해줘야함
	if sys.version_info.major == 3:
		image = bytes(image, encoding="utf-8")

	# 해당하는 data type과 대상 shape로 문자열을 NumPy 배열로 변환
	image = np.frombuffer(base64.decodestring(image), dtype=dtype)
	image = image.reshape(shape)
	return image

# 이미지 전처리
def prepare_image(image, target):
	# 만약 이미지가 RGB 형태가 아니라면 RGB 형태로 convert
	if image.mode != "RGB":
		image = image.convert("RGB")

	# 인풋 이미지 resize + 전처리
	image = image.resize(target)
	image = img_to_array(image)
	image = np.expand_dims(image, axis=0)
	image = imagenet_utils.preprocess_input(image)
	return image

def classify_process():
	# pre-trained 케라스 모델 load
	print("* Loading model...")
	model = ResNet50(weights="imagenet")
	print("* Model loaded")
	# 예측을 위해 전송되는 새로운 이미지를 계속 polling
	while True:
		# attempt to grab a batch of images from the database, then
		# initialize the image IDs and batch of images themselves
		# Redis에서 이미지 배치를 가져오고 다음 이미지 ID 및 배치 초기화
		queue = db.lrange(IMAGE_QUEUE, 0, BATCH_SIZE - 1)
		imageIDs = []
		batch = None

		# queue에 쌓인 것들 처리
		for q in queue:
			# 이미지 decodeing
			q = json.loads(q.decode("utf-8"))
			image = base64_decode_image(q["image"], IMAGE_DTYPE,
										(1, IMAGE_HEIGHT, IMAGE_WIDTH, IMAGE_CHANS))

			# batch 가 None인지 확인
			if batch is None:
				batch = image

			# None이 아니면 stack에 쌓음
			else:
				batch = np.vstack([batch, image])

			# 이미지 ID list 갱신
			imageIDs.append(q["id"])
			# 처리할게 있는지 확인
			if len(imageIDs) > 0:
				# 배치 분류
				print("* Batch size: {}".format(batch.shape))
				preds = model.predict(batch)
				results = imagenet_utils.decode_predictions(preds)

				# 이미지 ID 및 resultSet 반복
				for (imageID, resultSet) in zip(imageIDs, results):
					# 예측 결과리스트
					output = []

					# 예측 결과리스트에 추가
					for (imagenetID, label, prob) in resultSet:
						r = {"label": label, "probability": float(prob)}
						output.append(r)

					# 예측 결과리스트를 Redis db에 Image ID를 키로 저장함
					db.set(imageID, json.dumps(output))

				# 진행한 이미지는 queue에서 제거
				db.ltrim(IMAGE_QUEUE, len(imageIDs), -1)

			# delay
			time.sleep(SERVER_SLEEP)

# 전송된 이미지를 처리하는 flask end point
@app.route("/predict", methods=["POST"])
def predict():
	# 반환될 data 초기화
	data = {"success": False}

	# 형식에 맞게 요청받았는지 확인
	if flask.request.method == "POST":
		if flask.request.files.get("image"):
			# 받은 이미지 전처리
			image = flask.request.files["image"].read()
			image = Image.open(io.BytesIO(image))
			image = prepare_image(image, (IMAGE_WIDTH, IMAGE_HEIGHT))

			# NumPy 배열이 C-contiguous 하도록 serialize
			image = image.copy(order="C")

			# 분류를 위한 ID를 생성하고 이미지와 함께 queue에 push
			k = str(uuid.uuid4())
			d = {"id": k, "image": base64_encode_image(image)}
			db.rpush(IMAGE_QUEUE, json.dumps(d))
			# model server가 예측 결과를 return 할때까지 반복
			while True:
				# Redis db에 예측 결과가 저장됬는지 확인하기위해 get 시도
				output = db.get(k)

				# 예측 결과가 None이 아니면 완료된것
				if output is not None:
					# 반환할 data에 추가 예측 결과 추가
					output = output.decode("utf-8")
					data["predictions"] = json.loads(output)

					# 결과를 받았으므로 Redis db에서 제거 후 loop 탈출
					db.delete(k)
					break

				# delay
				time.sleep(CLIENT_SLEEP)

			# 결과를 성공적으로 받았으므로 data success 를 True로
			data["success"] = True

		# data 반환
		return flask.jsonify(data)

if __name__ == "__main__":
	# 입력 이미지를 분류하는 데 사용되는 함수를 별도의 스레드에서 실행
	print("* Starting model service...")
	t = Thread(target=classify_process, args=())
	t.daemon = True
	t.start()

	# flask 웹서버 실행
	print("* Starting web service...")
	app.run()