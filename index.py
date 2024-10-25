from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Spacer
from reportlab.lib.utils import ImageReader
from  io import BytesIO
import uuid
import math
import qrcode

#no_of_qr = 139


def draw_each_layout(count,c,no_of_qr,base_x,base_y,start_x,end_x,start_y,end_y,layout,prefix,s_num):
    qr_dimension = 20 #mm
    outerbox_dimension = 26
    for x in range (start_x, end_x):
        if layout%2 != 0 and layout!=0:
            x+=1
        if no_of_qr == count:
           break
        for y in range (start_y, end_y):
            
            if no_of_qr == count:
                break
            # if 2 <= layout <= 3:
            #     y += 1
            # elif 4 <= layout <= 5:
            #     y += 2

            #print("y number",y)
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=0,
            )
            #data = str(uuid.uuid4())
            
            # For tamperloks
            qr_parameter = prefix + f"{s_num:06}" +"AA"
            # For neokit
            # qr_parameter = prefix + f"{s_num:05}"
            url = rf"https://www.neovault.app/scan?sn={qr_parameter}"
            image_io = BytesIO()
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image()
            img.save(image_io)
            image = ImageReader(image_io)
            
            #c.drawImage("background_2.jpeg",x*15*mm, y*15*mm,13*mm,13*mm)
            print("x",x)
            c.drawImage("outerbox.png",x*base_x*mm, y*base_y*mm,outerbox_dimension*mm,outerbox_dimension*mm)
            c.drawImage("neo_ss.png",x*base_x*mm + 17.0,y*base_y*mm + 2.0,13.4*mm,3.6*mm) #2.3 in 2.1 for (6)
            c.drawImage(image, x*base_x*mm+6.0, y*base_y*mm+13.0, qr_dimension*mm, qr_dimension*mm)
            c.rotate(90)
            # For tamperloks
            c.setFont("Helvetica-Bold", 2.8*2)
            c.drawString(y*base_y*mm+4,-(x*base_x*mm+70.4),qr_parameter)
            # For neokit
            # c.setFont("Helvetica-Bold", 7.0)
            # c.drawString(y*base_y*mm+6,-(x*base_x*mm+70.4),qr_parameter)
            
            ###c.drawString(16*cm, -14*cm,"Hello World")
            c.rotate(270)
            s_num+=1
            count+=1
    return count,c,s_num

def add_qr_code_to_pages(count,c,no_of_qr,prefix,s_num,page):
    # no_of_layout = min(math.ceil(no_of_qr/25),6)
    no_of_layout = 1
    base_x = 30
    base_y = 30
    # cordinates_for_layout = [(1,6,1,6),(6,11,1,6),(1,6,6,11),(6,11,6,11),(1,6,11,16),(6,11,11,16)]
    cordinates_for_layout = [(1,6,1,6)]
    temp_s_num = s_num
    #print("layout",no_of_layout)
    for layout in range (no_of_layout):
        temp_s_num = s_num
        count,c,s_num = draw_each_layout(count,c,no_of_qr,base_x,base_y,cordinates_for_layout[layout][0],cordinates_for_layout[layout][1],cordinates_for_layout[layout][2],cordinates_for_layout[layout][3],layout,prefix,s_num)
        # if (layout ==1 or layout ==3 ):
        if page%2 == 0 :
            s_num = temp_s_num
        #     s_num = temp_s_num
        print("sumnmm",s_num)

    return count,c,s_num

def find_how_many_pages(no_of_qr):
    rounded_result = math.ceil(no_of_qr/25)
    return rounded_result
    

def create_qr_pdf(no_of_qr):
    #initialize pre requirements 
    no_of_qr*=2
    buffer = BytesIO()
    c = canvas.Canvas(buffer,pagesize=A4,cropMarks=False)
    count = 0
    
    prefix = "A9671-24955G"
    # start of the serial number
    s_num = 10626

    how_many_pages = find_how_many_pages(no_of_qr)
    #loop through each page
    

    for page in range(how_many_pages):
    #Add Images in a loop
        count,c,s_num = add_qr_code_to_pages(count,c,no_of_qr,prefix,s_num,page)
        c.showPage()
    c.save()
    return buffer
