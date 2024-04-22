import streamlit as st

from nrdb_parser import nrdbAPI
from img_transform import resize_images, create_3x3_sheets, imgUpscaler
from io import BytesIO
from PIL import Image

import requests # dev


"# NetrunnerDB module"
"""This module seeks to replicate https://proxynexus.net/ functionality, except it doesn't store image data in a local DB. Instead, it pulls card images from netrunnerdb.com API."""
st.divider()
"""NRDB images are low quality JPEGs. The image quality can be significantly improved by applying the ML upscaling algorithm (edsr-base model, 3x scaling). *This will increase PDF generation time significantly.*"""

tab1, tab2, tab3 = st.tabs(["Decklist", "Card list", "Set"])

with tab1:
    deck_id = st.text_input(label='Enter a decklist URL from NetrunnerDB', placeholder='81524', value=None)
    st.caption('Only Published decklist are supported currently. eg. https://netrunnerdb.com/en/decklist/xxxxx/deck-name https://netrunnerdb.com/en/deck/view/xxxxxxx ')
    perform_upscale = st.checkbox('Perform ML upscale (slow, higher quality)')


    if deck_id is not None:
        if st.button(label='Start'):
            nrdb_api = nrdbAPI(deck_id)
            with st.status("Polling NRDB API..."):
                #get cards list from nrdb
                deck_data = nrdb_api.get_decklist()
                st.write(deck_data)
                #get images from nrdb
                nrdb_api.get_images(deck_data, False)
                
            if perform_upscale:
                upscaler = imgUpscaler('edsr-base', 3)
                temp = []
                bar = st.progress(0, text='Upscaling images...')
                i = 1
                # with st.status("Upscaling"):
                for bytes_file in nrdb_api.nrdb_proxy_list:
                    image = Image.open(bytes_file)
                    image_bytes = upscaler.process(image)
                    temp.append(BytesIO(image_bytes))
                    bar.progress(int(100 * i / len(nrdb_api.nrdb_proxy_list)), text='Upscaling images...')
                    i+=1
                nrdb_api.nrdb_proxy_list = temp

            nrdb_api.resized_proxy_list = resize_images(nrdb_api.nrdb_proxy_list)

            with st.status("Generating PDF..."):
                #make 3x3 image grids
                sheets = create_3x3_sheets(nrdb_api.resized_proxy_list, nrdb_api.MODE)
                st.write('Total sheets: ', len(sheets))

                if len(sheets) > 0:
                    img_byte_arr = BytesIO()
                    sheets[0].save(img_byte_arr, format='PDF', save_all=True, append_images=sheets[1:])

            if len(sheets) > 0:
                st.download_button(':arrow_down: :red[Download PDF]', img_byte_arr, file_name=f'{deck_id}.pdf')

with tab2:
    st.write('DEV')
    card_input = st.text_area(label='Enter card names below', placeholder='Rebirth\nThe Twins\nDescent', value=None, key='input_card_list')
    if card_input:
        card_list = card_input.splitlines()
        st.write(f'Total cards: {len(card_list)}')

        cards_url = "https://netrunnerdb.com/api/2.0/public/cards"
        base_image_url = "https://card-images.netrunnerdb.com/v2/large/"

        # Initialization
        if 'result_cards' not in st.session_state:
            result_cards = {}

        # img storage is persistent between reruns because we don't want to poll API every time
        if 'imgs' not in st.session_state:
            st.session_state['imgs'] = {}


        result_cards = {}
        # all cards info
        cards_request = requests.get(cards_url)
        if cards_request.status_code == 200:
            cards_data = cards_request.json()
        else:
            print("Error: Could not retrieve all cards")
        
        # filter cards (search)
        for card_name in card_list:
            filtered_for_name = [card for card in cards_data['data'] if card_name in card['stripped_title']]
            result_cards[card_name] = {'cards': filtered_for_name, 'imgs' : {}}

        # get card imgs
        if st.button(label='Get Images'):
            with st.status("Polling NRDB API..."):
                for item in result_cards:
                    for card in result_cards[item]['cards']:
                        # get img bytes by id
                        try:
                            print(base_image_url + card['code'] + ".jpg")
                            card_picture_response = requests.get(base_image_url + card['code'] + ".jpg")
                            card_picture_content = BytesIO(card_picture_response.content)
                            # result_cards[item]['imgs'][card['code']] = card_picture_content
                            st.session_state['imgs'][card['code']] = card_picture_content
                        except Exception as ex:
                            print('Error: failed getting image from nrdb')
                            print(ex)

                st.write(result_cards)
        
        # display cards
        if len(st.session_state['imgs']) > 0:
            for item in result_cards:
                if len(result_cards[item]['cards']) > 1:
                    # multiple choice
                    chosen_card_code = st.selectbox(label=item, options=[f'{card['code']}' for card in result_cards[item]['cards']])
                    st.image(st.session_state['imgs'][chosen_card_code], width=225, caption=item)
                if len(result_cards[item]['cards']) == 1:
                    id = result_cards[item]['cards'][0]['code']
                    st.image(st.session_state['imgs'][id], width=225, caption=item)

with tab3:
    st.write('TODO 2')
    