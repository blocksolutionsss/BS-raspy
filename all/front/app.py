from customtkinter import *
import time

def on_closing():
    print("Aplicacion cerrada.")
    app.destroy()
    exit() 

app = CTk()
app.geometry("1050x400")

app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=1)

valor = 10

peso1 = None
peso2 = None
temperatura = None
humedad = None
aire = None




def update_humidity(new_humidity):
    global humedad
    humedad = new_humidity
    label_h_2.configure(text=f'{new_humidity:.2f}%')

def update_temperature(new_temperature):
    global temperatura
    print("temperatura atualizado")
    temperatura = new_temperature
    label_t_2.configure(text=f'{new_temperature:.2f}C°')


def update_air_quality(new_air_quality):
    global aire
    print("aire atualizado")
    aire = new_air_quality
    label_a_2.configure(text=f'{new_air_quality:.2f}%')

def update_weight1(new_weight1):
    global peso1
    print("peso1 atualizado")
    peso1 = new_weight1
    label_w1_1.configure(text=f'{new_weight1:.2f}g')

def update_weight2(new_weight2):
    global peso2
    print("peso2 atualizado")
    peso2 = new_weight2
    label_w2_1.configure(text=f'{new_weight2:.2f}g')



container_frame = CTkFrame(master=app)
container_frame.grid(padx=20, pady=20, sticky="nsew")

container_frame.grid_columnconfigure(0, weight=3)
container_frame.grid_columnconfigure(1, weight=1)

# Crear el primer frame (m�s grande)
frame_history = CTkFrame(master=container_frame, width=80, border_color="#FFCC70", border_width=2)
frame_history.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
frame_history.grid_rowconfigure(0, weight=1)  # Expande la fila que contiene frame_history
frame_history.grid_columnconfigure(0, weight=1)





history_temp_1 = CTkFrame(master=frame_history, fg_color="#49231E",border_color="#49231E",border_width=2, width=100)
history_temp_1.grid(row=0, column=0, padx=10, pady=10, sticky="nw")


history_hum = CTkFrame(master=frame_history, fg_color="#8e9dcc", border_color="#8e9dcc", border_width=2, width=100)
history_hum.grid(row=0, column=1, padx=10, pady=10, sticky="nw")


history_air = CTkFrame(master=frame_history, fg_color="#49231E", border_color="#49231E", border_width=2, width=100)
history_air.grid(row=0, column=2, padx=10, pady=10, sticky="nw")


history_w1 = CTkFrame(master=frame_history, fg_color="#49231E", border_color="#49231E", border_width=2, width=100)
history_w1.grid(row=0, column=3, padx=10, pady=10, sticky="nw")


history_w2 = CTkFrame(master=frame_history, fg_color="#49231E", border_color="#49231E", border_width=2, width=100)
history_w2.grid(row=0, column=4, padx=10, pady=10, sticky="nw")



frame_serial_esp32 = CTkFrame(
    master=container_frame,
    border_color="#ffffff",
    border_width=2,  # Ancho del borde
)
frame_serial_esp32.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")  # Padding a trav�s de grid()




set_appearance_mode("dark")

label_h = CTkLabel(master=history_temp_1, text="Temperatura")
label_h.grid(row=0, column=0, padx=30, pady=(10, 0), sticky="nsew")

label_h_2 = CTkLabel(master=history_temp_1, text=f"{temperatura}C°", font=("Arial", 20))
label_h_2.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew") 



label_t = CTkLabel(master=history_hum, text="Humedad")
label_t.grid(padx=30, pady=(10, 0), sticky="nsew")

label_t_2 = CTkLabel(master=history_hum, text=f"{humedad}%", font=("Arial", 20))
label_t_2.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew") 



label_a = CTkLabel(master=history_air, text="Aire puro")
label_a.grid(padx=30, pady=(10, 0), sticky="nsew")

label_a_2 = CTkLabel(master=history_air, text=f"{aire}%", font=("Arial", 20))
label_a_2.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew") 

label_w1 = CTkLabel(master=history_w1, text="Peso 1")
label_w1.grid(padx=30, pady=(10, 0), sticky="nsew")

label_w1_1 = CTkLabel(master=history_w1, text=f"{peso1}g", font=("Arial", 20))
label_w1_1.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew") 

label_w2 = CTkLabel(master=history_w2, text="Peso 2")
label_w2.grid(padx=30, pady=(10, 0), sticky="nsew")

label_w2_1 = CTkLabel(master=history_w2, text=f"{peso2}g", font=("Arial", 20))
label_w2_1.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew") 





# Configuraci�n de cierre de la aplicaci�n
app.protocol("WM_DELETE_WINDOW", on_closing)

# Crear label para el frame_serial_esp32
label_e = CTkLabel(master=frame_serial_esp32, text="ESP32 Serial", width=100, fg_color="green",   anchor="center",  # Centrar el texto tanto horizontal como verticalmente
    justify="center",)
label_e.grid(row=0, column=0, padx=10, pady=10, sticky="w", columnspan=1)  # Alineado a la izquierda

label_infor = CTkLabel(
    master=frame_serial_esp32,
    text="Esperando...",
    width=300,  # Ancho fijo
    height=260,  # Alto fijo, suficiente para acomodar m�ltiples l�neas
    anchor="nw",  # Alinear el texto hacia la parte superior izquierda
    justify="left",  # Justificar el texto a la izquierda
    fg_color="#666660",
    corner_radius=5,
    padx=5,  # Espacio a la izquierda dentro del label
    pady=5,
    wraplength=290  # Ajusta el texto si es m�s largo que 290px
)
label_infor.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")  # Alineado a la izquierda


mensajes = []

# Funci�n para actualizar el texto del label con un l�mite de 10 l�neas
def actualizar_label_limite(nuevo_texto):
    global mensajes
    mensajes.append(nuevo_texto)  # Agregar el nuevo mensaje a la lista
    if len(mensajes) > 12:  # Limitar a las �ltimas 10 l�neas
        mensajes.pop(0)
    texto_actualizado = "\n".join(mensajes)  # Combinar los mensajes con saltos de l�nea
    label_infor.configure(text=texto_actualizado)  # Actualizar el texto del label

