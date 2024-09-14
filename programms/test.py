from google.cloud import vision
import os
import dotenv
import requests

dotenv.load_dotenv()
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Google Cloud Vision APIクライアントを作成
client = vision.ImageAnnotatorClient()

image_url = "https://m.media-amazon.com/images/I/81SZekrUnEL.jpg"

image = vision.Image()
image.source.image_uri = image_url

# Web Detectionリクエストを作成
response = client.web_detection(image=image)
web_detection = response.web_detection

target_domains = ["www.amazon.com", "www.walmart.com"]

# 完全一致する画像を取得
if web_detection.pages_with_matching_images:
    for page in web_detection.pages_with_matching_images:
        if any(domain in page.url for domain in target_domains):
            print(f'URL: {page.url}')
else:
    print('完全一致する画像は見つかりませんでした。')
