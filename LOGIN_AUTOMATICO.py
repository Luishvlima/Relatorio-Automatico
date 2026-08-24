#====================================================================================================================================
#  IMPORTS INTERNOS
#====================================================================================================================================
import os
import sys
import time
import json
import re
#====================================================================================================================================
#  IMPORTS EXTERNOS
#====================================================================================================================================
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
#====================================================================================================================================
#  CLASSE PRINCIPAL PARA FAZER LOGIN NO ORACLE
#====================================================================================================================================
class FazerLoginOracle:
    def __init__(self, pasta_edge: str, log, email: str, password: str, password_oracle: str, cookie_file:json):
        #=======================================================================================================
        #  CONSTANTES 
        #=======================================================================================================
        #====VARIÁVEIS============
        self.pasta_edge         = pasta_edge
        self.email              = email
        self.password           = password
        self.password_oracle    = password_oracle
        self.log                = log
        self.cookie_file        = cookie_file

        #====TEMPO============
        self.timeout_autent     = 120  
        self.timeout_tokens     = 3
        self.timeout_pagina     = 2
        self.timeout_padrao     = 0.1
        
        #====FIXAS============
        self.url_id_login       = ""
        self.url                = ""
        self.jwt_re             = re.compile(r"eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+")

        #=======================================================================================================
        #  FLUXO PRINCIPAL
        #=======================================================================================================
        self.token    = self.obter_token()
    #====================================================================================================================================
    #  HELPERS
    #====================================================================================================================================
    #====Ação em elemento pelo ID============
    def _acao_id(self, id_elemento, acao,  valor=None):
        try:
            # =======Localiza o elemento pelo ID=========
            elemento = WebDriverWait(self.driver, self.timeout_padrao).until(
                    EC.presence_of_element_located((By.ID, id_elemento))
                )

            # =======Executa a ação especificada=========
            if acao == "click":
                elemento.click()
                time.sleep(0.1)
                
            elif acao == "send_keys" and valor is not None:
                elemento.send_keys(valor)
                time.sleep(0.1)
            return True
        except:
            return False
    #====Ação em elemento pelo seletor CSS============
    def _acao_CSS(self, seletor, acao,  valor=None):
        try:
            # =======Localiza o elemento pelo seletor=========
            elemento = WebDriverWait(self.driver, self.timeout_padrao).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, seletor))
                )

            # =======Executa a ação especificada=========
            if acao == "click":
                elemento.click()
                time.sleep(0.1)
                
            elif acao == "send_keys" and valor is not None:
                elemento.send_keys(valor)
                time.sleep(0.1)
            return True
        except:
            return False
    #====================================================================================================================================
    #  INICIAR NAVEGADOR
    #====================================================================================================================================
    def iniciar_navegador(self) -> webdriver.Edge:

        if getattr(sys, 'frozen', False):
            BASE_DIR = os.path.dirname(sys.executable)
        else:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        EDGE_USER_DATA_DIR      = os.path.join(BASE_DIR, self.pasta_edge)
        EDGE_PROFILE_DIRECTORY  = "Default"

        service = Service()
        options = EdgeOptions()
        options.add_argument(f"--user-data-dir={EDGE_USER_DATA_DIR}")
        options.add_argument(f"--profile-directory={EDGE_PROFILE_DIRECTORY}")
        options.add_argument("--log-level=3")
        options.add_argument("--disable-logging")
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches",["enable-automation", "enable-logging"])
        
        driver = webdriver.Edge(service=service, options=options)
        driver.get(self.url)
        self.log.info(f"Navegador iniciado")
        return driver
    #====================================================================================================================================
    #  COOKIES
    #====================================================================================================================================
    def salvar_cookies(self,cookies):
        try:
            with open(self.cookie_file, "w", encoding="utf-8") as arquivo:
                json.dump(cookies, arquivo, indent=2, ensure_ascii=False)
            self.log.info(f"Cookies salvos")
            return True
        except Exception as e:
            self.log.error(f"Erro ao salvar cookies: {e}")
            return False
    #====Obtenção de cookies após login============
    def obter_cookies(self):
        self.log.info("Aguardando redirecionamento final da URL.")
        inicio = time.time()
        while time.time() - inicio < self.timeout_autent:
            url_atual = self.driver.current_url
            if url_atual == self.url:
                time.sleep(1)
        
                try:
                    cookies_raw = self.driver.get_cookies()
                except Exception:
                    cookies_raw = []        
                
                cookies = {cookie.get("name"): cookie.get("value") for cookie in cookies_raw if cookie.get("name")}
                if cookies:
                    self.salvar_cookies(cookies)
                break  
        else:
            self.log.error(f"Url final não alcançada ({self.timeout_autent}s)")
    #====================================================================================================================================
    #  LOGINS
    #====================================================================================================================================
    #====Login automatico no Oracle============
    def _login_oracle(self):
        self._acao_id("username", "send_keys", self.email)
        time.sleep(self.timeout_padrao)

        self._acao_id("password", "send_keys", self.password_oracle)
        time.sleep(self.timeout_padrao)

        self._acao_id("remember_username", "click")
        time.sleep(self.timeout_padrao)

        if self._acao_id("sign-in","click"):
            return True
        else:
            self.log.error("Não foi necessário fazer login.")
            self.log.info("ETAPA 2/3 Concluída - Não foi necessário fazer login")
            self.log.info("="*60)
            print()

            return False
    #====Login automático no Microsoft Authenticator============
    def _fazer_login_microsoft(self):
        if self._acao_CSS(f'div[data-test-id="{self.email}"]', "click") == True:
            time.sleep(5)
        if self._acao_id("i0116", "send_keys", self.email) == True:
            self._acao_id("idSIButton9", "click")
            time.sleep(5)
        if self._acao_id("i0118", "send_keys", self.password) == True:
            self._acao_id("idSIButton9", "click")
            time.sleep(2)
        self._acao_CSS( 'div[data-value="PhoneAppNotification"]', "click") 
        
        self.log.info("Aguardando aprovação no Microsoft Authenticator")
        return self._aguardar_aprovacao_microsoft()
    #====Aguarda a aprovação do Microsoft Authenticator============
    def _aguardar_aprovacao_microsoft(self):
        inicio = time.time()
        while time.time() - inicio < self.timeout_autent:
            url_atual = self.driver.current_url

            if not url_atual:
                self.log.error("Sessão do navegador foi encerrada inesperadamente")
                time.sleep(2)
                return False

            if "token" in url_atual.lower() or "dashboard" in url_atual.lower() or url_atual.rstrip("/") == self.url.rstrip("/"):
                self.log.info("Autenticação bem-sucedida!")
                time.sleep(2)
                return True

            if "common/SAS/ProcessAuth" in url_atual:
                time.sleep(1)
                self._acao_id("KmsiCheckboxField", "click")   
                self._acao_id("idSIButton9", "click")         # Clica em "Sim" para manter a sessão ativa
                self.log.info("Sessão ativa mantida")
                time.sleep(2)
                return True
                
        else:
            self.log.error(f"Timeout! Nenhuma autenticação após {self.timeout_autent} segundos")
            return False
    #====================================================================================================================================
    #  MAIN
    #====================================================================================================================================
    def obter_token(self):
        #=====================MENSAGEM DE INICIO DE LOGIN AUTOMÁTICO============================
        self.log.info("="*60)
        self.log.info("INICIANDO LOGIN AUTOMÁTICO")
        self.log.info("="*60)
        print()
        self.log.info("="*60)
        self.log.info("ETAPA 1/3 - Iniciando login automático")
        self.driver = self.iniciar_navegador()
        self.log.info("ETAPA 1/3 CONCLUÍDA - Navegador iniciado com sucesso")
        self.log.info("="*60)
        print()
        time.sleep(2)
        #============================MENSAGEM DE LOGIN ORACLE===========================
        self.log.info("="*60)
        self.log.info("ETAPA 2/3 - Iniciando login")
        if self._login_oracle():
            self.log.info("Login Power Bi Realizado com sucesso")
            time.sleep(3)
            #============================MENSAGEM DE LOGIN MICROSOFT===========================
            if self._fazer_login_microsoft():
                self.log.info("Login Microsoft Realizado com sucesso")
                self.log.info("ETAPA 2/3 Concluída - Login realizado com sucesso")
                self.log.info("="*60)
                print()
                time.sleep(1)
        #============================MENSAGEM DE OBTENÇÃO DE TOKEN==============================
        self.log.info("="*60)
        self.log.info("ETAPA 3/3 - Obtendo token e salvando")
        token = self.obter_cookies()
        self.log.info("ETAPA 3/3 CONCLUÍDA - Token obtido com sucesso")
        self.log.info("="*60)
        print()
        time.sleep(1)
    
        self.log.info("="*60)
        self.log.info("SUCESSO NA DEFINIÇÃO DE TOKEN")
        self.log.info("="*60)
        print("")
        self.log.info("="*60)
        self.log.info("ETAPA 1/3 - CARREGANDO COOKIES")

        self.driver.quit()
        return token
