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
mobile_speed = 0.5
current_speed = mobile_speed
moving_to_drop_zone = False
info_panel = None
materials_info_labels = []
materials_position = [(0, 0), (0.5, 0), (1, 0), (1.5, 0)]  # Posición donde están inicialmente todos los materiales
drop_zone = (-5, -5)  # Zona de entrega de los materiales
materials_collected = []  # Lista para almacenar los materiales recolectados
target_material = None  # Material objetivo
delivery_point = (-8, -8)  # Punto de entrega de los materiales
# Lista de materiales entregados
delivered_materials = []
carrying_material = False  # Indicador si el móvil lleva material
mobile_data = {}  # Diccionario para almacenar los datos de los móviles


# Distancia máxima para comenzar a frenar
d_max = 3.0

fig, ani = None, None
canvas = None  # Canvas global
legend_shown = False  # Variable para controlar si ya se ha mostrado la leyenda

# Modificar las clases de formulario para manejar la configuración en orden
class MobileConfigForm:
    def __init__(self):
        self.mobile_count = 1
        self.mobile_velocities = []  # Lista para almacenar pares de velocidades
        
    def show_count_form(self):
        count_window = ctk.CTk()
        count_window.title("Configurar Número de Móviles")
        count_window.geometry("400x200")
        
        def submit_count():
            try:
                count = int(entry_count.get())
                if count < 1:
                    raise ValueError("El número debe ser mayor a 0")
                if count > 10:
                    raise ValueError("Máximo 10 móviles permitidos")
                self.mobile_count = count
                count_window.destroy()
                self.show_velocity_form()
            except ValueError as e:
                error_label.configure(text=str(e))
        
        label = ctk.CTkLabel(count_window, text="Número de móviles a simular:")
        label.pack(pady=10)
        
        entry_count = ctk.CTkEntry(count_window)
        entry_count.pack(pady=10)
        entry_count.insert(0, "1")
        
        error_label = ctk.CTkLabel(count_window, text="", text_color="red")
        error_label.pack(pady=5)
        
        submit_btn = ctk.CTkButton(count_window, text="Continuar", command=submit_count)
        submit_btn.pack(pady=20)
        
        count_window.mainloop()
    
    def show_velocity_form(self):
        vel_window = ctk.CTk()
        vel_window.title("Configurar Velocidades de Móviles")
        
        # Calcular el tamaño de la ventana basado en el número de móviles
        window_height = max(400, 100 + (self.mobile_count * 120))
        vel_window.geometry(f"500x{window_height}")
        
        # Crear un frame con scroll para muchos móviles
        frame = ctk.CTkScrollableFrame(vel_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        velocity_entries = []  # Lista para almacenar los entries de velocidades
        
        def submit_velocities():
            try:
                self.mobile_velocities = []
                for i, (entry_v1, entry_v2) in enumerate(velocity_entries):
                    v1 = float(entry_v1.get())
                    v2 = float(entry_v2.get())
                    self.mobile_velocities.append((v1, v2))
                vel_window.destroy()
                self.start_simulation()
            except ValueError:
                error_label.configure(text="Por favor ingrese valores numéricos válidos")
        
        # Crear campos para cada móvil
        for i in range(self.mobile_count):
            mobile_frame = ctk.CTkFrame(frame)
            mobile_frame.pack(pady=10, fill="x")
            
            ctk.CTkLabel(mobile_frame, text=f"Móvil {i+1}").pack(pady=5)
            
            vel_frame = ctk.CTkFrame(mobile_frame)
            vel_frame.pack(pady=5)
            
            # Velocidad 1
            v1_frame = ctk.CTkFrame(vel_frame)
            v1_frame.pack(side="left", padx=10)
            ctk.CTkLabel(v1_frame, text="Velocidad Motor 1:").pack()
            entry_v1 = ctk.CTkEntry(v1_frame)
            entry_v1.pack()
            entry_v1.insert(0, "1.0")
            
            # Velocidad 2
            v2_frame = ctk.CTkFrame(vel_frame)
            v2_frame.pack(side="left", padx=10)
            ctk.CTkLabel(v2_frame, text="Velocidad Motor 2:").pack()
            entry_v2 = ctk.CTkEntry(v2_frame)
            entry_v2.pack()
            entry_v2.insert(0, "1.0")
            
            velocity_entries.append((entry_v1, entry_v2))
        
        error_label = ctk.CTkLabel(vel_window, text="", text_color="red")
        error_label.pack(pady=5)
        
        submit_btn = ctk.CTkButton(vel_window, text="Iniciar Simulación", command=submit_velocities)
        submit_btn.pack(pady=20)
        
        vel_window.mainloop()
    
    def start_simulation(self):
        # Inicializar los datos de los móviles con las velocidades configuradas
        init_multi_mobile_simulation(self.mobile_count, self.mobile_velocities)
        run_simulation_1()

# Modificar la función de inicialización de múltiples móviles
def init_multi_mobile_simulation(count, velocities):
    global mobile_data
    mobile_data.clear()  # Limpiar cualquier dato anterior

    # Inicializar datos para cada móvil con sus velocidades específicas
    for i in range(count):
        v1, v2 = velocities[i]
        mobile_data[i] = {
            'x_data': [i * 0.5],  # Posiciones iniciales con un pequeño offset para evitar colisiones iniciales
            'y_data': [i * 0.5],
            'z_data': [0],
            'angle': 0,
            'v1': v1,
            'v2': v2
        }

def init_multi_mobile_simulation_3(count, velocities):
    global mobile_data
    mobile_data.clear()  # Limpiar cualquier dato anterior

    # Definir posiciones iniciales en lados opuestos
    initial_positions = [(-10, -10), (10, 10)]  # Definir dos posiciones iniciales

    for i in range(count):
        v1, v2 = velocities[i]
        x_init, y_init = initial_positions[i % len(initial_positions)]  # Asignar posiciones iniciales de forma cíclica si hay más móviles
        mobile_data[i] = {
            'x_data': [x_init],
            'y_data': [y_init],
            'z_data': [0],
            'angle': 0,
            'v1': v1,
            'v2': v2
        }


def update_plot_3d(i):
    global mobile_data
    
    ax.clear()
    
    for mobile_id in mobile_data:
        data = mobile_data[mobile_id]
        dt = 0.1
        
        # Calcular la nueva posición para este móvil
        if data['v1'] != data['v2']:
            data['angle'] += (data['v2'] - data['v1']) * dt
        
        dx = (data['v1'] + data['v2']) / 2 * np.cos(data['angle']) * dt
        dy = (data['v1'] + data['v2']) / 2 * np.sin(data['angle']) * dt
        dz = 0
        
        x_new = data['x_data'][-1] + dx
        y_new = data['y_data'][-1] + dy
        z_new = data['z_data'][-1] + dz
        
        # Verificar los límites
        if X_LIMIT[0] < x_new < X_LIMIT[1] and Y_LIMIT[0] < y_new < Y_LIMIT[1]:
            data['x_data'].append(x_new)
            data['y_data'].append(y_new)
            data['z_data'].append(z_new)
            
            # Dibujar la trayectoria y la posición actual
            ax.plot(data['x_data'], data['y_data'], data['z_data'], 
                    label=f"Móvil {mobile_id + 1}", 
                    color=plt.cm.tab10(mobile_id % 10))
            ax.scatter(x_new, y_new, z_new, 
                       color=plt.cm.tab10(mobile_id % 10), 
                       s=100)
            
            # Flecha de dirección
            arrow_length = 0.5
            ax.quiver(x_new, y_new, z_new,
                      arrow_length * np.cos(data['angle']),
                      arrow_length * np.sin(data['angle']),
                      0,
                      color=plt.cm.tab10(mobile_id % 10),
                      arrow_length_ratio=0.5)
    
    ax.set_xlim(X_LIMIT)
    ax.set_ylim(Y_LIMIT)
    ax.set_zlim(Z_LIMIT)
    ax.set_xlabel('X [m]')
    ax.set_ylabel('Y [m]')
    ax.set_zlabel('Z [m]')
    ax.legend()
    
# Función modificada para actualizar la animación del polígono
def update_polygon_3d(i):
    global current_index, heptagon_x, heptagon_y, heptagon_z, x_data, y_data, z_data, ax, ani, legend_shown
    
    # Inicializar las listas de datos si están vacías
    if not x_data:
        x_data = []
        y_data = []
        z_data = []
    
    # Limpiar y redibujar el polígono
    if current_index < len(heptagon_x):
        ax.clear()

        # Añadir los datos actuales del vértice a la trayectoria
        x_data.append(heptagon_x[current_index])
        y_data.append(heptagon_y[current_index])
        z_data.append(heptagon_z[current_index])

        # Dibujar el polígono completo
        ax.plot(heptagon_x, heptagon_y, heptagon_z, 'k--', alpha=0.5)
        
        # Dibujar el móvil en el vértice actual
        ax.scatter(heptagon_x[current_index], heptagon_y[current_index], heptagon_z[current_index],
                  color='red', s=100, label="Móvil")

        # Dibujar la trayectoria recorrida
        if len(x_data) > 1:
            ax.plot(x_data, y_data, z_data, color='blue', label="Trayectoria")

                # Añadir una flecha que indique la dirección del movimiento
        if current_index > 0:
            ax.quiver(x_data[-2], y_data[-2], z_data[-2],
                      x_data[-1] - x_data[-2], y_data[-1] - y_data[-2], z_data[-1] - z_data[-2],
                      color='green', arrow_length_ratio=0.1)

        current_index += 1
    
    # Configurar límites y etiquetas
    ax.set_xlim(X_LIMIT)
    ax.set_ylim(Y_LIMIT)
    ax.set_zlim(Z_LIMIT)
    ax.set_xlabel('X [m]')
    ax.set_ylabel('Y [m]')
    ax.set_zlabel('Z [m]')
    ax.legend()

# Inicializar las coordenadas del polígono
def init_polygon():
    global heptagon_x, heptagon_y, heptagon_z, num_sides
    theta = np.linspace(0, 2 * np.pi, num_sides + 1)  # Ángulos para los vértices
    
    # Generar las coordenadas del polígono
    heptagon_x = radius * np.cos(theta)
    heptagon_y = radius * np.sin(theta)
    heptagon_z = np.zeros(len(theta))  # Mantener z_data en 0

def update_area_traversal(i):
    global mobile_data, ax

    ax.clear()

    # Primero calculamos las posiciones actuales de todos los móviles
    current_positions = {
        mobile_id: (data['x_data'][-1], data['y_data'][-1])
        for mobile_id, data in mobile_data.items()
    }

    for mobile_id in mobile_data:
        data = mobile_data[mobile_id]
        dt = 0.3

        x_current = data['x_data'][-1]
        y_current = data['y_data'][-1]

        # Velocidad base
        base_speed = mobile_speed

        # Verificar la distancia a otros móviles
        min_distance_to_other = float('inf')
        for other_id, other_pos in current_positions.items():
            if other_id != mobile_id:
                distance = np.sqrt((x_current - other_pos[0])**2 + (y_current - other_pos[1])**2)
                min_distance_to_other = min(min_distance_to_other, distance)

        # Distancia de seguridad y distancia máxima de frenado
        d_safe = 2.0  # Distancia mínima de seguridad
        d_max = 4.0   # Distancia donde comienza el frenado

        # Calcular la velocidad actual usando la ecuación de frenado
        if min_distance_to_other < d_max:
            if min_distance_to_other <= d_safe:
                current_speed = 0  # Detener completamente si está muy cerca
            else:
                # Ecuación de frenado: v = v0 * (d - d_safe)/(d_max - d_safe)
                current_speed = base_speed * ((min_distance_to_other - d_safe)/(d_max - d_safe))
        else:
            current_speed = base_speed

        # Determinar dirección del movimiento
        if mobile_id % 2 == 0:
            # Móvil par se mueve de izquierda a derecha
            if data.get('move_right', True):
                x_new = x_current + current_speed * dt
                if x_new > X_LIMIT[1]:
                    x_new = X_LIMIT[1]
                    data['move_right'] = False
                    y_current += 1.0
            else:
                x_new = x_current - current_speed * dt
                if x_new < X_LIMIT[0]:
                    x_new = X_LIMIT[0]
                    data['move_right'] = True
                    y_current += 1.0
        else:
            # Móvil impar se mueve de derecha a izquierda
            if data.get('move_right', False):
                x_new = x_current + current_speed * dt
                if x_new > X_LIMIT[1]:
                    x_new = X_LIMIT[1]
                    data['move_right'] = False
                    y_current -= 1.0
            else:
                x_new = x_current - current_speed * dt
                if x_new < X_LIMIT[0]:
                    x_new = X_LIMIT[0]
                    data['move_right'] = True
                    y_current -= 1.0

        # Verificar límites de Y
        if y_current > Y_LIMIT[1]:
            y_current = Y_LIMIT[1]
        elif y_current < Y_LIMIT[0]:
            y_current = Y_LIMIT[0]

        # Actualizar las posiciones
        data['x_data'].append(x_new)
        data['y_data'].append(y_current)
        data['z_data'].append(0)

        # Visualización
        ax.plot(data['x_data'], data['y_data'], data['z_data'], 
                label=f"Trayectoria Móvil {mobile_id + 1}", 
                color=plt.cm.tab10(mobile_id % 10))
        ax.scatter(x_new, y_current, 0, 
                   color=plt.cm.tab10(mobile_id % 10), 
                   s=100, 
                   label=f"Móvil {mobile_id + 1}")

        # Flecha de dirección
        if len(data['x_data']) > 1:
            ax.quiver(data['x_data'][-2], data['y_data'][-2], data['z_data'][-2],
                      data['x_data'][-1] - data['x_data'][-2],
                      data['y_data'][-1] - data['y_data'][-2],
                      data['z_data'][-1] - data['z_data'][-2],
                      color=plt.cm.tab10(mobile_id % 10),
                      arrow_length_ratio=0.1)

    # Dibujar obstáculos
    for obs in obstacles:
        ax.bar3d(obs[0], obs[1], 0, 1, 1, 2, color='black')

    # Configurar límites y etiquetas
    ax.set_xlim(X_LIMIT)
    ax.set_ylim(Y_LIMIT)
    ax.set_zlim(Z_LIMIT)
    ax.set_xlabel('X [m]')
    ax.set_ylabel('Y [m]')
    ax.set_zlabel('Z [m]')
    ax.legend()

def update_material_search_simulation(i):
    global mobile_data, ax, materials, delivered_materials, carrying_material

    ax.clear()

    for mobile_id, data in mobile_data.items():
        # Velocidad original del móvil
        original_speed = 0.2

        # Si lleva material, dirigirse al punto de entrega
        if data.get('carrying_material', False):
            target = delivery_point
        else:
            # Si no lleva material y hay materiales disponibles, buscar el próximo
            if len(materials) == 0:
                print(f"Todos los materiales han sido recolectados y entregados por Móvil {mobile_id + 1}.")
                continue
            target = materials[0]

        # Calcular la distancia entre el móvil y el objetivo
        distance_to_target = np.linalg.norm([data['x_data'][-1] - target[0], data['y_data'][-1] - target[1]])

        # Establecer el límite donde se empieza a frenar
        d_max = 3  # Distancia máxima para comenzar a frenar

        # Aplicar frenado cuando la distancia es menor a d_max
        if distance_to_target < d_max:
            # Ecuación de frenado: v_f = v_i * (d / d_max)
            current_speed = mobile_speed * (distance_to_target / d_max)
        else:
            # Velocidad normal si está fuera del rango de frenado
            current_speed = mobile_speed

        dx = np.sign(target[0] - data['x_data'][-1]) * current_speed
        dy = np.sign(target[1] - data['y_data'][-1]) * current_speed

        x_new = data['x_data'][-1] + dx
        y_new = data['y_data'][-1] + dy
        z_new = 0

        # Comprobar si ha alcanzado el objetivo
        if distance_to_target < 0.5:
            if data.get('carrying_material', False):
                # Si lleva un material y llega al punto de entrega
                print(f"Material entregado en {delivery_point} por Móvil {mobile_id + 1}")
                delivered_materials.append(delivery_point)  # Añadir el punto de entrega a la lista de materiales entregados
                data['carrying_material'] = False  # Dejar de llevar el material
            else:
                # Si no lleva material y llega al material objetivo
                print(f"Material recolectado en {target} por Móvil {mobile_id + 1}")
                materials.pop(0)  # Remover el material de la lista de materiales
                data['carrying_material'] = True  # Ahora está llevando un material

        # Actualizar la trayectoria
        data['x_data'].append(x_new)
        data['y_data'].append(y_new)
        data['z_data'].append(z_new)

        # Dibujar la trayectoria y la posición actual del móvil
        ax.plot(data['x_data'], data['y_data'], data['z_data'], label=f"Trayectoria Móvil {mobile_id + 1}", color=plt.cm.tab10(mobile_id % 10))
        ax.scatter(x_new, y_new, z_new, color=plt.cm.tab10(mobile_id % 10), s=100, label=f"Móvil {mobile_id + 1}")

        # Dibujar una flecha para indicar la dirección del movimiento
        if len(data['x_data']) > 1:
            ax.quiver(data['x_data'][-2], data['y_data'][-2], data['z_data'][-2],
                      data['x_data'][-1] - data['x_data'][-2],
                      data['y_data'][-1] - data['y_data'][-2],
                      data['z_data'][-1] - data['z_data'][-2],
                      color=plt.cm.tab10(mobile_id % 10),
                      arrow_length_ratio=0.1)

    # Dibujar materiales restantes
    for material in materials:
        ax.bar3d(material[0], material[1], 0, 0.9, 1, 0.09, color='green', alpha=0.7)

    # Dibujar los materiales entregados en el punto de entrega
    for idx, delivered_material in enumerate(delivered_materials):
        offset = 0.3 * idx  # Añadir un desplazamiento para cada material entregado
        ax.bar3d(delivered_material[0] + offset, delivered_material[1] + offset, 0, 0.9, 1, 0.09, color='orange', alpha=0.7)

    # Dibujar el área de entrega
    ax.bar3d(delivery_point[0], delivery_point[1], 0, 6, 6, 0.015, color='yellow', alpha=0.3)

    ax.set_xlim(X_LIMIT)
    ax.set_ylim(Y_LIMIT)
    ax.set_zlim(Z_LIMIT)
    ax.set_xlabel('X [m]')
    ax.set_ylabel('Y [m]')
    ax.set_zlabel('Z [m]')
    ax.legend()

    # Actualizar el panel de información con la posición del último móvil
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

# Función para ejecutar la simulación 1 con giro
def run_simulation_1():
    global fig, ax, ani
    
    root = ctk.CTk()
    root.title(f"Simulación 1: {len(mobile_data)} Móviles en 3D")
    
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
    
    ani = FuncAnimation(fig, update_plot_3d, interval=100)
    
    def on_close():
        ani.event_source.stop()
        plt.close(fig)
        root.quit()
        root.destroy()
        show_menu()
    
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

# Función actualizada para ejecutar simulación 2
def run_polygon_simulation(parent_root):
    global fig, ax, ani, current_index, x_data, y_data, z_data

    current_index = 0
    x_data, y_data, z_data = [], [], []
    
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    init_polygon()
    
    canvas = FigureCanvasTkAgg(fig, master=parent_root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
    
    ani = FuncAnimation(fig, update_polygon_3d, interval=500)
    
    def on_close():
        ani.event_source.stop()
        plt.close(fig)
        parent_root.quit()
        parent_root.destroy()
        show_menu()
    
    parent_root.protocol("WM_DELETE_WINDOW", on_close)

def run_simulation_3(count):
    global fig, ax, mobile_data, ani, move_right
    
    move_right = True
    init_multi_mobile_simulation_3(count, [(mobile_speed, mobile_speed) for _ in range(count)])

    root = ctk.CTk()
    root.title(f"Simulación 3: Recorrido tipo serpiente con {count} Móviles")
    
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
    
    ani = FuncAnimation(fig, update_area_traversal, interval=100)
    
    def on_close():
        ani.event_source.stop()
        plt.close(fig)
        root.quit()
        root.destroy()
        show_menu()
    
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

def run_simulation_4(count):
    global fig, ax, mobile_data, ani, delivery_point, mobile_speed, materials_collected, materials_info_labels , materials

    # Reiniciar los datos para la simulación de búsqueda y entrega de materiales
    init_multi_mobile_simulation(count, [(mobile_speed, mobile_speed) for _ in range(count)])

    # Definir las nuevas posiciones de los materiales
    materials = [
        (7, 7),   # Material 1 - Parte superior derecha
        (7, 8),   # Material 2 - Parte inferior derecha
        (8, 7),   # Material 3 - Parte superior izquierda
        (8, 8)    # Material 4 - Parte inferior izquierda
    ]
    # Definir el nuevo punto de entrega
    delivery_point = (-8, -8)
    materials_collected = []
    materials_info_labels = []

    root = ctk.CTk()
    root.title(f"Simulación 4: Búsqueda y recolección de materiales con {count} Móviles")

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

# Función actualizada para el submenú de velocidades
def show_submenu():
    config_form = MobileConfigForm()
    config_form.show_count_form()

# Actualizar las funciones del menú principal para solicitar el número de móviles antes de las simulaciones 3 y 4
def show_submenu_3_4(simulation_type):
    count_window = ctk.CTk()
    count_window.title("Configurar Número de Móviles")
    count_window.geometry("400x200")

    def submit_count():
        try:
            count = int(entry_count.get())
            if count < 1:
                raise ValueError("El número debe ser mayor a 0")
            if count > 10:
                raise ValueError("Máximo 10 móviles permitidos")
            count_window.destroy()
            if simulation_type == 3:
                run_simulation_3(count)
            elif simulation_type == 4:
                run_simulation_4(count)
        except ValueError as e:
            error_label.configure(text=str(e))

    label = ctk.CTkLabel(count_window, text="Número de móviles a simular:")
    label.pack(pady=10)

    entry_count = ctk.CTkEntry(count_window)
    entry_count.pack(pady=10)
    entry_count.insert(0, "1")

    error_label = ctk.CTkLabel(count_window, text="", text_color="red")
    error_label.pack(pady=5)

    submit_btn = ctk.CTkButton(count_window, text="Continuar", command=submit_count)
    submit_btn.pack(pady=20)

    count_window.mainloop()

    # Función actualizada para el submenú del polígono
def show_polygon_submenu():
    submenu = ctk.CTk()
    submenu.title("Configurar Polígono")
    submenu.geometry("400x300")

    def start_simulation_with_sides():
        global num_sides
        try:
            sides = int(entry_sides.get())
            if sides < 3:
                raise ValueError("El número de lados debe ser mayor o igual a 3")
            num_sides = sides
            submenu.withdraw()
            
            sim_window = ctk.CTk()
            sim_window.title("Simulación 2: Recorrido del Polígono")
            run_polygon_simulation(sim_window)
            sim_window.mainloop()
            
        except ValueError as e:
            error_label.configure(text=str(e))

    label_sides = ctk.CTkLabel(submenu, text="Número de Lados del Polígono (mínimo 3):")
    label_sides.pack(pady=10)
    
    entry_sides = ctk.CTkEntry(submenu)
    entry_sides.pack(pady=10)
    entry_sides.insert(0, "7")
    
    error_label = ctk.CTkLabel(submenu, text="", text_color="red")
    error_label.pack(pady=5)
    
    start_button = ctk.CTkButton(submenu, text="Iniciar Simulación", command=start_simulation_with_sides)
    start_button.pack(pady=20)

    def on_close():
        submenu.destroy()
        show_menu()

    submenu.protocol("WM_DELETE_WINDOW", on_close)
    submenu.mainloop()

# Función actualizada del menú principal
def show_menu():
    root = ctk.CTk()
    root.title("Seleccionar Simulación")
    root.geometry("400x300")

    label = ctk.CTkLabel(root, text="Seleccione la simulación que desea ejecutar")
    label.pack(pady=20)

    btn_sim1 = ctk.CTkButton(root, text="Simulación 1: Movimiento en 3D",command=lambda: [root.destroy(), show_submenu()])
    btn_sim1.pack(pady=10)

    btn_sim2 = ctk.CTkButton(root, text="Simulación 2: Recorrido de un Polígono",command=lambda: [root.destroy(), show_polygon_submenu()])
    btn_sim2.pack(pady=10)

    btn_sim3 = ctk.CTkButton(root, text="Simulación 3: Recorrido tipo serpiente",command=lambda: [root.destroy(), show_submenu_3_4(3)])
    btn_sim3.pack(pady=10)

    btn_sim4 = ctk.CTkButton(root, text="Simulación 4: Búsqueda y recolección de materiales",command=lambda: [root.destroy(), show_submenu_3_4(4)])
    btn_sim4.pack(pady=10)

    root.mainloop()

show_menu()