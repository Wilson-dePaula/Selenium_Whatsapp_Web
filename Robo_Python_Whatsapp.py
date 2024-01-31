#Robô Whatsapp

# Essa automação tem como objetivo enviar mensagens individuais e automáticas
# pelo whatsapp com base em uma lista de contatos

# Desenvolvedor: Wilson de Paula Alves
# Ano: 2022

#-----------------------------------------

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as cond
from datetime import datetime, timedelta
import time
import urllib
import logging
import pandas as pd
import sys
from subprocess import call
import warnings

warnings.filterwarnings('ignore')

log_format = '%(asctime)s %(message)s'
logging.basicConfig(filename='Robô_Whatsapp.log',
                    filemode='a',
                    level=logging.INFO,
                    format=log_format)
logger = logging.getLogger('root')

midia = r'C:\Python\Robo_WhatsApp\teste.jpeg'
your_user_folder = ''
now = datetime.now()
end_cod = now + timedelta(minutes=200)

options = webdriver.ChromeOptions()
options.add_argument(rf'user-data-dir=C:\Users\{your_user_folder}\AppData\Local\Google\Chrome\User Data\Default\ ')
tabela_contatos = pd.read_csv('contatos.csv', delimiter=";", encoding='utf-8')

def enviar_midia(midia, driver):
    driver.find_element(By.CSS_SELECTOR, "span[data-icon='clip']").click()
    attach = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
    attach.send_keys(midia)
    time.sleep(3)
    send = driver.find_element(By.CSS_SELECTOR, "span[data-icon='send']")
    send.click()

def saudacao_func():
    hora = datetime.now().hour
    if hora < 12:
        saudacao = "Bom dia"
    elif 12 <= hora < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"
    return saudacao

def envia_mensagem(driver):
    global tabela_contatos, ultimo_contato

    texto = ''


    try:
        driver.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p').click()
        time.sleep(2)
        mensagem = driver.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p')
        mensagem.send_keys(texto)
        time.sleep(2)
        mensagem.send_keys(Keys.SHIFT + Keys.ENTER)

    except NoSuchElementException:
        logger.info('Erro ao enviar mensagem no WhatsApp Web')
        tabela_contatos.loc[ultimo_contato, 'Status'] = 'Erro no envio da mensagem'
        tabela_contatos.to_csv('contatos.csv', sep=';', index=False)
        sys.exit()



# Robô Principal
if __name__ == '__main__':

    with open('contador_contatos.txt', 'r') as cont:
        ultimo_contato = int(cont.read())

    try:
        logger.info('Robô iniciando automação')
        driver = webdriver.Chrome(executable_path=r'C:\Python\Python310\chromedriver.exe', options=options)
        driver.get('https://web.whatsapp.com/')
        logger.info('Whatsapp iniciado com sucesso')
    except:
        logger.info('Erro ao conectar com o WhatsApp Web')
        sys.exit()

    WebDriverWait(driver, 80).until(cond.visibility_of_element_located((By.ID, 'pane-side')))

    while now < end_cod:
        if len(tabela_contatos['Nome']) <= ultimo_contato:
            break
        try:
            logger.info('Iniciando processo envio de mensagem aos remetentes')
            saudacao = saudacao_func()
            pessoa = tabela_contatos.loc[ultimo_contato, 'Nome']
            numero = tabela_contatos.loc[ultimo_contato, 'Telefone']
            texto = urllib.parse.quote(f"Meu caro irmão e irmã, {saudacao}")
            logger.info('Saudações formulada')
            link = f"https://web.whatsapp.com/send?phone={numero}&text={texto}"
            driver.get(link)

            try:
                WebDriverWait(driver, 40).until(cond.visibility_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p')))
            except:
                if 'inválido' in driver.find_element(By.XPATH, '// *[ @ id = "app"] / div / span[2] / div / span / div / div / div / div / div / div[1]').text:
                    tabela_contatos.loc[ultimo_contato, 'Status'] = 'Número inválido'
                    tabela_contatos.to_csv('contatos.csv', sep=';', index=False)
                    with open("contador_contatos.txt", "w") as cont:
                        ultimo_contato += 1
                        cont.write(str(ultimo_contato))

                    continue
                else:
                    logger.info('Erro não mapeado')
                    tabela_contatos.loc[ultimo_contato, 'Status'] = 'Erro no envio da mensagem'
                    tabela_contatos.to_csv('contatos.csv', sep=';', index=False)
                    sys.exit()

            time.sleep(10)
            driver.find_element(By.XPATH,'//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p').send_keys(Keys.ENTER)
            logger.info('Saudações enviadas')
            time.sleep(10)
            envia_mensagem(driver)
            enviar_midia(midia, driver)
            logger.info('Mensagem enviada')
            tabela_contatos.loc[ultimo_contato, 'Status'] = 'Mensagem enviada'
            tabela_contatos.to_csv('contatos.csv', sep=';', index=False)
            time.sleep(10)

            logger.info('Atualizando contador')
            with open("contador_contatos.txt", "w") as cont:
                ultimo_contato += 1
                cont.write(str(ultimo_contato))
        except:
            logger.info('Erro no processo de envio das mensagens.')
            texto_erro = urllib.parse.quote(f"O robô está apresentando inconsistência")
            link = "https://web.whatsapp.com/send?phone={}&text={texto_erro}"
            driver.get(link)
            WebDriverWait(driver, 40).until(cond.visibility_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p')))
            driver.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p').send_keys(Keys.ENTER)
            tabela_contatos.loc[ultimo_contato, 'Status'] = 'Erro no envio da mensagem'
            tabela_contatos.to_csv('contatos.csv', sep=';', index=False)
            sys.exit()

        now = datetime.now()

    print('Fim da execução')
    sys.exit()