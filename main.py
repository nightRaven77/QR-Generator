import customtkinter
from tkinter import filedialog, colorchooser
import qrDinamico


# define las funciones para los botones
def upload_file():
    """Funcion que permite subir una imagen"""
    global file_path
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )
    if file_path:
        print("Selected file:", file_path)


def choose_colorEdge():
    """Funcion que permite seleccionar el color del borde del QR"""
    global edgeColor
    edgeColor = colorchooser.askcolor(title="Choose Edge color")
    print("Edge: ", edgeColor[0])


def choose_colorCenter():
    """Funcion que permite seleccionar el color del centro del QR"""
    global centerColor
    centerColor = colorchooser.askcolor(title="Choose Center color")
    print("Center: ", centerColor[0])


def choose_colorBack():
    """Funcion que permite seleccionar el color del fondo del QR"""
    global backColor
    backColor = colorchooser.askcolor(title="Choose Back color")
    print("Back: ", backColor[0])


def btn_Generar():
    """Funcion que permite generar el QR"""
    try:
        qrDinamico.makeQRDinamico(
            txtData.get(),
            file_path,
            backColor[0],
            edgeColor[0],
            centerColor[0],
            selected_drawer.get()
        )
        txtData.delete(0, customtkinter.END)
    except Exception:
        print("Error al generar el QR: ")


# estructura de la ventana
app = customtkinter.CTk()
app.title("QR Code Generator")
app.geometry("600x400")
app.grid_columnconfigure(0, weight=3)
app.grid_columnconfigure(1, weight=3)
app.grid_columnconfigure(2, weight=3)

# Create an input text to convert to QR
labelText = customtkinter.CTkLabel(
    app, text="Ingresa el texto que deseas convertir en un código QR:")
labelText.grid(row=0, column=0, padx=0, pady=20, columnspan=2)

txtData = customtkinter.CTkEntry(app, width=200)
txtData.grid(row=0, column=2, padx=20, pady=20)

# create a button to search the image to center in the QR
labelImage = customtkinter.CTkLabel(
    app, text="Seleccione la Imagen para el centro:")
labelImage.grid(row=1, column=0, padx=0, pady=20, columnspan=2)

upload_button = customtkinter.CTkButton(
    app, text="Upload File", command=upload_file, width=200)
upload_button.grid(row=1, column=2, padx=10, pady=10)

# create a drawer menu to select the drawer of the QR
# Create a dropdown menu
selected_drawer = customtkinter.StringVar()
selected_drawer.set("default")
# Set the default value
drawer_options = ["circle", "square", "horizontal",
                  "vertical", "rounded", "default"]

# Create a label for the dropdown menu
label = customtkinter.CTkLabel(app, text="Selecciona un estilo para el QR:")
label.grid(row=2, column=0, padx=0, pady=10, columnspan=2)

drawer_menu = customtkinter.CTkOptionMenu(
    app, variable=selected_drawer, values=drawer_options, width=200)
drawer_menu.grid(row=2, column=2, padx=10, pady=10)

# create a button to select the Edge color of the QR
labelEdgeColor = customtkinter.CTkLabel(
    app, text="Selecciona un color para el Contorno:")
labelEdgeColor.grid(row=3, column=0, padx=0, pady=10, columnspan=2)

buttonEdge = customtkinter.CTkButton(
    app, text="Edge Color", command=choose_colorEdge, width=200)
buttonEdge.grid(row=3, column=2, padx=10, pady=10)

# create a button to select the Center color of the QR
labelCenterColor = customtkinter.CTkLabel(
    app, text="Selecciona un color para el Centro:")
labelCenterColor.grid(row=4, column=0, padx=0, pady=10, columnspan=2)

buttonCenter = customtkinter.CTkButton(
    app, text="Center Color", command=choose_colorCenter, width=200)
buttonCenter.grid(row=4, column=2, padx=10, pady=10)

# create a button to select the Back color of the QR
labelBackColor = customtkinter.CTkLabel(
    app, text="Selecciona un color para el Fondo:")
labelBackColor.grid(row=5, column=0, padx=0, pady=10, columnspan=2)

buttonBack = customtkinter.CTkButton(
    app, text="Background Color", command=choose_colorBack, width=200)
buttonBack.grid(row=5, column=2, padx=10, pady=10)

button = customtkinter.CTkButton(app, text="Generar", command=btn_Generar, width=400)
button.grid(row=6, column=0, padx=0, pady=20, columnspan=3)

app.mainloop()
