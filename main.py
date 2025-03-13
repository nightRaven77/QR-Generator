import customtkinter
import qrDinamico 
import os


def button_callback():
	pth = os.path.join(os.getcwd(),'media', 'logoDif.jpg')
	try:
		qrDinamico.makeQRDinamico(txtData.get(),pth)
	except Exception:
		print("Error al generar el QR: ")


app = customtkinter.CTk()
app.title("QR Code Generator")
app.geometry("400x300")
app.grid_columnconfigure(0, weight=1)

label = customtkinter.CTkLabel(app, text="Ingresa el texto	 que deseas convertir en un código QR:")
label.grid(row=0, column=0, padx=10, pady=10)

txtData = customtkinter.CTkEntry(app)
txtData.grid(row=1, column=0, padx=10, pady=10)

button = customtkinter.CTkButton(app, text="my button", command=button_callback)
button.grid(row=2, column=0, padx=20, pady=20)

app.mainloop()