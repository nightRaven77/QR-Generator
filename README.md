 # QR Code Generator

A customizable QR code generator with a modern graphical user interface built using Python. This application allows you to create stylized QR codes with various design options and embedded images.

## Features

- Generate QR codes from any text or URL
- Customize QR code appearance with different module styles:
  - Circle modules
  - Square modules with gaps
  - Horizontal bars
  - Vertical bars
  - Rounded modules
  - Default square modules
- Add a custom image in the center of the QR code
- Modern GUI built with CustomTkinter

## Requirements

- Python 3.x
- Required packages:
  ```
  customtkinter
  qrcode
  Pillow
  ```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/QR-Generator.git
```

2. Install the required packages:
```bash
pip install customtkinter qrcode Pillow
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Enter the text or URL you want to convert to a QR code
3. (Optional) Select an image to embed in the center of the QR code
4. Choose a module style from the dropdown menu
5. Click "Generate" to create your QR code
6. The generated QR code will be saved in the "exported" folder on your Desktop

## Project Structure

```
QR-Generator/
├── main.py           # Main application file with GUI
├── qrDinamico.py    # QR code generation logic
└── assets/          # Folder for storing assets
```

## Contributing

Feel free to fork this project and submit pull requests with improvements.

## License

[Add your chosen license here]

## Acknowledgments

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the modern GUI elements
- [qrcode](https://github.com/lincolnloop/python-qrcode) for QR code generation capabilities
```

Would you like me to add or modify any specific sections in the README? For example, we could add:
1. Screenshots of the application
2. More detailed usage instructions
3. Specific configuration options
4. Troubleshooting section

Let me know what additional information you'd like to include!