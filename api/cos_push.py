import requests
from qcloud_cos import CosConfig, CosS3Client

SECRET_ID = 'AKIDb9TZQ22pOHyQgiV3OUTt7ILLCvSlvufD'
SECRET_KEY = 'QefT2NVP5YptjLlyxgBRXR8csuiKjvsd'
REGION = 'ap-hongkong'
BUCKET = 'hygzzcn-1352601878'

# Download current board.html
r = requests.get('https://hygzz.中国/board.html')
board = r.text
print(f'Downloaded: {len(board)} bytes')

# Fix hubs
board = board.replace('ADDENDUM_HUB = "https://hygzz.com/api"', 'ADDENDUM_HUB = "https://hygzz.cn/api"')
board = board.replace('BASELINE_HUB = "https://1352601878-lyrlgvm3bv.ap-guangzhou.tencentscf.com', 'BASELINE_HUB = "https://hygzz.cn/api')
print('Fixed hubs')

# Upload
config = CosConfig(Region=REGION, SecretId=SECRET_ID, SecretKey=SECRET_KEY)
client = CosS3Client(config)
client.put_object(Bucket=BUCKET, Key='board.html', Body=board.encode(), ContentType='text/html; charset=utf-8')
print('Uploaded!')

# Verify
r2 = requests.get('https://hygzz.中国/board.html')
print(f'Verify: {r2.status_code}, {len(r2.text)} bytes')
print(f'ADDENDUM_HUB fixed: {"hygzz.cn/api" in r2.text}')
print(f'BASELINE_HUB fixed: {"hygzz.cn/api" in r2.text}')
