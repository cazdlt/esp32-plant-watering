# Remote Plant Monitoring & Watering System
Crear un sistema que:
- Monitoree la humedad de diferentes plantas y la temperatura de la casa
- Permita ver el histórico de esa humedad (15-30 días)
- Permita actuar sobre una planta para regarle agua
- Permita automatizar el regado de esta agua
- Permita ver y actuar en esto de forma segura a través de internet

## Ideas
- HomeAssistant:
    - Hosteado en un RaspberryPi (pruebas en Mac)
    - multiples ESP32 envian data sensor a RPi por MQTT (ESPHome?)
    - cada ESP con su propia bomba
    - HA permite mostrar data y activar bomba
    - HA tiene automatizada la acción de la bomba
    - no usado porque aunque hay un RPi0 disponible, no se están consiguiendo más actualmente
    - cómo desplegar a internet?
    - ventajas:
        - menos trabajo de front
        - permite integrar cámaras/switches/otras cosas
        - Permite automatizar con lógica fuera del ESP
        - permite integrar con alexa/google/telegram etc...
- Broker:
    - Puede ser RPi
    - recibe data MQTT de multiples ESP32 con sensores
    - Cada ESP tiene su bomba
    - backend cloud recibe data de broker a traves de HTTP (croneado desde backend) y lo guarda en db
    - frontend cloud muestra data y permita activar bomba
    - estado de cada esp se guarda en db
    - periodicamente se lee estado en broker desde db y se actualiza en esp correspondiente por MQTT
    - demasiado complejo innecesariamente
- Broker Fácil:
    - Hay un broker+backend en la nube
    - comunica con esp32 a través de mqtt
    - cada esp envía data de sensor a topic relevante
    - guarda en db (timescale)
    - front con dashboard (grafana/react) puede enviar señal de regar agua a través de mqtt
    - eventualmente broker puede ser el RPi y comunicar con rabbit/kafka al backend 
- AWS / Azure IOT
    - no es tan divertido
    - más similar a lo que se podría hacer en la industria
- Blynk
    - micropy install blynklib (https://github.com/blynkkk/lib-python)
    - Descargar blynklib_mp a ./lib/
    - NUNCA SIRVIÓ

## TODO
- Last Will de conexión del nodo para avisar no disponible
- Manejar texto UTF8 en MQTT
- Añadir actuador
- Conseguir y configurar Raspberry Pi
- Usar postgres/timescaledb para medidas a "largo" plazo (1 mes)
- Dashboard grafana con estas medidas