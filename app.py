# Created by Davi Soares at 06/01/2021
# Projeto: CompareImageStreamlit
# Feature: # Enter feature name here
# Enter feature description here

# Scenario: # Enter scenario name here
# Enter steps here

# email: davi_soares@hotmail.com


import pdf2image  #
import streamlit as st  #
import numpy as np  #
import cv2  #
from PIL import Image  #
from skimage.metrics import structural_similarity as ssim  #
import imutils  #
from email_validator import validate_email, EmailNotValidError
import mysql.connector
from mysql.connector import Error
import base64
import io

Image.MAX_IMAGE_PIXELS = 1000000000000


@st.cache(suppress_st_warning=False)
def connect(usuario, endemail, tipo, pontuacao, contador):
    """ Connect to MySQL database """
    conn = None
    try:
        conn = mysql.connector.connect(host='deparadb.mysql.uhserver.com',
                                       database='deparadb',
                                       user='daviso',
                                       password='daviSO2309@')
        if conn.is_connected():
            print('Connected to MySQL database')
            mycursor = conn.cursor()
            sqlstring = "INSERT INTO transacoes(nome, email, tipo, SSIM, cnts) VALUES(%s, %s, %s, %s, %s)"
            mycursor.execute(sqlstring, (usuario, endemail, tipo, pontuacao, contador))
            conn.commit()
            print("Deu certo")
            conn.close()
    except Error as e:
        print(e)


@st.cache(suppress_st_warning=False)
def showtime(imageRef, imageMod, imageModRGB):
    (score, diff) = ssim(imageRef, imageMod, full=True)
    diff = (diff * 255).astype("uint8")
    # st.sidebar.text("SSIM: {}".format(score))
    thresh = cv2.threshold(diff, 0, 255,
                           cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    contador = 0
    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(imageModRGB, (x, y), (x + w, y + h), (0, 0, 255), 2)
        print(cv2.boundingRect(c))
        contador = contador + 1
    contador = contador / 4
    return contador, score, imageModRGB


@st.cache(suppress_st_warning=False)
def get_image_download_link(img):
    """Generates a link allowing the PIL image to be downloaded
    in:  PIL image
    out: href string
    """
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{img_str}">Download imagem</a>'
    return href

if __name__ == '__main__':
    st.set_page_config(
        page_title="Cara-Crachá",

        page_icon="inspect.png",

        layout="wide",

        initial_sidebar_state="collapsed")

    st.markdown("""
    <style>
    .big-title {
    	font-family: Courier;
    	color: red;
    	font-size:90px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<p class="big-title">Kra-Crachá!</p>', unsafe_allow_html=True)
    st.markdown("""
    <style>
    .big-font {
        font-size:35px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<p class="big-font">Não cometemos o erro de deixar passar um único erro.</p>', unsafe_allow_html=True)
    st.markdown('-' * 17)

    st.sidebar.title('Configurações')

    st.sidebar.title("Verificar", )
    st.sidebar.checkbox("Contorno", key="chkContorno")
    st.sidebar.checkbox("Texto", key="chkTexto")
    expander = st.beta_expander("Seleção de arquivos", expanded=True)
    if expander:
        expander.markdown("***Procure inserir documentos com comprimento máximo de 2500 pixels.***")
        opcoes_menu = ['Desenho', 'Foto', 'Texto']
        opcao = expander.selectbox("Escolha um tipo de análise:", opcoes_menu, index=0, )
        col1, col2 = expander.beta_columns(2)
        col1.markdown("**Carregue o desenho referência**")
        imagem_referencia = col1.file_uploader("", type=['jpg', 'jpeg', 'png', 'tiff'])
        if imagem_referencia is not None:
            if imagem_referencia.type == 'application/pdf':
                images = pdf2image.convert_from_bytes(imagem_referencia.read())
                for page in images:
                    imagemexibicao = col1.empty()
                    dtimgref = page
                    col1.header(opcao + " original")
                    imagemexibicao = col1.image(dtimgref, use_column_width=True)
                    imageRefRGB = np.array(dtimgref.convert('RGB'))
                    imageRef = cv2.cvtColor(imageRefRGB, cv2.COLOR_RGB2GRAY)
                    if imageRef.shape[1] > 2000:
                        imageRef = cv2.resize(imageRef, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_LINEAR)
                    w, h = imageRef.shape
                    dimensoes = col1.text(f"Dimensões: {w} x {h}")
                    boolimgref = True
            else:
                imagemexibicao = col1.empty()
                dtimgref = Image.open(imagem_referencia)
                col1.header(opcao + " original", )
                imagemexibicao = col1.image(dtimgref, use_column_width=True)
                imageRefRGB = np.array(dtimgref.convert('RGB'))
                imageRef = cv2.cvtColor(imageRefRGB, cv2.COLOR_RGB2GRAY)
                imageRef = cv2.resize(imageRef, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_LINEAR)
                w, h = imageRef.shape
                dimensoes = col1.text(f"Dimensões: {w} x {h}")
                boolimgref = True
        else:
            col1.image("placeholder.png", width=300)
            boolimgref = False
        col2.markdown("**Carregue o desenho a ser comparado**")
        imagem_modficada = col2.file_uploader("", type=['jpg', 'jpeg', 'png', 'tiff'], key="ImagemModif")
        if imagem_modficada is not None:
            if imagem_modficada.type == 'application/pdf':

                imagesmod = pdf2image.convert_from_bytes(imagem_modficada.read())
                for pagemod in imagesmod:
                    imagemmodexi = col2.empty()
                    imageMod = pagemod
                    col2.header(opcao + " para estudo")
                    imagemmodexi = col2.image(imageMod, use_column_width=True)
                    imageModRGB = np.array(imageMod.convert('RGB'))
                    if imageMod.shape[1]>2000:
                        print("reduzindo")
                        imageMod = cv2.resize(imageModRGB, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_LINEAR)
                    imageModRGB = imageMod
                    imageMod = cv2.cvtColor(imageMod, cv2.COLOR_RGB2GRAY)
                    w, h = imageMod.shape
                    dimensoes = col2.text(f"Dimensões: {w} x {h}")
                    boolimgmod = True
            else:
                dtimgmod = Image.open(imagem_modficada)
                col2.header(opcao + " para estudo")
                col2.image(dtimgmod, use_column_width=True)
                imageMod = np.array(dtimgmod.convert('RGB'))
                imageMod = cv2.resize(imageMod, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_LINEAR)
                imageModRGB = imageMod
                imageMod = cv2.cvtColor(imageMod, cv2.COLOR_RGB2GRAY)
                w, h = imageMod.shape
                col2.text(f"Dimensões: {w} x {h}")
                boolimgmod = True
        else:
            col2.image("placeholder.png", )
            boolimgmod = False

    expanderinicial = st.beta_expander("Dados para envio do arquivo", expanded=True)
    if expanderinicial:
        username = expanderinicial.text_input("Digite o seu nome.")
        email = expanderinicial.text_input("Digite o seu email")
        btncomparar = st.button("Comparar")
    if btncomparar:
        if username is not None and email is not None:
            try:
                # Validate.
                valid = validate_email(email)

                # Update with the normalized form.
                email = valid.email

            except EmailNotValidError as e:
                # email is not valid, exception message is human-readable
                expanderinicial.warning('Email inválido')
                pass
            if imagem_modficada is not None and imagem_referencia is not None:
                contador, score, imageModRGB = showtime(imageRef, imageMod, imageModRGB)
                st.success('Operação realizada com sucesso.')
                if score < 1:
                    st.sidebar.title("Status")
                    st.sidebar.markdown("**Resultado:**" + " Diferença computada")
                    st.sidebar.markdown("**Número de divergências:** {} divergências".format(contador))
                    expander2 = st.beta_expander("Resultados", expanded=True)
                    if expander2:
                        expander2.markdown("**Para receber o arquivo, pressione o botão 'Salvar' ao fim da página**")
                        scoredb = "{:.2f}".format(score)
                        connect(username, email, opcao, scoredb, contador)
                        expander2.image(imageModRGB, use_column_width=True)
                        if imageModRGB.shape[1] > 2000:
                            imageModRGB = cv2.resize(imageModRGB, None, fx=1.6, fy=1.6, interpolation=cv2.INTER_LINEAR)
                        result = Image.fromarray(imageModRGB)
                        # st.subheader('**Download dos Dados**')
                        st.markdown(get_image_download_link(result), unsafe_allow_html=True)
                else:
                    st.sidebar.markdown("**Resultado:**" + " Arquivos iguais")
        else:
            expander.warning("Insira um nome e email válido")
    link = '[Criado por: Davi Soares](https://www.linkedin.com/in/davi-soares-batista-2a14692b/)'

    st.markdown(link, unsafe_allow_html=True)
