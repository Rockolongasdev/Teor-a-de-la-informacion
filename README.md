# Gustavo Ivan Meraz Sanchez
# Prueba de Selenium para Obtener el Precio de Bitcoin de Binance

## ¿Qué es Selenium?

[Selenium](https://www.selenium.dev/) es una herramienta de automatización de navegadores web que permite interactuar con páginas web de manera programática. A través de Selenium, es posible automatizar tareas como la navegación por sitios web, la interacción con formularios, la captura de información de páginas web dinámicas, y mucho más. En este caso, estamos utilizando Selenium para extraer el precio actual de Bitcoin desde Binance sin la necesidad de iniciar sesión.

Selenium se utiliza comúnmente para la automatización de pruebas de aplicaciones web, pero también se puede aplicar en la recopilación de datos de sitios web dinámicos, donde otras herramientas de scraping tradicionales no funcionan debido a la necesidad de interactuar con JavaScript y otros componentes dinámicos.

## ¿Cómo funciona en este código?

Este script de Python usa Selenium para obtener el precio actual de Bitcoin en Binance mediante la automatización del navegador. Aquí se describen los pasos clave que realiza:

1. **Configuración del Navegador:**
   - Se configura Selenium para usar el navegador Microsoft Edge mediante el controlador `msedgedriver.exe`.
   - Opciones como `--headless` permiten ejecutar el navegador sin interfaz gráfica, pero en este caso está comentada para que se vea el navegador durante la ejecución.

2. **Navegar a la Página de Binance:**
   - El script abre la página de trading de Bitcoin de Binance: [https://www.binance.com/es/trade/BTC_USDT](https://www.binance.com/es/trade/BTC_USDT).
   - Usa Selenium para cargar la página y esperar a que los elementos necesarios estén disponibles.

3. **Esperar y Buscar el Precio:**
   - Utiliza WebDriverWait para esperar hasta que los elementos con el precio de Bitcoin estén presentes.
   - Se buscan varios selectores CSS que podrían contener el precio en la página. Si no se encuentra el precio con estos selectores, se hace una búsqueda alternativa por texto que contenga símbolos como el dólar `$` o la criptomoneda `USDT`.

4. **Extracción y Verificación:**
   - Una vez encontrado el precio, se verifica que el texto contiene un valor numérico válido.
   - Si se encuentra un precio válido, se imprime en la consola y se guarda una captura de pantalla del navegador.

5. **Captura de Pantalla y Depuración:**
   - Si no se puede encontrar el precio, el script guarda una captura de pantalla para la depuración y muestra mensajes de error con posibles causas (como cambios en la estructura de la página o problemas de conectividad).

6. **Cierre del Navegador:**
   - Al finalizar el proceso, se cierra el navegador de manera ordenada.

Este proceso de automatización es útil para obtener datos en tiempo real desde sitios web que requieren interacción dinámica, como es el caso de la cotización de criptomonedas en Binance.

## Requisitos

Para ejecutar este script, necesitarás:

- **Python 3.x**
- **Selenium**: Se puede instalar mediante `pip install selenium`.
- **WebDriver de Microsoft Edge**: Asegúrate de tener el [Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/) instalado en tu sistema.
- **Red activa**: El script necesita acceder a la página web de Binance, por lo que debes asegurarte de tener acceso a internet.

## Ejecución

Para ejecutar el script, simplemente corre el siguiente comando:

```bash
python prueba_binance_bitcoin.py
