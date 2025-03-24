import customtkinter
from tkinter import filedialog, colorchooser
import qrDinamico



#define las funciones para los botones
def upload_file():
    global file_path
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.jpeg")]
    )
    if file_path:
        print("Selected file:", file_path)

app = customtkinter.CTk()
app.title("QR Code Generator")
app.geometry("600x400")
app.grid_columnconfigure(0, weight=3)
app.grid_columnconfigure(1, weight=3)
app.grid_columnconfigure(2, weight=3)

#Create an input text to convert to QR
labelText = customtkinter.CTkLabel(
    app, text="Ingresa el texto que deseas convertir en un código QR:")
labelText.grid(row=0, column=0, padx=0, pady=20, columnspan=2)

txtData = customtkinter.CTkEntry(app, width=200)
txtData.grid(row=0, column=2, padx=20, pady=20)

#create a button to search the image to center in the QR
labelImage = customtkinter.CTkLabel(
    app, text="Seleccione la Imagen para el centro:")
labelImage.grid(row=1, column=0, padx=0, pady=20, columnspan=2)

upload_button = customtkinter.CTkButton(
    app, text="Upload File", command=upload_file)
upload_button.grid(row=1, column=2, padx=10, pady=10)

#create a drawer menu to select the drawer of the QR
# Create a dropdown menu
selected_drawer = customtkinter.StringVar()
selected_drawer.set("default")
# Set the default value
drawer_options = ["circle", "square", "horizontal",
                  "vertical", "rounded", "default"]

# Create a label for the dropdown menu
label = customtkinter.CTkLabel(app, text="Selecciona un estilo para el QR:")
label.grid(row=2, column=2, padx=10, pady=10)

drawer_menu = customtkinter.CTkOptionMenu(
    app, variable=selected_drawer, values=drawer_options)
drawer_menu.grid(row=2, column=0, padx=10, pady=10)

app.mainloop()

# buttonBack = customtkinter.CTkButton(
#     app, text="Background Color", command=choose_colorBack)
# buttonBack.grid(row=3, column=0, padx=10, pady=10)

# buttonCenter = customtkinter.CTkButton(
#     app, text="Center Color", command=choose_colorCenter)
# buttonCenter.grid(row=3, column=1, padx=10, pady=10)

# buttonEdge = customtkinter.CTkButton(
#     app, text="Edge Color", command=choose_colorEdge)
# buttonEdge.grid(row=3, column=2, padx=10, pady=10)


# button = customtkinter.CTkButton(app, text="Generar", command=btn_Generar)
# button.grid(row=4, column=1, padx=20, pady=20)



# def btn_Generar():
#     print(file_path)
#     print("Center: ", centerColor[0])
#     print("Back: ", backColor[0])
#     print("Edge: ", edgeColor[0])
#     try:
#         qrDinamico.makeQRDinamico(
#             txtData.get(),
#             file_path,
#             backColor[0],
#             edgeColor[0],
#             centerColor[0],
#             selected_drawer.get()
#         )
#         txtData.delete(0, customtkinter.END)
#     except Exception:
#         print("Error al generar el QR: ")


#     # Process the selected file here

# def choose_colorCenter():
#     # variable to store hexadecimal code of color
#     global centerColor
#     centerColor = colorchooser.askcolor(title="Choose Center color")
#     print("Center: ", centerColor[0])

# def choose_colorBack():
#     # variable to store hexadecimal code of color
#     global backColor
#     backColor = colorchooser.askcolor(title="Choose Back color")
#     print("Back: ", backColor[0])

# def choose_colorEdge():
#     # variable to store hexadecimal code of color
#     global edgeColor
#     edgeColor = colorchooser.askcolor(title="Choose Edge color")
#     print("Edge: ", edgeColor[0])
