import sys
import os
import subprocess
import re

from fastapi import FastAPI, File, UploadFile, Response, status
from pydantic import BaseModel
from typing import List

from PyPDF2 import PdfReader, PdfWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4

from bo.upload_bo import UploadBo

app = FastAPI()

async def makeWatermark():

    # text
    '''pdf = canvas.Canvas("watermark.pdf", pagesize=A4)
    pdf.translate(inch, inch)
    pdf.setFillColor(colors.grey, alpha=0.6)
    pdf.setFont("Helvetica", 50)
    pdf.rotate(45)
    pdf.drawCentredString(400, 100, 'SUPER HIPER Marca')
    pdf.save()'''

    # imagem
    img = ImageReader('./app/logo.jpg')
    pdf = canvas.Canvas("watermark.pdf", pagesize=A4)
    pdf.setFillColor(colors.grey, alpha=0.6)
    img_width, img_height = img.getSize()
    aspect = img_height / float(img_width)
    display_width = 380
    display_height = (display_width * aspect)
    pdf.drawImage('./app/logo.jpg',
                    (4*cm),
                    ((29.7 - 5) * cm) - display_height,
                    width=display_width,
                    height=display_height,
                    mask="auto")
    pdf.save()


async def addWaterMark(path: str) -> bytes:

    await makeWatermark()

    reader = PdfReader(path)
    page_indices = list(range(0, len(reader.pages)))

    writer = PdfWriter()

    for i in page_indices:
        content_page = reader.pages[i]

        reader_stamp = PdfReader("watermark.pdf")
        image_page = reader_stamp.pages[0]

        image_page.merge_page(content_page)
        writer.add_page(image_page)

    with open(path, "wb") as fp:
        writer.write(fp)

    with open(path, "rb") as arquivo_pdf:
        conteudo_pdf = arquivo_pdf.read()

    return conteudo_pdf


async def convert_to(file: bytes) -> str:
    with open("arquivo.docx", "wb") as arquivo_temporario:
        arquivo_temporario.write(file)

    args = ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', '.', 'arquivo.docx']

    process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)
    filename = re.search('-> (.*?) using filter', process.stdout.decode())

    retorno = await addWaterMark(filename.group(1))

    os.remove(filename.group(1))
    os.remove("arquivo.docx")
    os.remove("watermark.pdf")

    return retorno
        

@app.get('/')
def hello_world():
    return {'message': 'Hello, World!'}

@app.get('/healthcheck', status_code=status.HTTP_200_OK)
def perform_healthcheck():
    return {'healthcheck': sys.platform}

@app.post('/api/docx2pdf', status_code=status.HTTP_200_OK)
async def docx2pdf(file: UploadFile = File(...)):
    arquivo = file.file.read()

    retorno = await convert_to(arquivo)

    return Response(content=retorno,
                    media_type="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=arquivo.pdf"})


@app.post('/api/upload/replace_string')
async def replace_string(tags: str, values: str, file: UploadFile = File(...)):
    arquivo = file.file.read()

    retorno = await UploadBo.replaceString(arquivo, tags, values)
    
    return Response(content=retorno,
                    media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    headers={"Content-Disposition": "attachment; filename=arquivo.docx"})
