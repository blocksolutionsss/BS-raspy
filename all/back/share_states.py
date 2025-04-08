import threading
from threading import Lock

from .rabbit import send_notification
from .config import DEVICE


monitoring = False
terminate = False
elapsed_time = {
    'hours': 0,
    'minutes': 0,
}
paused = False
lock = Lock()  # Para proteger el acceso concurrente

def set_monitoring(value):
    global monitoring
    with lock:  # Protege el acceso a la variable
        monitoring = value
        print(monitoring)

def get_monitoring():
    with lock:  # Protege el acceso a la variable
        return monitoring
    
def set_terminate(value):
    global terminate
    with lock:
        terminate = value    
def get_terminate():
    with lock:
        return terminate


def reset_elapsed_time():
    global elapsed_time
    with lock:
        elapsed_time = {'hours': 0, 'minutes': 0}

def increment_elapsed_time():
    global elapsed_time, paused
    prev_time = {'hours': 0, 'minutes': 0}

    while True:
        with lock:
            if not paused:  # Solo incrementa si no est� en pausa
                elapsed_time['minutes'] += 1

                if elapsed_time['minutes'] == 60:
                    elapsed_time['minutes'] = 0
                    elapsed_time['hours'] += 1

                # Solo enviar notificaciones si hay un cambio en minutos o horas
                if prev_time['minutes'] != elapsed_time['minutes']:
                    payload = {
                        "device": DEVICE,
                        "minutes": elapsed_time['minutes']
                    }
                    send_notification('bs.real-time-minute', payload)

                if prev_time['hours'] != elapsed_time['hours']:
                    payload = {
                        "device": DEVICE,
                        "hours": elapsed_time['hours']
                    }
                    send_notification('bs.real-time-hour', payload)

                # Imprimir el tiempo para observar el progreso
                print(f"{elapsed_time['hours']:02}:{elapsed_time['minutes']:02}")
        
        # Esperar 60 segundos antes del siguiente incremento (porque ya no estamos usando segundos)
        threading.Event().wait(60)


def toggle_pause_time():
    global paused
    with lock:
        paused = not paused  # Cambia el estado entre pausado y reanudado
        if paused:
            print("El contador esta en pausa.")
        else:
            print("El contador ha sido reanudado.")

def get_elapsed_time():
    with lock:
        return elapsed_time.copy()          
    

def start_counter():
    hilo_timer = threading.Thread(target=increment_elapsed_time)
    hilo_timer.daemon = True  # El hilo se cerrar� cuando el programa principal termine
    hilo_timer.start()
    print("Hilo de timer iniciado.")
