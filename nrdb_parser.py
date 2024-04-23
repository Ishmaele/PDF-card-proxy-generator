import requests
import sys
import getopt
from io import BytesIO

from img_transform import create_3x3_sheets


usage = 'nrdb_parser.py -d <deck id>'


class nrdbAPI():
    def __init__(self, deck_id: str = ""):
        self.deck_id = deck_id
        self.base_decklist_url = "https://netrunnerdb.com/api/2.0/public/decklist/"
        self.base_image_url = "https://card-images.netrunnerdb.com/v2/large/"
        self.cards_url = "https://netrunnerdb.com/api/2.0/public/cards"
        self.packs_url = "https://netrunnerdb.com/api/2.0/public/packs"
        self.MODE = 'RGB'

    def get_decklist(self):
        deck_request = requests.get(self.base_decklist_url + str(self.deck_id))

        if deck_request.status_code == 200:
            self.deck_data = deck_request.json()
            return self.deck_data
        else:
            print("Error: Could not retrieve decklist")
            return False

    def get_decklist_images(self, deck_data, perform_upscale=False) -> list:
        '''Returns images from NRDB according to decklist id:count'''
        self.nrdb_proxy_list = []
        self.resized_proxy_list = []
        try:
            for card_id, number in deck_data['data'][0]['cards'].items():
                #card_picture = requests.get("https://netrunnerdb.com/card_image/" + card_id + ".png")
                card_picture_response = requests.get(self.base_image_url + card_id + ".jpg")
                card_picture_content = BytesIO(card_picture_response.content)

                # Create a list of all pictures to be resized+printed (including duplicates)
                for cards in range(0, number):
                    self.nrdb_proxy_list.append(card_picture_content)
        except Exception as ex:
            print('Error: failed getting images from nrdb')
            return False

        return self.nrdb_proxy_list


    def get_cardlist_images(self, nrdb_cards: list, images: dict) -> list:
        '''Returns images from NRDB according to cards list'''
        try:
            for card in nrdb_cards:
                # get img bytes by id
                print(self.base_image_url + card['code'] + ".jpg")
                card_picture_response = requests.get(self.base_image_url + card['code'] + ".jpg")
                card_picture_content = BytesIO(card_picture_response.content)
                images[card['code']] = card_picture_content
        except Exception as ex:
            print('Error: failed getting images from nrdb')
            return False

        return images

    def get_all_cards(self):
        '''all cards info'''
        cards_request = requests.get(self.cards_url)
        if cards_request.status_code == 200:
            cards_data = cards_request.json()
        else:
            print("Error: Could not retrieve all cards")

        return cards_data
    
    def get_all_packs(self):
        '''all packs (sets) info'''
        packs_request = requests.get(self.packs_url)
        if packs_request.status_code == 200:
            packs_data = packs_request.json()
        else:
            print("Error: Could not retrieve all packs")

        return packs_data


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(usage)
    else:
        deck_id = -1
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'd:', ["deckid="]) #Get the deck id from the command line

            for opt, arg in opts:
                if opt in ("-d", "--deckid"):
                    deck_id = arg
                else:
                    print ("Unsupported argument found!")
        except getopt.GetoptError as e:
            print("Error: " + str(e))
            print(usage)
            sys.exit(2)

        nrdb_api = nrdbAPI(deck_id)

        #get cards list from nrdb
        deck_data = nrdb_api.get_decklist()

        #get resized images from nrdb
        proxy_list = nrdb_api.get_decklist_images(deck_data)

        #make 3x3 image grids
        sheets = create_3x3_sheets(proxy_list, nrdb_api.MODE)

        #write to pdf
        sheets[0].save(str(deck_id) + f'_{nrdb_api.MODE}.pdf', save_all=True, append_images=sheets[1:])
