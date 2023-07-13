
from fastapi import FastAPI, File, UploadFile, Response, status

from .bo.upload_bo import UploadBo

app = FastAPI()


@app.get('/')
def hello_world():
    return {'message': 'Hello, World!'}

@app.post('/api/docx2pdf', status_code=status.HTTP_200_OK)
async def docx2pdf(doc: UploadFile = File(...), image: UploadFile = File(...)):
    arquivo_doc = doc.file.read()
    arquivo_image = image.file.read()

    retorno = await UploadBo.convert_to(arquivo_doc, arquivo_image)

    return Response(content=retorno,
                    media_type="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=arquivo.pdf"})


@app.post('/api/replace_string')
async def replace_string(tags: str, values: str, file: UploadFile = File(...)):
    arquivo = file.file.read()

    retorno = await UploadBo.replaceString(arquivo, tags, values)
    
    return Response(content=retorno,
                    media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    headers={"Content-Disposition": "attachment; filename=arquivo.docx"})
