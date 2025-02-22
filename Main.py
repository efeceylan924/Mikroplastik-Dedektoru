import cv2
import numpy as np
from tkinter import Tk, filedialog, Label, Button, Canvas, PhotoImage, simpledialog
from PIL import Image, ImageTk, ImageEnhance
import os
from fpdf import FPDF


def fix_text(text):
    replacements = {
        "ı": "i", "İ": "I", "ç": "c", "Ç": "C", "ğ": "g", "Ğ": "G",
        "ö": "o", "Ö": "O", "ş": "s", "Ş": "S", "ü": "u", "Ü": "U"
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def process_image(file_path):
    image = cv2.imread(file_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    pil_image = Image.fromarray(gray)
    enhancer = ImageEnhance.Contrast(pil_image)
    contrast_image = enhancer.enhance(1.2)
    contrast_np = np.array(contrast_image)

    edges = cv2.Canny(contrast_np, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    output = cv2.cvtColor(contrast_np, cv2.COLOR_GRAY2BGR)
    microplastic_data = []

    for idx, contour in enumerate(contours):
        if len(contour) >= 5:
            ellipse = cv2.fitEllipse(contour)
            cv2.ellipse(output, ellipse, (255, 0, 0), 2)

            (x, y), (major_axis, minor_axis), angle = ellipse
            major_axis = int(major_axis)
            minor_axis = int(minor_axis)
            aspect_ratio = round(major_axis / minor_axis, 5)

            cv2.putText(output, str(idx + 1), (int(x), int(y)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

            microplastic_data.append((idx + 1, major_axis, minor_axis, aspect_ratio))

    return Image.fromarray(output), microplastic_data


def generate_pdf(microplastic_data):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, fix_text("Mikroplastik Boyutları"), ln=True, align='C')
    pdf.ln(10)

    pdf.cell(40, 10, fix_text("Numara"), 1)
    pdf.cell(50, 10, fix_text("En (px)"), 1)
    pdf.cell(50, 10, fix_text("Boy (px)"), 1)
    pdf.cell(50, 10, fix_text("En/Boy Oranı"), 1)
    pdf.ln()

    for num, width, height, aspect_ratio in microplastic_data:
        pdf.cell(40, 10, str(num), 1)
        pdf.cell(50, 10, str(width), 1)
        pdf.cell(50, 10, str(height), 1)
        pdf.cell(50, 10, f"{aspect_ratio:.5f}", 1)
        pdf.ln()

    pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if pdf_path:
        pdf.output(pdf_path, 'F')


def open_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
    if not file_path:
        return

    processed_img, microplastic_data = process_image(file_path)
    processed_img.thumbnail((400, 400))

    img_tk = ImageTk.PhotoImage(processed_img)
    canvas.image = img_tk
    canvas.create_image(0, 0, anchor='nw', image=img_tk)

    global processed_image, processed_img_path, microplastic_info
    processed_image = processed_img
    processed_img_path = file_path
    microplastic_info = microplastic_data


def save_image():
    if processed_image:
        file_path = filedialog.asksaveasfilename(filetypes=[("PNG file", "*.png"), ("JPG file", "*.jpg")])
        if file_path:
            processed_image.save(file_path)


def save_pdf():
    if microplastic_info:
        generate_pdf(microplastic_info)


root = Tk()
root.title("Mikroplastik Tespiti")

label = Label(root, text="Görseli yükleyin ve işlemi başlatın")
label.pack()

canvas = Canvas(root, width=400, height=400)
canvas.pack()

btn_open = Button(root, text="Görsel Yükle", command=open_image)
btn_open.pack()

btn_save = Button(root, text="Görseli Kaydet", command=save_image)
btn_save.pack()

btn_save_pdf = Button(root, text="PDF Olarak Kaydet", command=save_pdf)
btn_save_pdf.pack()

processed_image = None
processed_img_path = None
microplastic_info = None

root.mainloop()
