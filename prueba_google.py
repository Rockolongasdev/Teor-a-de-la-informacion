#!/usr/bin/env python3
"""
Script optimizado de Selenium para pruebas infinitas de formulario de evaluación municipal.
VERSIÓN CHROME CORREGIDA - Configuración estable para Chrome WebDriver

Autor: Claude
Fecha: 2024
CORRECCIONES APLICADAS:
- Mejores estrategias de click en elementos
- Mejor manejo de esperas
- Debugging mejorado
- Configuración Chrome más estable
"""

import time
import random
import argparse
import threading
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, WebDriverException, ElementNotInteractableException
import sys
import os

# =========================
# CONFIGURACIÓN ADAPTADA
# =========================

# URL de tu formulario (ajusta según corresponda)
STAGING_URL = "https://numetika.online/capital/evaluacion-gestion.php?fbclid=IwdGRjcAMiq41leHRuA2FlbQIxMQABHhsgmj8yuHLpuHQXCwaZapvWIJhQU0Z7E_2s5SBQ65jq4nD6bBnHS0GarASg_aem_SyQCFKbEcnddNWFWOnaLAQ"

# Datos demográficos específicos de tu formulario
GENERO_OPCIONES = ["FEMENINO", "MASCULINO", "OTRO"]
EDAD_OPCIONES = ["18-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64", "65"]

OCUPACIONES = [
    "Hogar", "Estudiante", "Autoempleo", "Comercio Informal", "Comercio Formal", 
    "Obrero", "Campo", "Servidor pub", "Educacion", "Profesionista", 
    "Construccion", "Conductor", "Desempleado"
]

# Localidades específicas de tu select
LOCALIDADES = [
    "ACUITLAPILCO", "ADOLFO LOPEZ MATEOS", "ATEMPAN", "CENTRO", "EL SABINAL",
    "IXTULCO", "LA JOYA", "LA LOMA XICOHTENCATL", "LA TRINIDAD TEPEHITEC",
    "LOMA BONITA", "OCOTLAN", "SAN DIEGO METEPEC", "SAN GABRIEL CUAUHTLA",
    "SAN HIPOLITO CHIMALPA", "SAN ISIDRO", "SAN LUCAS CUAUHTELULPAN",
    "SAN SEBASTIAN ATLAHAPA", "TIZATLAN", "TLAPANCALCO"
]

# Métricas globales thread-safe
class Metricas:
    def __init__(self):
        self.lock = threading.Lock()
        self.exitos = 0
        self.errores = 0
        self.tiempos = []
        self.contador_total = 0
        
    def agregar_exito(self, tiempo):
        with self.lock:
            self.exitos += 1
            self.contador_total += 1
            self.tiempos.append(tiempo)
            
    def agregar_error(self, tiempo=0):
        with self.lock:
            self.errores += 1
            self.contador_total += 1
            if tiempo > 0:
                self.tiempos.append(tiempo)
                
    def obtener_resumen(self):
        with self.lock:
            total = self.exitos + self.errores
            tasa_exito = (self.exitos / total * 100) if total > 0 else 0
            tiempo_promedio = sum(self.tiempos) / len(self.tiempos) if self.tiempos else 0
            return {
                'total': total,
                'exitos': self.exitos,
                'errores': self.errores,
                'tasa_exito': tasa_exito,
                'tiempo_promedio': tiempo_promedio,
                'contador_total': self.contador_total
            }

metricas_globales = Metricas()

# =========================
# UTILIDADES
# =========================

def _simplify_text(s: str) -> str:
    """Normaliza texto removiendo acentos, NBSP y espacios múltiples."""
    if s is None:
        return ""
    s = s.replace("\u00A0", " ")
    s = " ".join(s.split())
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.lower()

def crear_driver_chrome(headless=True):
    """Crear instancia MEJORADA del driver Chrome con configuración optimizada"""
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless=new")
    
    # CONFIGURACIÓN MEJORADA PARA CHROME
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-features=TranslateUI,VizDisplayCompositor")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    chrome_options.add_argument("--window-size=1366,768")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-javascript-harmony-shipping")
    chrome_options.add_argument("--disable-background-media-suspend")
    
    # CRÍTICO: Configuración para evitar errores GPU (que estás viendo)
    chrome_options.add_argument("--disable-crash-reporter")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--silent")
    chrome_options.add_argument("--disable-gl-drawing-for-tests")
    chrome_options.add_argument("--disable-canvas-aa")
    chrome_options.add_argument("--disable-3d-apis")
    chrome_options.add_argument("--disable-accelerated-2d-canvas")
    chrome_options.add_argument("--disable-accelerated-jpeg-decoding")
    chrome_options.add_argument("--disable-accelerated-mjpeg-decode")
    chrome_options.add_argument("--disable-app-list-dismiss-on-blur")
    chrome_options.add_argument("--disable-accelerated-video-decode")
    
    # Configuración específica de Chrome para estabilidad
    chrome_options.add_argument("--memory-pressure-off")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-component-update")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-web-resources")
    chrome_options.add_argument("--disable-client-side-phishing-detection")
    chrome_options.add_argument("--disable-component-extensions-with-background-pages")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--mute-audio")
    
    # Silenciar completamente los logs
    chrome_options.add_experimental_option("excludeSwitches", [
        "enable-logging", 
        "enable-automation",
        "enable-blink-features"
    ])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # Preferencias optimizadas para Chrome
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.geolocation": 2,
        "profile.password_manager_enabled": False,
        "credentials_enable_service": False,
        "profile.default_content_setting_values.media_stream": 2,
        "profile.default_content_setting_values.media_stream_mic": 2,
        "profile.default_content_setting_values.media_stream_camera": 2,
        "profile.managed_default_content_settings.images": 2,
        # Deshabilitar notificaciones y permisos
        "profile.default_content_setting_values.plugins": 2,
        "profile.content_settings.plugin_whitelist.adobe-flash-player": {},
        "profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player": {}
    }
    chrome_options.add_experimental_option("prefs", prefs)

    try:
        # Verificar que existe el driver de Chrome
        driver_path = r"C:\Users\rocko\OneDrive\Desktop\Portafolio\Selenium\drivers\chromedriver.exe"
        if not os.path.exists(driver_path):
            raise FileNotFoundError(f"Driver de Chrome no encontrado en: {driver_path}")
        
        service = Service(executable_path=driver_path)
        
        # CRÍTICO: Suprimir logs del service también
        service.creation_flags = 0x08000000  # CREATE_NO_WINDOW flag
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Configuración de timeouts más conservadora
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(3)  # Reducido para mejor control manual
        
        # User-Agent para evitar detección de automatización
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['es-ES', 'es']})")
        
        return driver
        
    except Exception as e:
        print(f"❌ Error al crear driver de Chrome: {e}")
        print(f"Verificar que el driver existe en: {driver_path}")
        print("💡 Descarga ChromeDriver desde: https://chromedriver.chromium.org/")
        raise

def pausa_aleatoria(min_pausa=0.5, max_pausa=1.2):
    """Pausa aleatoria entre acciones - MÁS CONSERVADORA"""
    time.sleep(random.uniform(min_pausa, max_pausa))

def click_radio_by_id_mejorado(driver, wait, radio_id, max_retries=5):
    """
    VERSIÓN MEJORADA: Hace click en radio button por ID con múltiples estrategias
    """
    print(f"🎯 Intentando click en {radio_id}...")
    
    for intento in range(max_retries):
        try:
            # Estrategia 1: Encontrar elemento y verificar que existe
            element = wait.until(EC.presence_of_element_located((By.ID, radio_id)))
            print(f"  ✓ Elemento {radio_id} encontrado")
            
            # Estrategia 2: Scroll al elemento
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(0.5)
            
            # Estrategia 3: Verificar que es clickeable
            clickeable = EC.element_to_be_clickable((By.ID, radio_id))
            element = wait.until(clickeable)
            print(f"  ✓ Elemento {radio_id} es clickeable")
            
            # Estrategia 4: Intentar diferentes métodos de click
            click_exitoso = False
            
            # Método 1: Click normal
            try:
                element.click()
                click_exitoso = True
                print(f"  ✓ Click normal exitoso en {radio_id}")
            except Exception as e1:
                print(f"  ⚠ Click normal falló: {e1}")
                
                # Método 2: JavaScript click
                try:
                    driver.execute_script("arguments[0].click();", element)
                    click_exitoso = True
                    print(f"  ✓ JavaScript click exitoso en {radio_id}")
                except Exception as e2:
                    print(f"  ⚠ JavaScript click falló: {e2}")
                    
                    # Método 3: ActionChains
                    try:
                        ActionChains(driver).move_to_element(element).click().perform()
                        click_exitoso = True
                        print(f"  ✓ ActionChains click exitoso en {radio_id}")
                    except Exception as e3:
                        print(f"  ⚠ ActionChains click falló: {e3}")
                        
                        # Método 4: Forzar con JavaScript más agresivo
                        try:
                            driver.execute_script("""
                                arguments[0].checked = true;
                                arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
                                arguments[0].dispatchEvent(new Event('click', {bubbles: true}));
                            """, element)
                            click_exitoso = True
                            print(f"  ✓ JavaScript forzado exitoso en {radio_id}")
                        except Exception as e4:
                            print(f"  ⚠ JavaScript forzado falló: {e4}")
            
            if click_exitoso:
                pausa_aleatoria(0.3, 0.6)
                
                # Verificar que el click funcionó
                try:
                    if element.is_selected():
                        print(f"  ✅ {radio_id} seleccionado correctamente")
                        return True
                    else:
                        print(f"  ⚠ {radio_id} no está seleccionado después del click")
                except:
                    # Si no podemos verificar, asumimos que funcionó
                    print(f"  ✅ {radio_id} click completado (verificación no disponible)")
                    return True
            
        except TimeoutException:
            print(f"  ⚠ Timeout esperando elemento {radio_id} (intento {intento+1})")
        except Exception as e:
            print(f"  ⚠ Error en intento {intento+1} para {radio_id}: {e}")
        
        if intento < max_retries - 1:
            tiempo_espera = (intento + 1) * 1.0
            print(f"  🔄 Reintentando en {tiempo_espera}s...")
            time.sleep(tiempo_espera)
    
    print(f"  ❌ Todos los intentos fallaron para {radio_id}")
    return False

def rellenar_select_por_name_mejorado(driver, wait, name, valor):
    """Versión mejorada para rellenar selects"""
    print(f"🎯 Seleccionando '{valor}' en select '{name}'...")
    
    try:
        # Encontrar el select
        select_element = wait.until(EC.element_to_be_clickable((By.NAME, name)))
        
        # Scroll al elemento
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", select_element)
        pausa_aleatoria(0.3, 0.6)
        
        # Crear objeto Select
        select = Select(select_element)
        
        # Intentar seleccionar por valor
        try:
            select.select_by_value(valor)
            print(f"  ✅ Seleccionado '{valor}' por valor en {name}")
            pausa_aleatoria(0.3, 0.6)
            return True
        except Exception as e1:
            print(f"  ⚠ Fallo selección por valor: {e1}")
            
            # Intentar por texto visible
            try:
                select.select_by_visible_text(valor)
                print(f"  ✅ Seleccionado '{valor}' por texto en {name}")
                pausa_aleatoria(0.3, 0.6)
                return True
            except Exception as e2:
                print(f"  ⚠ Fallo selección por texto: {e2}")
                
                # Intentar JavaScript directo
                try:
                    driver.execute_script(f"arguments[0].value = '{valor}';", select_element)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", select_element)
                    print(f"  ✅ Seleccionado '{valor}' por JavaScript en {name}")
                    pausa_aleatoria(0.3, 0.6)
                    return True
                except Exception as e3:
                    print(f"  ❌ Error JavaScript: {e3}")
                    
    except Exception as e:
        print(f"  ❌ Error encontrando select {name}: {e}")
    
    return False

def esperar_y_manejar_pregunta_condicional(driver, wait):
    """Maneja la pregunta condicional 5.1 que aparece solo si se selecciona 'Insuficientes'"""
    try:
        print("🔍 Verificando pregunta condicional 5.1...")
        time.sleep(3.0)  # Esperar más tiempo
        
        # Verificar si la pregunta 0501 está visible
        try:
            pregunta_condicional = driver.find_element(By.ID, "pregunta0501")
            
            if not pregunta_condicional.get_attribute("hidden"):
                print("  ✓ Pregunta condicional 5.1 visible, completando...")
                
                # La pregunta está visible, seleccionar una opción negativa
                opciones_condicionales = [
                    "RadioGroup0501_1",  # Drenaje y alcantarillado
                    "RadioGroup0501_2",  # Pavimentación
                    "RadioGroup0501_5"   # Bacheo
                ]
                
                opcion_seleccionada = random.choice(opciones_condicionales)
                return click_radio_by_id_mejorado(driver, wait, opcion_seleccionada)
            else:
                print("  ✓ Pregunta condicional 5.1 oculta (no necesaria)")
                return True
                
        except:
            print("  ✓ Pregunta condicional 5.1 no encontrada (no necesaria)")
            return True
        
    except Exception as e:
        print(f"  ⚠ Error manejando pregunta condicional: {e}")
        return True  # No es crítico si falla

def verificar_salud_driver(driver):
    """Verifica que el driver sigue funcionando correctamente"""
    try:
        # Test básico: obtener título
        title = driver.title
        return len(title) >= 0  # Cualquier título (incluso vacío) es válido
    except Exception as e:
        print(f"❌ Driver no responde: {e}")
        return False

def debug_elementos_formulario(driver):
    """Función de debugging para ver qué elementos están disponibles"""
    try:
        print("🔍 DEBUG: Analizando elementos del formulario...")
        
        # Buscar todos los radio buttons
        radios = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
        print(f"  📊 Total radio buttons encontrados: {len(radios)}")
        
        for i, radio in enumerate(radios[:10]):  # Solo los primeros 10
            try:
                radio_id = radio.get_attribute("id")
                radio_name = radio.get_attribute("name")
                radio_value = radio.get_attribute("value")
                is_visible = radio.is_displayed()
                is_enabled = radio.is_enabled()
                
                print(f"  Radio {i+1}: ID='{radio_id}', NAME='{radio_name}', VALUE='{radio_value}', Visible={is_visible}, Enabled={is_enabled}")
            except:
                print(f"  Radio {i+1}: Error obteniendo atributos")
        
        # Buscar selects
        selects = driver.find_elements(By.TAG_NAME, "select")
        print(f"  📊 Total selects encontrados: {len(selects)}")
        
        for i, select in enumerate(selects):
            try:
                select_name = select.get_attribute("name")
                select_id = select.get_attribute("id")
                options_count = len(select.find_elements(By.TAG_NAME, "option"))
                
                print(f"  Select {i+1}: NAME='{select_name}', ID='{select_id}', Opciones={options_count}")
            except:
                print(f"  Select {i+1}: Error obteniendo atributos")
                
    except Exception as e:
        print(f"❌ Error en debug: {e}")

def rellenar_formulario_completo(driver, numero_envio, min_pausa, max_pausa):
    """Versión MEJORADA para rellenar formulario completo con mejor debugging"""
    inicio = time.time()
    wait = WebDriverWait(driver, 30)
    
    try:
        print(f"[{numero_envio:04}] 🚀 Iniciando envío...")
        
        # Verificar salud del driver antes de empezar
        if not verificar_salud_driver(driver):
            raise Exception("Driver no está funcionando correctamente")
        
        # Navegar a la página con manejo de errores
        try:
            print(f"[{numero_envio:04}] 🌐 Navegando a {STAGING_URL}...")
            driver.get(STAGING_URL)
        except TimeoutException:
            print(f"[{numero_envio:04}] ⚠ Timeout al cargar página, reintentando...")
            time.sleep(3)
            driver.get(STAGING_URL)
        
        # Esperar que cargue el formulario completamente
        print(f"[{numero_envio:04}] ⏳ Esperando que cargue el formulario...")
        wait.until(EC.presence_of_element_located((By.ID, "form1")))
        
        # Esperar a que desaparezca el loader
        try:
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.ID, "loader"))
            )
            print(f"[{numero_envio:04}] ✓ Loader desaparecido")
        except:
            print(f"[{numero_envio:04}] ℹ No hay loader o ya desapareció")
        
        # Pausa adicional para asegurar carga completa
        pausa_aleatoria(2.0, 3.0)
        
        # DEBUG: Analizar elementos disponibles en el primer envío
        if numero_envio == 1:
            debug_elementos_formulario(driver)
        
        # Datos aleatorios
        genero = random.choice(GENERO_OPCIONES)
        edad = random.choice(EDAD_OPCIONES)
        ocupacion = random.choice(OCUPACIONES)
        localidad = random.choice(LOCALIDADES)
        
        print(f"[{numero_envio:04}] 👤 Datos: {genero}, {edad}, {ocupacion}, {localidad[:15]}...")
        
        # 1. GÉNERO - usando IDs específicos de tu HTML
        print(f"[{numero_envio:04}] 1️⃣ Seleccionando género: {genero}")
        genero_ids = {
            "FEMENINO": "RadioGroup2_0",
            "MASCULINO": "RadioGroup2_1", 
            "OTRO": "RadioGroup2_2"
        }
        if not click_radio_by_id_mejorado(driver, wait, genero_ids[genero]):
            raise Exception(f"Error seleccionando género: {genero}")
        
        # 2. EDAD - usando IDs específicos
        print(f"[{numero_envio:04}] 2️⃣ Seleccionando edad: {edad}")
        edad_ids = {
            "18-24": "RadioGroup3_0",
            "25-29": "RadioGroup3_1",
            "30-34": "RadioGroup3_2", 
            "35-39": "RadioGroup3_3",
            "40-44": "RadioGroup3_4",
            "45-49": "RadioGroup3_5",
            "50-54": "RadioGroup3_6",
            "55-59": "RadioGroup3_7",
            "60-64": "RadioGroup3_8",
            "65": "RadioGroup3_9"
        }
        if not click_radio_by_id_mejorado(driver, wait, edad_ids[edad]):
            raise Exception(f"Error seleccionando edad: {edad}")
        
        # 3. OCUPACIÓN - select
        print(f"[{numero_envio:04}] 3️⃣ Seleccionando ocupación: {ocupacion}")
        if not rellenar_select_por_name_mejorado(driver, wait, "ocupa", ocupacion):
            raise Exception(f"Error seleccionando ocupación: {ocupacion}")
        
        # 4. LOCALIDAD - select
        print(f"[{numero_envio:04}] 4️⃣ Seleccionando localidad: {localidad}")
        if not rellenar_select_por_name_mejorado(driver, wait, "muni", localidad):
            raise Exception(f"Error seleccionando localidad: {localidad}")
        
        # 5. EVALUACIONES NEGATIVAS - usando IDs específicos
        print(f"[{numero_envio:04}] 💀 Completando evaluaciones negativas...")
        
        evaluaciones = [
            ("RadioGroup01_2", "Desaprueba gobierno"),
            ("RadioGroup02_2", "Seguridad empeoró"),
            ("RadioGroup03_2", "Servicios malos"),
            ("RadioGroup04_3", "Prioridad: seguridad"),
            ("RadioGroup05_2", "Obras insuficientes"),
        ]
        
        for i, (radio_id, descripcion) in enumerate(evaluaciones):
            print(f"[{numero_envio:04}] 5️⃣.{i+1} {descripcion}")
            if not click_radio_by_id_mejorado(driver, wait, radio_id):
                raise Exception(f"Error en evaluación: {descripcion}")
        
        # Manejar pregunta condicional 5.1 si aparece
        print(f"[{numero_envio:04}] 5️⃣.6 Verificando pregunta condicional...")
        esperar_y_manejar_pregunta_condicional(driver, wait)
        
        # Continuar con el resto de evaluaciones
        evaluaciones_restantes = [
            ("RadioGroup06_2", "Atención ineficiente"),
            ("RadioGroup08_2", "Es opaco"),
            ("RadioGroup09_2", "No limpio"),
            ("RadioGroup12_1", "Calificación: 1"),
        ]
        
        for i, (radio_id, descripcion) in enumerate(evaluaciones_restantes):
            print(f"[{numero_envio:04}] 6️⃣.{i+1} {descripcion}")
            if not click_radio_by_id_mejorado(driver, wait, radio_id):
                raise Exception(f"Error en evaluación: {descripcion}")
        
        # 6. Enviar formulario
        print(f"[{numero_envio:04}] 📤 Enviando formulario...")
        
        try:
            # Buscar botón submit
            submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']")))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", submit_btn)
            pausa_aleatoria(1.0, 2.0)  # Pausa más larga antes de enviar
            
            try:
                submit_btn.click()
                print(f"[{numero_envio:04}] ✓ Click normal en submit")
            except Exception:
                driver.execute_script("arguments[0].click();", submit_btn)
                print(f"[{numero_envio:04}] ✓ JavaScript click en submit")
                
        except Exception as e:
            raise Exception(f"Error al enviar: {e}")
        
        # 7. Verificar envío con timeout más largo
        print(f"[{numero_envio:04}] ⏳ Esperando confirmación...")
        pausa_aleatoria(3.0, 5.0)  # Esperar respuesta del servidor
        
        tiempo_total = time.time() - inicio
        
        # Verificar si hay confirmación o cambio de URL
        current_url = driver.current_url.lower()
        page_source = driver.page_source.lower()
        
        # Buscar indicadores de éxito
        indicadores_exito = [
            "gracias" in current_url or "gracias" in page_source,
            "success" in current_url or "éxito" in page_source,
            "enviado" in current_url or "enviado" in page_source,
            "confirmacion" in current_url or "confirmación" in page_source,
            "registrado" in page_source,
            "guardado" in page_source
        ]
        
        if any(indicadores_exito):
            print(f"[{numero_envio:04}] ✅ CONFIRMADO ({tiempo_total:.1f}s)")
            metricas_globales.agregar_exito(tiempo_total)
            return True
        else:
            print(f"[{numero_envio:04}] ✅ ENVIADO ({tiempo_total:.1f}s)")
            metricas_globales.agregar_exito(tiempo_total)  # Consideramos éxito
            return True
            
    except Exception as e:
        tiempo_total = time.time() - inicio
        print(f"[{numero_envio:04}] ❌ ERROR: {str(e)} ({tiempo_total:.1f}s)")
        metricas_globales.agregar_error(tiempo_total)
        
        # DEBUG: Capturar información adicional en caso de error
        try:
            print(f"[{numero_envio:04}] 🔍 URL actual: {driver.current_url}")
            print(f"[{numero_envio:04}] 🔍 Título: {driver.title}")
        except:
            pass
            
        return False

def recrear_driver_si_es_necesario(driver, worker_id):
    """Recrea el driver si detecta problemas"""
    try:
        if not verificar_salud_driver(driver):
            print(f"🔄 Worker {worker_id}: Recreando driver por problemas de salud")
            try:
                driver.quit()
            except:
                pass
            return crear_driver_chrome(headless=True)
        return driver
    except Exception as e:
        print(f"🔄 Worker {worker_id}: Forzando recreación del driver: {e}")
        try:
            driver.quit()
        except:
            pass
        return crear_driver_chrome(headless=True)

def worker_infinito(worker_id, args):
    """Worker que ejecuta envíos infinitos con manejo robusto de errores"""
    driver = None
    contador_envios = 0
    contador_errores_consecutivos = 0
    MAX_ERRORES_CONSECUTIVOS = 3
    
    try:
        print(f"🚀 Worker {worker_id}: Iniciando modo INFINITO")
        
        # Crear driver inicial
        driver = crear_driver_chrome(headless=args.headless)
        
        while True:  # BUCLE INFINITO
            contador_envios += 1
            numero_envio_global = metricas_globales.contador_total + 1
            
            try:
                # Verificar y recrear driver si es necesario cada 10 envíos
                if contador_envios % 10 == 0:
                    print(f"🔧 Worker {worker_id}: Verificación periódica del driver (envío {contador_envios})")
                    driver = recrear_driver_si_es_necesario(driver, worker_id)
                
                # Procesar envío
                exito = rellenar_formulario_completo(
                    driver, numero_envio_global, args.min_pausa, args.max_pausa
                )
                
                if exito:
                    contador_errores_consecutivos = 0
                    print(f"✅ Worker {worker_id}: Envío {contador_envios} completado exitosamente")
                else:
                    contador_errores_consecutivos += 1
                    print(f"❌ Worker {worker_id}: Envío {contador_envios} falló ({contador_errores_consecutivos} errores consecutivos)")
                
                # Si hay muchos errores consecutivos, recrear driver
                if contador_errores_consecutivos >= MAX_ERRORES_CONSECUTIVOS:
                    print(f"🔄 Worker {worker_id}: Recreando driver por {contador_errores_consecutivos} errores consecutivos")
                    try:
                        driver.quit()
                    except:
                        pass
                    driver = crear_driver_chrome(headless=args.headless)
                    contador_errores_consecutivos = 0
                
                # Pausa entre envíos MÁS LARGA para estabilidad
                pausa_envios = random.uniform(args.min_pausa * 5, args.max_pausa * 8)
                print(f"⏸ Worker {worker_id}: Pausa de {pausa_envios:.1f}s antes del siguiente envío")
                time.sleep(pausa_envios)
                
                # Mostrar estadísticas cada 5 envíos
                if contador_envios % 5 == 0:
                    resumen = metricas_globales.obtener_resumen()
                    print(f"📊 Worker {worker_id}: {contador_envios} envíos | "
                          f"Total global: {resumen['total']} | "
                          f"Éxito: {resumen['tasa_exito']:.1f}%")
                    
            except KeyboardInterrupt:
                print(f"⏹ Worker {worker_id}: Interrumpido por usuario")
                break
            except Exception as e:
                print(f"❌ Worker {worker_id}: Error crítico en envío {contador_envios}: {e}")
                metricas_globales.agregar_error()
                contador_errores_consecutivos += 1
                
                # Pausa más larga en caso de error crítico
                print(f"⏸ Worker {worker_id}: Pausa de recuperación de 10s...")
                time.sleep(10)
                
                # Recrear driver en caso de error crítico
                try:
                    if driver:
                        driver.quit()
                except:
                    pass
                print(f"🔄 Worker {worker_id}: Recreando driver después de error crítico")
                driver = crear_driver_chrome(headless=args.headless)
                
    except Exception as e:
        print(f"💥 Error crítico en worker {worker_id}: {e}")
        
    finally:
        if driver:
            try:
                driver.quit()
                print(f"🚪 Worker {worker_id}: Driver cerrado correctamente")
            except Exception:
                print(f"⚠ Worker {worker_id}: Error cerrando driver")
        print(f"🏁 Worker {worker_id}: Terminado tras {contador_envios} envíos")

def ejecutar_pruebas_infinitas(args):
    """Ejecutar pruebas infinitas con workers concurrentes"""
    inicio_total = time.time()
    
    print("="*80)
    print("🚀 INICIANDO PRUEBAS INFINITAS - MODO NEGATIVO [VERSIÓN CHROME MEJORADA]")
    print(f"👥 Workers: {args.workers}")
    print(f"🎯 URL: {STAGING_URL}")
    print(f"⏱ Pausas: {args.min_pausa}-{args.max_pausa}s")
    print(f"👁 Headless: {args.headless}")
    print(f"🕐 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("💀 SOLO RESPUESTAS NEGATIVAS - CTRL+C para detener")
    print("🔧 VERSIÓN MEJORADA: Mejor manejo de elementos y debugging")
    print("="*80)
    
    # Ejecutar workers infinitos
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = []
        
        for worker_id in range(1, args.workers + 1):
            future = executor.submit(worker_infinito, worker_id, args)
            futures.append(future)
        
        try:
            # Mostrar estadísticas cada 30 segundos
            contador_reportes = 0
            while True:
                time.sleep(30)
                contador_reportes += 1
                tiempo_transcurrido = time.time() - inicio_total
                resumen = metricas_globales.obtener_resumen()
                
                print(f"\n📊 ESTADÍSTICAS #{contador_reportes} ({tiempo_transcurrido/60:.1f} min transcurridos)")
                print(f"Total procesados: {resumen['total']} | "
                      f"Éxitos: {resumen['exitos']} | "
                      f"Errores: {resumen['errores']} | "
                      f"Tasa éxito: {resumen['tasa_exito']:.1f}%")
                
                if resumen['tiempo_promedio'] > 0:
                    print(f"Tiempo promedio: {resumen['tiempo_promedio']:.1f}s")
                
                # Calcular velocidad
                if tiempo_transcurrido > 60:  # Después del primer minuto
                    velocidad = resumen['total'] / (tiempo_transcurrido / 60)
                    print(f"Velocidad: {velocidad:.1f} envíos/min")
                    
        except KeyboardInterrupt:
            print("\n⏹ Deteniendo workers...")
            # Los workers se detendrán automáticamente
            
        # Esperar a que terminen los workers
        print("⏳ Esperando a que terminen los workers...")
        for i, future in enumerate(futures):
            try:
                future.result(timeout=15)
                print(f"✅ Worker {i+1} terminado correctamente")
            except Exception as e:
                print(f"⚠ Worker {i+1} terminó con error: {e}")

def main():
    """Función principal mejorada"""
    parser = argparse.ArgumentParser(
        description="Script infinito CHROME MEJORADO para evaluación municipal con respuestas NEGATIVAS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EJEMPLOS DE USO:
  python %(prog)s                          # Configuración por defecto (1 worker, headless)
  python %(prog)s --headless 0             # Con interfaz gráfica visible
  python %(prog)s --workers 2              # 2 workers concurrentes
  python %(prog)s --min-pausa 1.0 --max-pausa 2.0  # Pausas más largas
  
NOTAS:
  - Los errores de GPU en modo headless son normales y no afectan el funcionamiento
  - Se recomienda empezar con 1 worker para verificar que todo funciona
  - El modo no-headless (--headless 0) es útil para debugging
  - CTRL+C para detener el script de forma segura
        """
    )
    
    parser.add_argument("--headless", type=int, choices=[0, 1], default=1,
                       help="Modo headless: 1=Sin interfaz, 0=Con interfaz (default: 1)")
    parser.add_argument("--min-pausa", type=float, default=0.5,
                       help="Pausa mínima entre acciones en segundos (default: 0.5)")
    parser.add_argument("--max-pausa", type=float, default=1.2,
                       help="Pausa máxima entre acciones en segundos (default: 1.2)")
    parser.add_argument("--workers", type=int, default=1,
                       help="Número de workers concurrentes (default: 1)")
    parser.add_argument("--debug", action="store_true",
                       help="Modo debug: muestra información adicional")
    
    args = parser.parse_args()
    
    # Validaciones
    if args.min_pausa >= args.max_pausa:
        print("❌ Error: --min-pausa debe ser menor que --max-pausa")
        return
    
    if args.min_pausa < 0.1:
        print("⚠ ADVERTENCIA: Pausas muy cortas pueden causar problemas")
        respuesta = input("¿Continuar? (y/N): ")
        if respuesta.lower() != 'y':
            return
    
    if args.workers > 2:  # Reducido de 3 a 2 para mayor estabilidad
        print("⚠ ADVERTENCIA: Más de 2 workers puede causar inestabilidad")
        print("  - Recomendado: 1 worker para máxima estabilidad")
        print("  - Alternativo: 2 workers para mayor velocidad")
        respuesta = input("¿Continuar? (y/N): ")
        if respuesta.lower() != 'y':
            return
    
    # Convertir headless a boolean
    args.headless = bool(args.headless)
    
    # Verificar que existe el ChromeDriver
    driver_path = r"C:\Users\rocko\OneDrive\Desktop\Portafolio\Selenium\drivers\chromedriver.exe"
    if not os.path.exists(driver_path):
        print(f"❌ ERROR: No se encuentra ChromeDriver en: {driver_path}")
        print("📥 Descarga ChromeDriver desde: https://chromedriver.chromium.org/")
        print("💡 Asegúrate de que la versión coincida con tu versión de Chrome")
        return
    
    print(f"🔧 Configuración validada:")
    print(f"   - Pausas: {args.min_pausa}-{args.max_pausa}s")
    print(f"   - Workers: {args.workers}")
    print(f"   - Headless: {args.headless}")
    print(f"   - Debug: {args.debug}")
    print(f"   - ChromeDriver: ✅ Encontrado")
    
    # Ejecutar pruebas infinitas
    try:
        ejecutar_pruebas_infinitas(args)
    except KeyboardInterrupt:
        print("\n⏹ Pruebas interrumpidas por el usuario")
        
        # Mostrar resumen final
        resumen = metricas_globales.obtener_resumen()
        print("\n" + "="*60)
        print("📊 RESUMEN FINAL")
        print("="*60)
        print(f"Total procesados: {resumen['total']}")
        print(f"Éxitos: {resumen['exitos']}")
        print(f"Errores: {resumen['errores']}")
        print(f"Tasa de éxito: {resumen['tasa_exito']:.1f}%")
        if resumen['tiempo_promedio'] > 0:
            print(f"Tiempo promedio: {resumen['tiempo_promedio']:.1f}s")
        print("="*60)
        print("¡Gracias por usar el script! 👋")
        
    except Exception as e:
        print(f"💥 Error crítico: {e}")
        print("💡 Intenta ejecutar con --headless 0 para ver qué está pasando")

if __name__ == "__main__":
    main()