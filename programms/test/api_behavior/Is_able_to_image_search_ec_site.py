from dotenv import load_dotenv
from google.cloud import vision

load_dotenv()

def search_image(search_url, image_url):
    client = vision.ImageAnnotatorClient()
    print(search_url)

    image = vision.Image()
    image.source.image_uri = image_url

    response = client.web_detection(image=image)
    annotations = response.web_detection
    if annotations.pages_with_matching_images:
        for page in annotations.pages_with_matching_images:
            if any(domain in page.url for domain in search_url):
                print(page.url)
    return

# 対象のECサイト
search_url = ['https://s.taobao.com/']
# テスト用の画像
image_url = "https://f.media-amazon.com/images/I/31GTHO78ljL.jpg"

print(search_image(search_url=search_url, image_url=image_url))

'''
[画像検索不可サイト]
'https://www.1688.com/'
'https://item.taobao.com/'
'https://s.taobao.com/'
-->baidu_api or alibaba_cloud

'''