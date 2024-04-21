from PIL import Image
import math
from super_image import EdsrModel, ImageLoader
import cv2


DEFAULT_ITEM_WIDTH=732
DEFAULT_ITEM_HEIGHT=1018
DEFAULT_PADDING_HORIZONTAL=142
DEFAULT_PADDING_VERTICAL=221


def resize_images(imgs):
    resized_result = []
    for image in imgs:
        card_picture = Image.open(image)
        resized_card_picture = card_picture.resize((DEFAULT_ITEM_WIDTH, DEFAULT_ITEM_HEIGHT), Image.LANCZOS)
        resized_result.append(resized_card_picture)
    return resized_result


def create_3x3_sheets(proxy_list: list, color_mode: str) -> list:
    '''
    Creates 3x3 grids
    :param proxy_list: a list of PIL Image objects.
    '''
    PIL_BACKGROUNDS = {
        'RGB': 'white',
        'CMYK': (0,0,0,0)
    }

    proxy_index = 0
    sheets = []

    for sheet_count in range(0, math.ceil(len(proxy_list) / 9)): # calc 3x3 grids count
        sheet = Image.new(color_mode, (DEFAULT_ITEM_WIDTH * 3 + DEFAULT_PADDING_HORIZONTAL * 2, DEFAULT_ITEM_HEIGHT * 3 + DEFAULT_PADDING_VERTICAL * 2), color=PIL_BACKGROUNDS[color_mode]) #a sheet is 3 rows of 3 cards
        y_offset = DEFAULT_PADDING_VERTICAL
        # Fill three rows of three images
        rows = [Image.new(color_mode, (DEFAULT_ITEM_WIDTH * 3, DEFAULT_ITEM_HEIGHT), color=PIL_BACKGROUNDS[color_mode]) for _ in range(3)]
        for row in rows:
            x_offset = 0

            for j in range(proxy_index, proxy_index + 3):
                if j >= len(proxy_list):
                    break
                row.paste(proxy_list[j], (x_offset, 0))
                x_offset += DEFAULT_ITEM_WIDTH + 3 # 3 - line between images

            # Combine rows vertically into one image
            sheet.paste(row, (DEFAULT_PADDING_HORIZONTAL, y_offset))
            y_offset += DEFAULT_ITEM_HEIGHT + 3 # 3 - line between images
            proxy_index += 3
            if proxy_index >= len(proxy_list):
                break

        sheets.append(sheet)
    return sheets


class imgUpscaler():
    def __init__(self, model_name, scale) -> None:
        self.model_name = model_name
        self.scale = scale
        self.model = EdsrModel.from_pretrained(f'eugenesiow/{model_name}', scale=scale)
        
    def process(self, image) -> bytes:
        inputs = ImageLoader.load_image(image)
        preds = self.model(inputs)
        keks = ImageLoader._process_image_to_save(preds)
        image_bytes = cv2.imencode('.png', keks)[1].tobytes()
        return image_bytes
    