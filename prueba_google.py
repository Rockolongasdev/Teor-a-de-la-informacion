#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prueba de Selenium para obtener el precio de Bitcoin de Binance sin iniciar sesión
Archivo: prueba_binance_bitcoin.py
"""

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re

def obtener_precio_bitcoin():
    """
    Función para obtener el precio actual de Bitcoin desde Binance
    """
    # Configuración del driver de Edge
    driver_path = r"C:\xampp\htdocs\Teor-a-de-la-informacion\msedgedriver.exe"
    service = Service(driver_path)
    
    # Opciones para el navegador
    options = webdriver.EdgeOptions()
    # Opcional: ejecutar en modo headless (sin ventana del navegador)
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    driver = None
    
    try:
        # Inicializar el driver
        driver = webdriver.Edge(service=service, options=options)
        print("Driver de Edge iniciado correctamente")
        
        # Navegar a la página de Bitcoin en Binance
        url = "https://www.binance.com/es/trade/BTC_USDT"
        print(f"Navegando a: {url}")
        driver.get(url)
        
        # Esperar a que la página cargue
        wait = WebDriverWait(driver, 15)
        
        # Intentar diferentes selectores para encontrar el precio
        selectores_precio = [
            # Selector principal del precio en la página de trading
            "[data-testid='price-display']",
            ".showPrice",
            "[class*='price']",
            "[class*='Price']",
            # Selectores más específicos
            ".css-1ej4hfo",
            ".css-vurnku",
            # Selectores generales como backup
            "[data-qa='price']",
            "[data-price]"
        ]
        
        precio_encontrado = None
        selector_usado = None
        
        # Intentar encontrar el precio con diferentes selectores
        for selector in selectores_precio:
            try:
                print(f"Intentando selector: {selector}")
                elemento_precio = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                precio_texto = elemento_precio.text.strip()
                
                # Verificar que el texto contiene un precio válido
                if precio_texto and re.search(r'\d+[.,]\d+', precio_texto):
                    precio_encontrado = precio_texto
                    selector_usado = selector
                    print(f"✓ Precio encontrado con selector {selector}: {precio_encontrado}")
                    break
                    
            except (TimeoutException, NoSuchElementException):
                print(f"✗ No se encontró elemento con selector: {selector}")
                continue
        
        # Si no se encontró con los selectores específicos, intentar una búsqueda más amplia
        if not precio_encontrado:
            print("Intentando búsqueda alternativa...")
            try:
                # Buscar elementos que contengan texto con formato de precio
                elementos = driver.find_elements(By.XPATH, "//*[contains(text(), '$') or contains(text(), 'USDT')]")
                
                for elemento in elementos:
                    texto = elemento.text.strip()
                    # Buscar patrones de precio (números con decimales)
                    if re.search(r'\$?\d{1,3}[.,]\d{3}[.,]?\d*|\d{1,6}[.,]\d{2,8}', texto):
                        precio_encontrado = texto
                        selector_usado = "búsqueda por texto"
                        print(f"✓ Precio encontrado por búsqueda alternativa: {precio_encontrado}")
                        break
                        
            except Exception as e:
                print(f"Error en búsqueda alternativa: {e}")
        
        # Resultados
        if precio_encontrado:
            print(f"\n{'='*50}")
            print(f"PRECIO DE BITCOIN OBTENIDO EXITOSAMENTE")
            print(f"{'='*50}")
            print(f"Precio: {precio_encontrado}")
            print(f"Selector usado: {selector_usado}")
            print(f"Fecha/Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*50}")
            
            # Opcional: tomar screenshot
            screenshot_path = r"C:\xampp\htdocs\Teor-a-de-la-informacion\precio_bitcoin_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot guardado en: {screenshot_path}")
            
        else:
            print(f"\n{'='*50}")
            print(f"NO SE PUDO OBTENER EL PRECIO")
            print(f"{'='*50}")
            print("Posibles causas:")
            print("- Cambios en la estructura de la página")
            print("- Problemas de conectividad")
            print("- Elementos que requieren más tiempo para cargar")
            
            # Tomar screenshot para debug
            debug_screenshot = r"C:\xampp\htdocs\Teor-a-de-la-informacion\debug_binance.png"
            driver.save_screenshot(debug_screenshot)
            print(f"Screenshot de debug guardado en: {debug_screenshot}")
        
        # Pausa para ver el resultado (opcional)
        time.sleep(3)
        
    except TimeoutException:
        print("Error: Timeout - La página tardó demasiado en cargar")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        # Cerrar el navegador
        if driver:
            driver.quit()
            print("Driver cerrado correctamente")

def main():
    """
    Función principal
    """
    print("="*60)
    print("PRUEBA DE SELENIUM - PRECIO BITCOIN BINANCE")
    print("="*60)
    print("Iniciando prueba...")
    
    obtener_precio_bitcoin()
    
    print("\nPrueba completada.")
    print("="*60)

if __name__ == "__main__":
    main()