IDEAS
- HomeAssistant:
    - Hosteado en un RaspberryPi (pruebas en Mac)
    - multiples ESP32 envian data sensor a RPi por MQTT (ESPHome?)
    - cada ESP con su propia bomba
    - HA permite mostrar data y activar bomba
    - HA tiene automatizada la acción de la bomba
    - no usado porque aunque hay un RPi0 disponible, no se están consiguiendo más actualmente
    - ventajas:
        - menos trabajo de front
        - permite integrar cámaras/switches/otras cosas
        - permite integrar con alexa/etc...
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