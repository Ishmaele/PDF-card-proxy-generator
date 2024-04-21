import streamlit as st
from io import BytesIO

from img_transform import resize_images, create_3x3_sheets


st.set_page_config(
        page_title="PDF card proxy generator",
)

st.markdown(
    """
    <style>
    img {
        cursor: pointer;
        transition: all .2s ease-in-out;
    }
    img:hover {
        transform: scale(1.1);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

"# PDF card proxy generator"

"""This app can generate printout-ready PDF with 3x3 grid of standard size game cards (MTG, FFG cards etc.) for the purpose of proxying.
Card images need to be uploaded via the upload menu below. The desired amount of copies of each card can be set both globally (use the slider) and individually."""
st.divider()
"""All uploaded images should use the **same color mode**! Please, make sure that all images are either **RGB** or **CMYK** before uploading, and choose the mode accordingly in the selector below."""

color_mode = st.radio(label='Color mode', options=['CMYK', 'RGB'], index=None)
uploaded_files = st.file_uploader("Choose a IMG file", accept_multiple_files=True)
default_card_count = st.slider(label='Select default number of copies (can be changed for individual cards below)', min_value=1, max_value=6, value=1)


if uploaded_files is not None:
    # display grid
    grid = st.columns(3, gap='small')
    col = 0
    for image in uploaded_files:
        with grid[col]:
            st.image(image, width=225, caption=image.name)
            number = st.number_input(label=image.name, value=default_card_count, key='count_' + image.name, label_visibility="hidden")
            #st.write(st.session_state['count_' + image.name])

        col = (col + 1) % 3

    if len(uploaded_files) > 0:
        if color_mode is None:
            st.write('Please choose the color mode')
        else:
            if st.button(label='Generate PDF'):
                with st.status("Generating PDF..."):
                    # add extra copies
                    all_files_with_copies = []
                    for file in uploaded_files:
                        target_count = st.session_state['count_' + file.name]
                        for cards in range(0, target_count):
                            all_files_with_copies.append(file)

                    st.write('Total cards: ', len(all_files_with_copies))
                    proxy_list = resize_images(all_files_with_copies) # [PIL.Image]

                    sheets = create_3x3_sheets(proxy_list, color_mode)
                    st.write('Total sheets: ', len(sheets))

                    st.write(st.session_state)
                    if len(sheets) > 0:
                        img_byte_arr = BytesIO()
                        sheets[0].save(img_byte_arr, format='PDF', save_all=True, append_images=sheets[1:])

                if len(sheets) > 0:
                    st.download_button(':arrow_down: :red[Download PDF]', img_byte_arr, file_name='PROXIES.pdf')
