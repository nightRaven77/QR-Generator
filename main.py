import customtkinter
from tkinter import filedialog, colorchooser
import qrDinamico


def btn_Generar():
	print(file_path)
	print("Center: ", centerColor[0])
	print("Back: ",backColor[0])
	print("Edge: ",edgeColor[0])
	try:
		qrDinamico.makeQRDinamico(txtData.get(), file_path, backColor[0], edgeColor[0], centerColor[0])	
	except Exception:
		print("Error al generar el QR: ")


def upload_file():
	global file_path
	file_path = filedialog.askopenfilename(
		filetypes=[("Image files", "*.jpg *.jpeg")]
	)
	if file_path:
		print("Selected file:", file_path)
        # Process the selected file here


def choose_colorCenter():
    # variable to store hexadecimal code of color
	global centerColor
	centerColor = colorchooser.askcolor(title="Choose Center color")
	print("Center: ", centerColor[0])


def choose_colorBack():
    # variable to store hexadecimal code of color
	global backColor
	backColor = colorchooser.askcolor(title="Choose Back color")
	print("Back: ",backColor[0])

def choose_colorEdge():
    # variable to store hexadecimal code of color
	global edgeColor
	edgeColor = colorchooser.askcolor(title ="Choose Edge color") 
	print("Edge: ",edgeColor[0])

app = customtkinter.CTk()
app.title("QR Code Generator")
app.geometry("600x400")
app.grid_columnconfigure(0, weight=3)
app.grid_columnconfigure(1, weight=3)
app.grid_columnconfigure(2, weight=3)

label = customtkinter.CTkLabel(app, text="Ingresa el texto que deseas convertir en un código QR:")
label.grid(row=0, column=0, padx=20, pady=20, columnspan=3)

txtData = customtkinter.CTkEntry(app)
txtData.grid(row=1, column=0, padx=20, pady=20,columnspan=3)

upload_button = customtkinter.CTkButton(app, text="Upload File", command=upload_file)
upload_button.grid(row=2, column=1, padx=10, pady=10)

buttonBack = customtkinter.CTkButton(app, text="Background Color", command=choose_colorBack)
buttonBack.grid(row=3, column=0, padx=10, pady=10)

buttonCenter = customtkinter.CTkButton(app, text="Center Color", command=choose_colorCenter)
buttonCenter.grid(row=3, column=1, padx=10, pady=10)

buttonEdge = customtkinter.CTkButton(app, text="Edge Color", command=choose_colorEdge)
buttonEdge.grid(row=3, column=2, padx=10, pady=10)

button = customtkinter.CTkButton(app, text="Generar", command=btn_Generar)
button.grid(row=4, column=1, padx=20, pady=20)

app.mainloop()