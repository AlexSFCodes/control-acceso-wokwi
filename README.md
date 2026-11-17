# Control de acceso con Arduino UNO y Wokwi

Proyecto en línea: https://wokwi.com/projects/480894635131400193

Python analiza una foto con OpenCV (Haar Cascade y un respaldo YuNet para caras que Haar no detecta), envía `1` si detecta algún rostro o `0` si no detecta ninguno y espera la confirmación del Arduino. El UNO controla dos LED: verde en el pin 8 y rojo en el pin 9, cada uno con una resistencia de 220 ohmios.

Esta demostración detecta presencia de rostros. No reconoce la identidad de una persona ni comprueba si está autorizada.

## 1. Probar el circuito en la web

1. Abre el enlace del proyecto y pulsa el botón verde de iniciar simulación.
2. En el campo del monitor serial, debajo del circuito, escribe `1` y pulsa Enter.
   Se enciende el verde y aparece `acceso correcto`.
3. Escribe `0` y pulsa Enter. Se enciende el rojo y aparece `acceso denegado`.

Al comenzar, ambos LED están apagados. Los saltos de línea y otros caracteres se ignoran. La velocidad serial del programa es de 115200 baudios.

La aplicación de Python se ejecuta en Windows. La dirección `rfc2217://localhost:4000` corresponde al simulador de Wokwi **en VS Code**, no al proyecto abierto en la página web.

## 2. Analizar fotos en Windows

La primera vez que uses el proyecto, ejecuta `instalar.cmd` para preparar un entorno de Python dentro de `.venv`. Si ya está preparado, puedes abrir directamente `iniciar.cmd`.

1. Haz doble clic en `iniciar.cmd` desde el Explorador de archivos. La versión corregida muestra `v2` en el título. Si tenías la aplicación abierta, ciérrala y vuelve a abrirla para cargar la actualización.
2. Para probar únicamente el reconocimiento de rostros, marca **Solo analizar la foto**.
3. Pulsa **Cargar y analizar foto** y selecciona una foto frontal bien iluminada.
4. Prueba también con una imagen de un paisaje u objeto. Los recuadros verdes indican las caras detectadas.

Si copias el proyecto a otro equipo o extraes el ZIP, instala Python y ejecuta primero `instalar.cmd`. Ese archivo descarga OpenCV, NumPy, Pillow y PySerial en un entorno propio del proyecto. Después abre `iniciar.cmd`.

Desde PowerShell, dentro de la carpeta del proyecto, ejecuta `.\iniciar.cmd`. No pegues el contenido del archivo CMD como comandos de PowerShell.

## 3. Python conectado automáticamente a Wokwi

1. Haz doble clic en `control_acceso.code-workspace` para abrir la carpeta correcta en VS Code. También puedes abrir la carpeta `control_acceso_wokwi` como carpeta raíz; abrir únicamente su carpeta padre `Arduino` no selecciona esta configuración.
2. Usa la extensión **Wokwi Simulator** (ya instalada en este equipo). Si solicita una licencia, sigue su proceso de activación; no se compró ni activó un plan durante la preparación del proyecto.
3. Pulsa F1 y ejecuta **Wokwi: Start Simulator**.
4. Mantén el simulador visible. Los archivos de firmware ya compilados están incluidos en `build/` y `wokwi.toml` apunta a ellos.
5. Abre `iniciar.cmd`, desmarca **Solo analizar la foto** y deja el puerto `rfc2217://localhost:4000`.
6. Carga una foto. La aplicación mostrará el resultado y el mensaje de confirmación del Arduino.

La conexión automática de Python con VS Code está configurada; la prueba realizada aquí fue la simulación web. La activación de la extensión depende de tu cuenta de Wokwi.

Si modificas el `.ino`, vuelve a compilar antes de usar la simulación local. Puedes ejecutar `compilar.ps1` desde PowerShell, o usar **Programa > Exportar binarios compilados** en Arduino IDE y copiar el archivo HEX generado a `build/control_acceso_wokwi.ino.hex`. Si usas esta última opción, elimina la línea `elf` de `wokwi.toml` para que no apunte a un ELF anterior.

## 4. Usar tu Arduino IDE y una placa física

1. Abre `control_acceso_wokwi.ino` en Arduino IDE.
2. Selecciona **Arduino Uno**, el puerto de la placa y pulsa **Subir**.
3. Conecta D8 a una resistencia de 220 ohmios y de esta al ánodo del LED verde.
4. Conecta D9 a otra resistencia de 220 ohmios y de esta al ánodo del LED rojo.
5. Conecta los dos cátodos a GND. El cátodo suele ser la pata corta y el lado plano del encapsulado.
6. Cierra el monitor serial del IDE, abre `iniciar.cmd` y selecciona el COM de tu placa.

Tener Arduino IDE instalado no implica que haya una placa conectada. No se ha cargado ningún programa a hardware físico.

## Archivos

| Archivo | Uso |
| --- | --- |
| `control_acceso_wokwi.ino` | Programa para Arduino IDE y el simulador |
| `diagram.json` | Circuito y conexiones de Wokwi |
| `app.py` | Interfaz para cargar fotos y enviar resultados |
| `iniciar.cmd` / `instalar.cmd` | Abrir la aplicación / preparar dependencias |
| `wokwi.toml` | Firmware y puerto RFC2217 para VS Code |
| `build/` | HEX y ELF compilados en Wokwi a partir del `.ino` incluido |
| `compilar.ps1` | Volver a compilar usando Arduino CLI del IDE instalado |
| `control_acceso.code-workspace` | Abrir la carpeta correcta del simulador en VS Code |
| `modelos/` | Modelo YuNet de OpenCV, licencia MIT y origen de la descarga |

## Si reconoce el rostro pero no enciende el LED

- Si aparece **No se envió por serial**, desmarca **Solo analizar la foto** y vuelve a cargar la imagen.
- Si aparece **Sin conexión con el Arduino simulado**, abre `control_acceso.code-workspace`, ejecuta **Wokwi: Start Simulator** y mantén visible la simulación. Debe abrirse el puerto local 4000.
- El resultado verde o rojo en Python describe la detección. El mensaje **Arduino confirmó** indica que el programa de la placa recibió el resultado y respondió.
- Para una foto con rostro que antes aparecía como acceso denegado, reinicia `iniciar.cmd` para usar el detector corregido. El título debe incluir `v2`.

## Comprobaciones realizadas

- El programa compiló y arrancó en Wokwi con Arduino UNO.
- El comando `1` encendió solo el LED verde y devolvió `acceso correcto`.
- El comando `0` encendió solo el LED rojo y devolvió `acceso denegado`.
- El código y el diagrama exportados de Wokwi coinciden con los archivos locales.
- Se instaló el entorno Python y se comprobó la detección corregida con dos imágenes: ambas produjeron un rostro, incluida la foto recortada que Haar omitía.
- Tres imágenes uniformes (blanca, negra y verde) produjeron cero rostros.
- El modelo YuNet se obtuvo del repositorio oficial de OpenCV y se verificó su SHA256. Las fotos se procesan localmente.

## Documentación oficial

- Monitor serial: https://docs.wokwi.com/guides/serial-monitor
- Configuración y RFC2217: https://docs.wokwi.com/vscode/project-config
- Arduino UNO: https://docs.wokwi.com/parts/wokwi-arduino-uno
- Modelo YuNet: https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet
