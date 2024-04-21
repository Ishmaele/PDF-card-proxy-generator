import streamlit as st

from nrdb_parser import nrdbAPI
from img_transform import resize_images, create_3x3_sheets, imgUpscaler
from io import BytesIO
from PIL import Image


st.write('TODO')
deck_id = st.text_input(label='NetrunnerDB decklist id', placeholder='81524', value=None)
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
