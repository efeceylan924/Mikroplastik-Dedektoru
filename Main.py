import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# Tkinter ana pencereyi oluştur
root = tk.Tk()
root.title("Mikroplastik Tespiti ve Görsel İşleme")


# Yeni kod: Mikroplastik tespiti ve hafif kontrast artırımı

def load_and_process_microplastics():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if not file_path:
        return

    global microplastic_processed_image
    image = cv2.imread(file_path)

    # Eğer görüntü okunamazsa hata mesajı göster
    if image is None:
        messagebox.showerror("Hata",
                             "Görsel yüklenemedi! Lütfen dosya yolunu ve dosyanın bozulmamış olduğunu kontrol edin.")
        return

    process_microplastic_image(image)


def process_microplastic_image(image):
    global microplastic_processed_image

    # Görseli gri tonlamaya çevir
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Kontrastı çok az artır
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.normalize(l, None, alpha=100, beta=180, norm_type=cv2.NORM_MINMAX)  # Hafif kontrast artırımı
    lab = cv2.merge((l, a, b))
    contrast_image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    gray = cv2.cvtColor(contrast_image, cv2.COLOR_BGR2GRAY)

    # Kenar tespiti
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blurred, 30, 100)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    for contour in contours:
        if len(contour) > 5:
            ellipse = cv2.fitEllipse(contour)
            cv2.ellipse(gray_bgr, ellipse, (0, 0, 255), 2)  # Kırmızı renk ve 2 px kalınlıkta çiz

    microplastic_processed_image = gray_bgr
    display_microplastic_image(gray_bgr)


def display_microplastic_image(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    image_tk = ImageTk.PhotoImage(image)

    microplastic_panel.config(image=image_tk)
    microplastic_panel.image = image_tk


def save_microplastic_image():
    if microplastic_processed_image is None:
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("JPEG", "*.jpeg")])
    if file_path:
        cv2.imwrite(file_path, microplastic_processed_image)


# Yeni butonlar ve panel ekleme
btn_load_microplastic = tk.Button(root, text="Mikroplastik Görsel Yükle", command=load_and_process_microplastics)
btn_load_microplastic.pack()

btn_save_microplastic = tk.Button(root, text="İşlenen Mikroplastik Görseli Kaydet", command=save_microplastic_image)
btn_save_microplastic.pack()

microplastic_panel = tk.Label(root)
microplastic_panel.pack()

microplastic_processed_image = None

# Tkinter ana döngüsünü başlat
root.mainloop()
