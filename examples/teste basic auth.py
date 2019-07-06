
import shutil

import requests

url = 'http://example.com/img.png'
response = requests.get('http://192.168.15.42/ISAPI/Streaming/channels/201/picture?snapShotImageType=JPEG', auth=('admin', 'Esiexata2017'), stream=True)
with open('img.png', 'wb') as out_file:
    shutil.copyfileobj(response.raw, out_file)
del response