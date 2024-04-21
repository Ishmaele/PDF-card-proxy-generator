from super_image import EdsrModel, ImageLoader, MsrnModel, DrlnModel
from PIL import Image
import requests

url = 'https://paperswithcode.com/media/datasets/Set5-0000002728-07a9793f_zA3bDjj.jpg'
url2 = 'https://card-images.netrunnerdb.com/v2/large/34080.jpg'
image = Image.open(requests.get(url2, stream=True).raw)

model_name = 'drln-bam'
scale = 4

#model = MsrnModel.from_pretrained('eugenesiow/msrn', scale=2)
#model = EdsrModel.from_pretrained(f'eugenesiow/{model_name}', scale=scale)
model = DrlnModel.from_pretrained(f'eugenesiow/{model_name}', scale=scale)
inputs = ImageLoader.load_image(image)
preds = model(inputs)

ImageLoader.save_image(preds, f'./{model_name}_scaled_{scale}x.png')
ImageLoader.save_compare(inputs, preds, f'./{model_name}_{scale}x_compare.png')