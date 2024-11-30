import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from io import BytesIO
import math
import qrcode
import uuid
from datetime import datetime
import requests
import time
import json

def create_qr_pdf(no_of_qr, productName, variant, serialNumber):
    no_of_qr *= 2
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4, cropMarks=False)
    count = 0
    year_last_two_digits = str(datetime.now().year)[-2:]
    
    prefix = f"{variant}-{year_last_two_digits}{'955G' if productName == 'TamperLoks' else 'AA'}"
    s_num = int(serialNumber)
    how_many_pages = find_how_many_pages(no_of_qr)
    
    for page in range(how_many_pages):
        count, c, s_num = add_qr_code_to_pages(count, c, no_of_qr, prefix, s_num, page, productName)
        c.showPage()
    c.save()
    return buffer

def find_how_many_pages(no_of_qr):
    return math.ceil(no_of_qr / 25)

def add_qr_code_to_pages(count, c, no_of_qr, prefix, s_num, page, productName):
    no_of_layout = 1
    base_x = 30
    base_y = 30
    cordinates_for_layout = [(1, 6, 1, 6)]
    temp_s_num = s_num

    for layout in range(no_of_layout):
        temp_s_num = s_num
        count, c, s_num = draw_each_layout(count, c, no_of_qr, base_x, base_y, cordinates_for_layout[layout][0], cordinates_for_layout[layout][1], cordinates_for_layout[layout][2], cordinates_for_layout[layout][3], layout, prefix, s_num, productName)
        if page % 2 == 0:
            s_num = temp_s_num

    return count, c, s_num

def draw_each_layout(count, c, no_of_qr, base_x, base_y, start_x, end_x, start_y, end_y, layout, prefix, s_num, productName):
    qr_dimension = 20  # mm
    outerbox_dimension = 26
    for x in range(start_x, end_x):
        if layout % 2 != 0 and layout != 0:
            x += 1
        if no_of_qr == count:
            break
        for y in range(start_y, end_y):
            if no_of_qr == count:
                break
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=0)
            
            if productName == "TamperLoks":
                qr_parameter = f"{prefix}{s_num:06}AA"
            else:
                qr_parameter = f"{prefix}{s_num:05}"

            url = rf"https://www.neovault.app/scan?sn={qr_parameter}"
            image_io = BytesIO()
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image()
            img.save(image_io)
            image = ImageReader(image_io)
            c.drawImage("outerbox.png", x * base_x * mm, y * base_y * mm, outerbox_dimension * mm, outerbox_dimension * mm)
            c.drawImage("neo_ss.png", x * base_x * mm + 17.0, y * base_y * mm + 2.0, 13.4 * mm, 3.6 * mm)
            c.drawImage(image, x * base_x * mm + 6.0, y * base_y * mm + 13.0, qr_dimension * mm, qr_dimension * mm)
            c.rotate(90)
            c.setFont("Helvetica-Bold", 5.6 if productName == "TamperLoks" else 7.0)
            c.drawString(y * base_y * mm + 4, -(x * base_x * mm + 70.4), qr_parameter)
            c.rotate(270)
            s_num += 1
            count += 1
    return count, c, s_num

products = []
varients = []
with open('data.json', 'r', encoding='utf-8') as file:
    jsonValues = json.load(file)
for item in jsonValues:
    products.append(item['name'])
st.title("QR Code PDF Generator")

no_of_qrcode = st.number_input("Enter the number of QR codes:", min_value=1, step=1)
serialNumber = st.text_input("Enter the stock serial number:")
main_variant = st.selectbox("Choose a main variant", products)
for i in jsonValues:
    if i['name'] == main_variant:
        for j in i['skus']:
            varients.append(j['skuId'])

variant = st.selectbox("Choose a variant", varients)

if st.button("Generate PDF"):
    if no_of_qrcode > 0:
        pdf_buffer = create_qr_pdf(no_of_qrcode, main_variant, variant, serialNumber)
        st.download_button(
            label="Download QR Code PDF",
            data=pdf_buffer,
            file_name="qr_output.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Please enter a number greater than 0.")
