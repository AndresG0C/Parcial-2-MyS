import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import customtkinter as ctk
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Parámetros iniciales para todas las simulaciones
heptagon_x, heptagon_y, heptagon_z = [], [], []  # Coordenadas del heptágono
current_index = 0  # Para controlar el vértice actual en la animación
num_sides = 7  # Heptágono
radius = 5
height = 2  # Altura del polígono en Z

# Variables de velocidad para la primera simulación
v1, v2 = 0, 0  # Velocidades de los motores
angle = 0  # Ángulo inicial

# Limites del área de trabajo
X_LIMIT = (-10, 10)
Y_LIMIT = (-10, 10)
Z_LIMIT = (0, 2)

# Variables adicionales para la simulación de obstáculos
move_right = True  # Comienza moviéndose a la derecha
step_size = 0.5  # Tamaño del paso
obstacles = [(-5, -5), (3, 6), (0, 0), (5, -3)]  # Obstáculos en el área de trabajo
materials = [(6, 6), (-6, 6), (-6, -6), (6, -6)]  # Puntos de materiales

# Variables globales para la simulación 4
current_speed = 0.5  # Velocidad inicial antes del frenado
mobile_speed = 0.2
info_panel = None
materials_info_labels = []

# Distancia máxima para comenzar a frenar
d_max = 3.0

# Controlador de la figura y animación
fig = None
ani = None

# Función para simular el movimiento y frenado (Simulación 1)
def update_plot_3d(i):
    global angle, x_data, y_data, z_data, v1, v2
    dt = 0.1  # Intervalo de tiempo
    
    # Cálculo de nuevo ángulo y desplazamiento
    angle += (v2 - v1) * dt  # El ángulo cambia dependiendo de la diferencia de velocidades
    dx = (v1 + v2) * np.cos(angle) * dt
    dy = (v1 + v2) * np.sin(angle) * dt
    dz = 0  # Para mantenerlo en el plano 2D

    # Nueva posición
    x_new = x_data[-1] + dx
    y_new = y_data[-1] + dy
    z_new = z_data[-1] + dz

    # Detección de colisión con las paredes
    if not (X_LIMIT[0] < x_new < X_LIMIT[1]) or not (Y_LIMIT[0] < y_new < Y_LIMIT[1]):
        print("Colisión con las paredes. Simulación detenida.")
        return  # Detener la simulación si colisiona

    # Actualizar posiciones
    x_data.append(x_new)
    y_data.append(y_new)
    z_data.append(z_new)

    ax.clear()
    ax.plot(x_data, y_data, z_data, label="Trayectoria", color='red')
    ax.scatter(x_data[-1], y_data[-1], z_data[-1], label="Móvil", color='blue', s=100)

    # Configurar límites de la gráfica
    ax.set_xlim(X_LIMIT)
    ax.set_ylim(Y_LIMIT)
    ax.set_zlim(Z_LIMIT)
    ax.set_xlabel('X [m]')
    ax.set_ylabel('Y [m]')
    ax.set_zlabel('Z [m]')
    ax.legend()

# Función para actualizar la animación de la simulación del heptágono
def update_polygon_3d(i):
    global current_index, heptagon_x, heptagon_y, heptagon_z, x_data, y_data, z_data, ax
    
    # Limpiar y redibujar el heptágono completo
    ax.clear()
    # Mover el móvil vértice por vértice en el mismo plano (Z=0)
    if current_index < len(heptagon_x):
        # Dibujar la trayectoria hasta el punto actual
        x_data.append(heptagon_x[current_index])
        y_data.append(heptagon_y[current_index])
        z_data.append(0)  # Mantener z_data en 0 para que siga el plano XY

        # Dibujar el móvil como un punto rojo
        ax.scatter(heptagon_x[current_index], heptagon_y[current_index], 0, color='red', s=100, label="Móvil")

        current_index += 1
    else:
        current_index = 0  # Reiniciar el recorrido si llega al final

    # Redibujar la trayectoria del móvil
    ax.plot(x_data, y_data, z_data, color='blue', label="Trayectoria")

    # Configurar límites de la gráfica
    ax.set_xlim(X_LIMIT)
    ax.set_ylim(Y_LIMIT)
    ax.set_zlim(Z_LIMIT)
    ax.set_xlabel('X [m]')
    ax.set_ylabel('Y [m]')
    ax.set_zlabel('Z [m]')
    ax.legend()

# Inicializar las coordenadas del heptágono en 3D
def init_heptagon():
    global heptagon_x, heptagon_y, heptagon_z
    theta = np.linspace(0, 2 * np.pi, num_sides + 1)
    
    # Generar las coordenadas del heptágono en el plano XY con altura variable en Z
    heptagon_x = radius * np.cos(theta)
    heptagon_y = radius * np.sin(theta)
    heptagon_z = np.linspace(0, height, num_sides + 1)  # Variación en Z

# Función mejorada para esquivar obstáculos y regresar a la línea original de forma precisa (Simulación 3)
def update_area_traversal(i):
    global x_data, y_data, z_data, ax, move_right, current_speed
    
    # Condiciones para frenado completo
    m = 1  # Valor arbitrario de la masa
    b = 0.1  # Coeficiente de amortiguamiento (ajustar según comportamiento deseado)
    
    if current_speed <= 0.01:  # Condición para considerar que el móvil ya está frenado
        print("El móvil se ha detenido por completo.")
        return

    return_to_line = False  # Indicador para volver a la línea original
    original_x, original_y = x_data[-1], y_data[-1]  # Guardar la posición original antes de esquivar

    # Movimiento continuo en X y Y
    x_new = x_data[-1]
    y_new = y_data[-1]

    # Moverse a la derecha o izquierda
    if move_right:
        x_new += current_speed  # Incremento en X cuando se mueve a la derecha
    else:
        x_new -= current_speed  # Decremento en X cuando se mueve a la izquierda

    # Al llegar a los límites en X, cambiar de dirección y moverse en Y
    if x_new > X_LIMIT[1]:
        x_new = X_LIMIT[1]
        move_right = False
        y_new += current_speed
    elif x_new < X_LIMIT[0]:
        x_new = X_LIMIT[0]
        move_right = True
        y_new += current_speed

    # Detectar obstáculos y esquivar antes
    obstacle_size = 1  # Tamaño del obstáculo (asumimos que es un cuadrado de 1x1)
    avoidance_step = step_size  # Paso de esquivamiento
    avoidance_distance = step_size * 2  # Detectar antes para esquivar a tiempo

    for obstacle in obstacles:
        x_min, x_max = obstacle[0] - obstacle_size / 2 - avoidance_distance, obstacle[0] + obstacle_size / 2 + avoidance_distance
        y_min, y_max = obstacle[1] - obstacle_size / 2 - avoidance_distance, obstacle[1] + obstacle_size / 2 + avoidance_distance

        # Verificar si el móvil está dentro de los límites ajustados para esquivar a tiempo
        if x_min <= x_new <= x_max and y_min <= y_new <= y_max:
            print(f"Obstáculo detectado en ({x_new}, {y_new}). Evitando obstáculo.")
            
            # Esquivar pero intentar regresar a la línea original
            if move_right:
                x_new += avoidance_step  # Intentar rodear hacia la derecha primero
                return_to_line = True  # Activar el retorno a la línea
            else:
                x_new -= avoidance_step  # Intentar rodear hacia la izquierda primero
                return_to_line = True  # Activar el retorno a la línea
            if x_min <= x_new <= x_max:
                y_new += avoidance_step  # Mover en Y para rodear el obstáculo hacia arriba

    # Si se activa el retorno, volver a la línea original (asegurarse de que regresa a la misma X o Y)
    if return_to_line:
        # Verificar si el móvil puede volver a la línea original
        if move_right and x_new < original_x:
            x_new = original_x  # Volver a la línea original en X
        elif not move_right and x_new > original_x:
            x_new = original_x  # Volver a la línea original en X

    # Finalizar si se alcanzan los límites en Y
    if y_new > Y_LIMIT[1]:
        print("Área completa recorrida. Comenzando el frenado.")
        
        # Aplicar la ecuación de frenado mecánico
        current_speed = current_speed - (b * current_speed / m)  # Frenado amortiguado

    # Actualizar las posiciones
    x_data.append(x_new)
    y_data.append(y_new)
    z_data.append(0)  # Mantener z_data en 0 para el plano XY

    # Redibujar la trayectoria y los obstáculos
    ax.clear()
    ax.plot(x_data, y_data, z_data, label="Trayectoria", color='blue')
    ax.scatter(x_data[-1], y_data[-1], z_data[-1], label="Móvil", color='red', s=100)

    for obs in obstacles:
        ax.bar3d(obs[0], obs[1], 0, 10, 1, 1, color='black')  # Cubos de tamaño 1x1 en el plano XY

    ax.set_xlim(X_LIMIT)
    ax.set_ylim(Y_LIMIT)
    ax.set_zlim(Z_LIMIT)
    ax.set_xlabel('X [m]')
    ax.set_ylabel('Y [m]')
    ax.set_zlabel('Z [m]')
    ax.legend()

# Función actualizada para la simulación 4 con frenado y aceleración después de recolectar material
def update_material_search_simulation(i):
    global x_data, y_data, z_data, ax, materials, mobile_speed, info_panel
    
    # Velocidad original del móvil
    original_speed = 0.2

    if len(materials) == 0:
        print("Todos los materiales han sido recolectados.")
        return

    target_material = materials[0]
    
    # Calcular la distancia entre el móvil y el material
    distance_to_material = np.linalg.norm([x_data[-1] - target_material[0], y_data[-1] - target_material[1]])
    
    # Establecer el límite donde se empieza a frenar
    d_max = 3  # Distancia máxima para comenzar a frenar

    # Aplicar frenado cuando la distancia es menor a d_max
    if distance_to_material < d_max:
        # Ecuación de frenado: v_f = v_i * (d / d_max)
        current_speed = mobile_speed * (distance_to_material / d_max)
    else:
        # Velocidad normal si está fuera del rango de frenado
        current_speed = mobile_speed

    dx = np.sign(target_material[0] - x_data[-1]) * current_speed
    dy = np.sign(target_material[1] - y_data[-1]) * current_speed

    x_new = x_data[-1] + dx
    y_new = y_data[-1] + dy
    z_new = 0

    # Comprobar si ha alcanzado el material
    if np.linalg.norm([x_new - target_material[0], y_new - target_material[1]]) < 0.5:
        print(f"Material recolectado en {target_material}")
        materials.pop(0)

        # Después de recoger el material, restaurar la velocidad original
        mobile_speed = original_speed

    # Actualizar la trayectoria
    x_data.append(x_new)
    y_data.append(y_new)
    z_data.append(0)

    ax.clear()
    ax.plot(x_data, y_data, z_data, label="Trayectoria", color='blue')
    ax.scatter(x_data[-1], y_data[-1], z_data[-1], label="Móvil", color='red', s=100)

    # Dibujar materiales restantes
    for material in materials:
        ax.scatter(material[0], material[1], 0, label="Material", color='green', s=100)

    ax.set_xlim(X_LIMIT)
    ax.set_ylim(Y_LIMIT)
    ax.set_zlim(Z_LIMIT)
    ax.set_xlabel('X [m]')
    ax.set_ylabel('Y [m]')
    ax.set_zlabel('Z [m]')
    ax.legend()

    # Actualizar el panel de información
    update_info_panel(x_new, y_new, current_speed, materials)


# Función para crear el panel de información
def create_info_panel(root):
    global info_panel, materials_info_labels
    info_panel = ctk.CTkScrollableFrame(root, width=200)
    info_panel.pack(side=ctk.RIGHT, fill=ctk.Y, padx=10, pady=10)


    ctk.CTkLabel(info_panel, text="Panel de Información", font=("Arial", 16, "bold")).pack(pady=1)
    ctk.CTkLabel(info_panel, text="Variables Importantes", font=("Arial", 14, "bold")).pack(pady=1)

    global position_label, speed_label, materials_count_label
    position_label = ctk.CTkLabel(info_panel, text="Posición: ")
    position_label.pack(pady=1)

    speed_label = ctk.CTkLabel(info_panel, text="Velocidad: ")
    speed_label.pack(pady=1)

    materials_count_label = ctk.CTkLabel(info_panel, text="Materiales restantes: ")
    materials_count_label.pack(pady=1)

    ctk.CTkLabel(info_panel, text="Posición de Materiales:", font=("Arial", 12, "bold")).pack(pady=1)
    
    # Crear etiquetas para cada material
    for i in range(len(materials)):
        label = ctk.CTkLabel(info_panel, text=f"Material {i+1}: ")
        label.pack(pady=1)
        materials_info_labels.append(label)

# Función para actualizar el panel de información
def update_info_panel(x, y, speed, remaining_materials):
    position_label.configure(text=f"Posición: ({x:.2f}, {y:.2f})")
    speed_label.configure(text=f"Velocidad: {speed:.2f} m/s")
    materials_count_label.configure(text=f"Materiales restantes: {len(remaining_materials)}")

    # Actualizar la posición de cada material
    for i, material in enumerate(remaining_materials):
        if i < len(materials_info_labels):
            materials_info_labels[i].configure(text=f"Material {i+1}: ({material[0]:.2f}, {material[1]:.2f})")
        else:
            # Si hay más materiales que etiquetas, crear nuevas etiquetas
            label = ctk.CTkLabel(info_panel, text=f"Material {i+1}: ({material[0]:.2f}, {material[1]:.2f})")
            label.pack(pady=1)
            materials_info_labels.append(label)
    
    # Ocultar las etiquetas de materiales ya recolectados
    for i in range(len(remaining_materials), len(materials_info_labels)):
        materials_info_labels[i].pack_forget()

# Función modificada para ejecutar la simulación 4
def run_simulation_4():
    global fig, ax, x_data, y_data, z_data, materials, ani, mobile_speed, materials_info_labels

    # Reiniciar los datos para la simulación de búsqueda de materiales
    x_data, y_data, z_data = [0], [0], [0]
    materials = [(6, 6), (-6, 6), (-6, -6), (6, -6)]  # Reiniciar los materiales
    mobile_speed = 0.2  # Velocidad inicial
    materials_info_labels = []  # Reiniciar las etiquetas de información de materiales

    root = ctk.CTk()
    root.title("Simulación 4: Búsqueda y recolección de materiales")

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

    create_info_panel(root)

    ani = FuncAnimation(fig, update_material_search_simulation, interval=100)

    def on_close():
        ani.event_source.stop()
        plt.close(fig)
        root.quit()
        root.destroy()
        show_menu()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

# Función para iniciar la simulación seleccionada
def run_simulation(simulation_type):
    global fig, ax, x_data, y_data, z_data, current_index, move_right, materials, ani

    # Si hay una simulación o figura abierta, cerrarla
    if plt.fignum_exists(fig.number) if fig else False:
        plt.close(fig)

    if simulation_type == "Simulación 1" or simulation_type == "Simulación 2":
        # Reiniciar los datos de la trayectoria, comenzando en el origen
        x_data, y_data, z_data = [0], [0], [0]  # Iniciar en el origen
    elif simulation_type == "Simulación 3":
        # Reiniciar los datos de la trayectoria, comenzando en la esquina inferior izquierda
        x_data, y_data, z_data = [-10], [-10], [0]  # Iniciar en la esquina inferior izquierda
    elif simulation_type == "Simulación 4":
        # Reiniciar los datos para la simulación de búsqueda de materiales
        x_data, y_data, z_data = [0], [0], [0]
        materials = [(6, 6), (-6, 6), (-6, -6), (6, -6)]  # Reiniciar los materiales

    current_index = 0  # Reiniciar el índice de vértices
    move_right = True  # Reiniciar la dirección de movimiento

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Asignar la función de actualización de acuerdo a la simulación seleccionada
    if simulation_type == "Simulación 1":
        ani = FuncAnimation(fig, update_plot_3d, interval=100)
    elif simulation_type == "Simulación 2":
        init_heptagon()
        ani = FuncAnimation(fig, update_polygon_3d, interval=500)
    elif simulation_type == "Simulación 3":
        ani = FuncAnimation(fig, update_area_traversal, interval=100)
    elif simulation_type == "Simulación 4":
        ani = FuncAnimation(fig, update_material_search_simulation, interval=100)

    def on_close(event):
        global ani
        ani.event_source.stop()  # Detener la animación
        plt.close(fig)  # Cerrar la figura completamente
        show_menu()  # Abrir el menú nuevamente

    fig.canvas.mpl_connect('close_event', on_close)  # Conectar el evento de cierre
    plt.show()

# Submenú para establecer las velocidades (solo para simulación 1)
def show_submenu():
    submenu = ctk.CTk()
    submenu.title("Configurar Velocidades")
    submenu.geometry("400x300")

    def start_simulation_with_values():
        global v1, v2
        v1 = float(entry_v1.get())
        v2 = float(entry_v2.get())
        submenu.destroy()
        run_simulation("Simulación 1")

    label_v1 = ctk.CTkLabel(submenu, text="Velocidad Motor 1:")
    label_v1.pack(pady=10)
    entry_v1 = ctk.CTkEntry(submenu)
    entry_v1.pack(pady=10)

    label_v2 = ctk.CTkLabel(submenu, text="Velocidad Motor 2:")
    label_v2.pack(pady=10)
    entry_v2 = ctk.CTkEntry(submenu)
    entry_v2.pack(pady=10)

    start_button = ctk.CTkButton(submenu, text="Iniciar Simulación", command=start_simulation_with_values)
    start_button.pack(pady=20)

    submenu.mainloop()

# Modificar la función show_menu para usar la nueva run_simulation_4
def show_menu():
    root = ctk.CTk()
    root.title("Seleccionar Simulación")
    root.geometry("400x300")

    label = ctk.CTkLabel(root, text="Seleccione la simulación que desea ejecutar")
    label.pack(pady=20)

    btn_sim1 = ctk.CTkButton(root, text="Simulación 1: Movimiento en 3D", command=lambda: [root.destroy(), show_submenu()])
    btn_sim1.pack(pady=10)

    btn_sim2 = ctk.CTkButton(root, text="Simulación 2: Recorrido de un Heptágono", command=lambda: [root.destroy(), run_simulation("Simulación 2")])
    btn_sim2.pack(pady=10)

    btn_sim3 = ctk.CTkButton(root, text="Simulación 3: Recorrido tipo serpiente", command=lambda: [root.destroy(), run_simulation("Simulación 3")])
    btn_sim3.pack(pady=10)

    btn_sim4 = ctk.CTkButton(root, text="Simulación 4: Búsqueda y recolección de materiales", command=lambda: [root.destroy(), run_simulation_4()])
    btn_sim4.pack(pady=10)

    root.mainloop()

# Iniciar con el menú de selección de simulación
show_menu()
