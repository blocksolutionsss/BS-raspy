import matplotlib.pyplot as plt
import numpy as np
from tkinter import *
from customtkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Funci�n para dibujar el gr�fico de temperatura
def draw_temperature_potentiometer(temperature, frame):
    start_angle = -50  # El gr�fico empieza desde abajo (180�)
    total_range = 180  # Rango de temperatura (de 0 a 90�C)
    
    # Calcular la proporci�n de la temperatura sobre el rango m�ximo de 180 grados
    proportional_temperature = (temperature / total_range) * 100
    
    # Calcular el �ngulo que representa la temperatura proporcionalmente
    used_angle = (proportional_temperature / 100) * 280  # El �ngulo total es 280� (el arco)
    unused_angle = 180 - used_angle  # El �ngulo restante ser� la parte vac�a
    
    # Crear los datos del gr�fico
    data = [used_angle, unused_angle]
    colors = ['#7e7e7e', '#FFFFFF']  # Verde para la temperatura, blanco para lo vac�o
    
    # Crear la figura de Matplotlib con tama�o m�s peque�o
    fig, ax = plt.subplots(figsize=(2.7, 2.5))  # Tama�o reducido de la gr�fica
    
    # Primer gr�fico (con borde)
    ax.pie(data, startangle=start_angle, colors=colors, 
           wedgeprops={'width': 0.3, 'edgecolor': '#7e7e7e'})  # Borde verde para used_angle
    
    # Crear el segundo gr�fico encima del primero (sin borde)
    data2 = [used_angle, unused_angle]  # Datos para el segundo gr�fico (puedes modificarlos si lo deseas)
    colors2 = ['#FF6347', '#FFFFFF']  # Rojo para el segundo gr�fico, blanco para lo vac�o
    
    # Segundo gr�fico sin borde
    ax.pie(data2, startangle=start_angle, colors=colors2, 
           wedgeprops={'width': 0.3, 'edgecolor': 'none'})  # Sin borde
    
    # Configurar la visualizaci�n del gr�fico
    ax.set_aspect('equal')  # Asegura que el gr�fico sea un c�rculo
    
    # Ajustar el espacio blanco alrededor de la gr�fica
    plt.subplots_adjust(left=0.06, right=0.95, top=1, bottom=0.02)  # Ajusta el espacio blanco

    # Colocar la gr�fica dentro del frame
    canvas = FigureCanvasTkAgg(fig, master=frame)  # Crear un canvas para integrar la figura
    canvas.draw()
    canvas.get_tk_widget().grid(row=1, column=0, padx=10, pady=10)  # Insertar el gr�fico en el frame
    
    # Colocar texto encima y debajo del gr�fico
    label_temp = CTkLabel(master=frame, text="Temperatura", font=("Arial", 16))
    label_temp.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")  # Texto arriba de la gr�fica
    
    label_value = CTkLabel(master=frame, text=f"{temperature}�C", font=("Arial", 16))
    label_value.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")  # Texto abajo de la gr�fica

# Configuraci�n de la interfaz
app = CTk()
app.geometry("1200x700")

# Crear contenedor
container_frame = CTkFrame(master=app, width=800, height=500, border_color="#FFCC70", border_width=2)
container_frame.grid(padx=20, pady=20, sticky="nsew")

# Configurar las columnas del grid para que se expandan con diferentes proporciones
container_frame.grid_columnconfigure(0, weight=3)
container_frame.grid_columnconfigure(1, weight=1)

# Crear frame para historia de temperatura
frame_history = CTkFrame(master=container_frame, fg_color="#8D6F3A", border_color="#FFCC70", border_width=2)
frame_history.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Dibujar el gr�fico de temperatura dentro de frame_history
draw_temperature_potentiometer(90, frame_history)  # Llamar a la funci�n con una temperatura de ejemplo

# Configuraci�n de cierre de la aplicaci�n
def on_closing():
    print("Aplicaci�n cerrada.")
    app.destroy()
    exit()

app.protocol("WM_DELETE_WINDOW", on_closing)

# Ejecutar la aplicaci�n
app.mainloop()
