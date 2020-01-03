# 포스트 따라하기

- [참고 사이트](https://www.pyimagesearch.com/2018/01/29/scalable-keras-deep-learning-rest-api/)
- Redis 다운로드(Mac)은 참고사이트 그대로 따라하면 됨

# PC 환경
- Windows 10 + WSL(ubuntu 18.04.2 LTS)
- Tensorflow 2.0
- GPU RTX 2060 Super
- CUDA 10.0 / cudnn 7.6.5
- python 3.7.5 가상환경

# python packages
- 레포지토리 내 requirements.txt 참고
```
pip install -r requirements.txt 
```


# Windows 환경에서 Redis 설치 및 실행 따라하기

- Linux용 Windows 하위 시스템(WLS) 설치 후, Linux Shell에서 진행

- Window에서 wget 명령어는 레포지토리에 있는 wget.exe 파일을 통해 실행가능 혹은 WSL Linux Shell 에서 진행 가능

- redis 설치
```
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
sudo apt install make
sudo apt-get update
sudo apt install gcc
sudo make install
```

redis-server 실행
```
$redis-server
8648:C 02 Jan 2020 16:39:01.772 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
8648:C 02 Jan 2020 16:39:01.772 # Redis version=5.0.7, bits=64, commit=33b6047f, modified=1, pid=8648, just started
8648:C 02 Jan 2020 16:39:01.774 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
8648:M 02 Jan 2020 16:39:01.776 * Increased maximum number of open files to 10032 (it was originally set to 1024).
                _._
           _.-``__ ''-._
      _.-``    `.  `_.  ''-._           Redis 5.0.7 (33b6047f/1) 64 bit
  .-`` .-```.  ```\/    _.,_ ''-._
 (    '      ,       .-`  | `,    )     Running in standalone mode
 |`-._`-...-` __...-.``-._|'` _.-'|     Port: 6379
 |    `-._   `._    /     _.-'    |     PID: 8648
  `-._    `-._  `-./  _.-'    _.-'
 |`-._`-._    `-.__.-'    _.-'_.-'|
 |    `-._`-._        _.-'_.-'    |           http://redis.io
  `-._    `-._`-.__.-'_.-'    _.-'
 |`-._`-._    `-.__.-'    _.-'_.-'|
 |    `-._`-._        _.-'_.-'    |
  `-._    `-._`-.__.-'_.-'    _.-'
      `-._    `-.__.-'    _.-'
          `-._        _.-'
              `-.__.-'

8648:M 02 Jan 2020 16:39:01.791 # WARNING: The TCP backlog setting of 511 cannot be enforced because /proc/sys/net/core/somaxconn is set to the lower value of 128.
8648:M 02 Jan 2020 16:39:01.792 # Server initialized
8648:M 02 Jan 2020 16:39:01.792 # WARNING overcommit_memory is set to 0! Background save may fail under low memory condition. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
8648:M 02 Jan 2020 16:39:01.794 * Ready to accept connections
```
`위 화면이 나타나야 정상`

- 레디스 동작 확인 
```
$redis-cli ping
PONG
```

`위와같이 ping - pong 되면 정상 작동`

# Flask + Redis + Keras 

- 원래 포스트에서는 keras를 설치해서 하는데, Tensorflow 2.0 버전에는 Keras가 포함되어있어서 이를 사용함

1. 서버 실행
```
python run_keras_server.py 
```

`서버 정상 작동 시 아래와 같은 메세지 출력, Model Load 진행`

```
2020-01-03 16:53:23.002150: I tensorflow/stream_executor/platform/default/dso_loader.cc:44] Successfully opened dynamic library cudart64_100.dll
* Starting model service...
* Loading model...
* Starting web service...
 * Serving Flask app "run_keras_server" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
2020-01-03 16:53:29.919884: I tensorflow/stream_executor/platform/default/dso_loader.cc:44] Successfully opened dynamic library nvcuda.dll
2020-01-03 16:53:29.958846: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1618] Found device 0 with properties:
name: GeForce RTX 2060 SUPER major: 7 minor: 5 memoryClockRate(GHz): 1.65
pciBusID: 0000:01:00.0
2020-01-03 16:53:29.987878: I tensorflow/stream_executor/platform/default/dlopen_checker_stub.cc:25] GPU libraries are statically linked, skip dlopen check.
2020-01-03 16:53:29.999213: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1746] Adding visible gpu devices: 0
2020-01-03 16:53:30.004964: I tensorflow/core/platform/cpu_feature_guard.cc:142] Your CPU supports instructions that this TensorFlow binary was not compiled to use: AVX2
2020-01-03 16:53:30.012990: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1618] Found device 0 with properties:
name: GeForce RTX 2060 SUPER major: 7 minor: 5 memoryClockRate(GHz): 1.65
pciBusID: 0000:01:00.0
2020-01-03 16:53:30.026202: I tensorflow/stream_executor/platform/default/dlopen_checker_stub.cc:25] GPU libraries are statically linked, skip dlopen check.
2020-01-03 16:53:30.034947: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1746] Adding visible gpu devices: 0
2020-01-03 16:53:31.941175: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1159] Device interconnect StreamExecutor with strength 1 edge matrix:
2020-01-03 16:53:31.947551: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1165]      0
2020-01-03 16:53:31.951309: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1178] 0:   N
2020-01-03 16:53:31.957387: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1304] Created TensorFlow device (/job:localhost/replica:0/task:0/device:GPU:0 with 6310 MB memory) -> physical GPU (device: 0, name: GeForce RTX 2060 SUPER, pci bus id: 0000:01:00.0, com
pute capability: 7.5)
* Model loaded
```

2. 서버 실행 후 클라이언트(단순 POST 요청) 실행 혹은 WSL 리눅스 쉘 cURL 이용

```
- in python 
python simple_request.py
```

`클라이언트 정상 작동시 아래와 같은 메세지 출력`

```
1. golden_retriever: 0.7907
2. Tibetan_mastiff: 0.0625
3. chow: 0.0368
4. kuvasz: 0.0163
5. Newfoundland: 0.0090
```

```
- in WSL Linux Shell
$ curl -X POST -F image=@dog.png 'http://localhost:5000/predict'
```

`정상 작동시 아래와 같은 메세지 출력`

```
$ curl -X POST -F image=@dog.jpg 'http://localhost:5000/predict'
{"predictions":[{"label":"golden_retriever","probability":0.7906918525695801},{"label":"Tibetan_mastiff","probability":0.06248874217271805},{"label":"chow","probability":0.03684154152870178},{"label":"kuvasz","probability":0.01625353842973709},{"label":"Newfoundland","probability":0.00903804786503315}],"success":true}
```




