import customtkinter
from tkinter import filedialog,colorchooser
import qrDinamico

# file_path = ""

def button_callback():
	# pth = os.path.join(os.getcwd(),'media', 'logoDif.jpg')
	print(file_path)
	try:
		qrDinamico.makeQRDinamico(txtData.get(),file_path)
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
    color_code = colorchooser.askcolor(title ="Choose Center color") 
    print("Center: ",color_code[0])

def choose_colorBack():
    # variable to store hexadecimal code of color
    color_code = colorchooser.askcolor(title ="Choose Back color") 
    print("Back: ",color_code[0])

def choose_colorEdge():
    # variable to store hexadecimal code of color
    color_code = colorchooser.askcolor(title ="Choose Edge color") 
    print("Edge: ",color_code[0])

app = customtkinter.CTk()
app.title("QR Code Generator")
app.geometry("400x600")
app.grid_columnconfigure(0, weight=1)

label = customtkinter.CTkLabel(app, text="Ingresa el texto que deseas convertir en un código QR:")
label.grid(row=0, column=0, padx=10, pady=10, columnspan=3)
txtData = customtkinter.CTkEntry(app)
txtData.grid(row=1, column=0, padx=10, pady=10,columnspan=3)

upload_button = customtkinter.CTkButton(app, text="Upload File", command=upload_file)
upload_button.grid(row=2, column=0, padx=20, pady=20)

buttonBack = customtkinter.CTkButton(app, text="Color Button", command=choose_colorBack)
buttonBack.grid(row=3, column=0, padx=10, pady=10)

buttonCenter = customtkinter.CTkButton(app, text="Color Button", command=choose_colorCenter)
buttonCenter.grid(row=3, column=1, padx=10, pady=10)

buttonEdge = customtkinter.CTkButton(app, text="Color Button", command=choose_colorEdge)
buttonEdge.grid(row=3, column=2, padx=10, pady=10)

button = customtkinter.CTkButton(app, text="my button", command=button_callback)
button.grid(row=4, column=0, padx=20, pady=20)

app.mainloop()