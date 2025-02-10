from tkinter import *
from tkinter import ttk
from tkinter import messagebox, filedialog
from PIL import ImageTk, Image, ImageSequence # 1 2 3 4 5
from tkinter.filedialog import askopenfilename
from scipy.stats import chisquare # 1 2
from scipy.fft import dct # 3
import numpy as np # 3
import collections # 1 2
import math # 1 2
import matplotlib.pyplot as plt # 1 3


window = Tk()
window.geometry("650x350")

carrier = Text(width = 40, height = 5)
carrier.place(x = 10,y = 30)

hiden_file = Text(width = 40, height = 5)
hiden_file.place(x = 10,y = 180)

lb2 = ttk.Label()


def open_carrier():
    filepath = askopenfilename()
    carrier.delete("1.0", END)
    carrier.insert("1.0",filepath)


def open_hiden_file():
    filepath = askopenfilename()
    hiden_file.delete("1.0", END)
    hiden_file.insert("1.0", filepath)


def XI_gistogramm():
    src = carrier.get("1.0", END)
    image = Image.open(src[:-1], 'r')
    height = image.size[1]

    p_values = []
    for i in range(1, height + 1):
       # Открываем изображение
       image = Image.open(src[:-1], 'r')

       # Получаем данные пикселей
       pixels = list(image.getdata())

       # Получаем ширину и высоту
       width, height = image.size

       # Преобразуем список пикселей в список строк
       pixels = [pixels[j * width:(j + 1) * width] for j in range(height)]

       # Переводим пиксели в последовательность битов
       bit_sequence = ''
       for j in range(i):
           for pixel in pixels[j]:
               bit_sequence += format(pixel[0], '08b')[-1]
               bit_sequence += format(pixel[1], '08b')[-1]
               bit_sequence += format(pixel[2], '08b')[-1]

       # Подсчитываем частоту битов в последовательности
       freq = collections.Counter(bit_sequence)
       total = sum(freq.values())
       freq = {k: v / total for k, v in freq.items()}

       # Рассчитываем статистику хи-квадрат и уровень значимости
       observed = [freq.get('0', 0), freq.get('1', 0)]
       expected = [0.5, 0.5]
       chi_square, p_value = chisquare(observed, expected)

       # Добавляем p-value в список
       p_values.append(p_value)

    if all(p == p_values[0] for p in p_values):
        hiden_file.insert(END, "\nСокрытие не обнаружено")
    else:
        hiden_file.insert(END, "\nСокрытие обнаружено")

    hiden_file.delete("1.0", END)
    hiden_file.insert("1.0", "Чем меньше значение уровня значимости, тем выше вероятность того, что в изображении содержится скрытое сообщение.")
        
    # Построение графика
    plt.plot(range(1, height + 1), p_values)
    plt.xlabel('Строки')
    plt.ylabel('Уровень значимости')
    plt.title('Вероятность встраивания в каждой строке')
    plt.show()


def XI_sravnenie():
    src = carrier.get("1.0", END)
    image = Image.open(src[:-1], 'r')
    pixels = list(image.getdata())
    width, height = image.size
    pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]

    # Переводим пиксели в последовательность битов
    bit_sequence = ''
    for row in pixels:
        for pixel in row:
            bit_sequence += format(pixel[0], '08b')[-1]
            bit_sequence += format(pixel[1], '08b')[-1]
            bit_sequence += format(pixel[2], '08b')[-1]

    # Подсчитываем частоту битов в последовательности
    freq = collections.Counter(bit_sequence)
    total = sum(freq.values())
    freq = {k: v / total for k, v in freq.items()}

    # Рассчитываем статистику хи-квадрат и уровень значимости
    observed = [freq.get('0', 0), freq.get('1', 0)]
    expected = [0.5, 0.5]
    chi_square, p_value = chisquare(observed, expected)

    hiden_file.delete("1.0", END)
    hiden_file.insert("1.0", f"Число хи-квадрат: {chi_square} , Уровень значимости: {p_value}. Чем меньше значение уровня значимости, тем выше вероятность того, что в изображении содержится скрытое сообщение.")


def Koh_Jao():
# Загрузить цветное изображение
    src = carrier.get("1.0", END)
    image = Image.open(src[:-1], 'r')
    image = np.array(image)

    # Получаем размеры изображения
    height, width, _ = image.shape

    # Вычисляем количество блоков по высоте и ширине
    num_blocks_h = height // 8
    num_blocks_w = width // 8

    # Оставляем только полные блоки
    image = image[:num_blocks_h * 8, :num_blocks_w * 8]

    # Разделить изображение на блоки размером 8x8
    blocks = [image[i:i+8, j:j+8] for i in range(0, image.shape[0], 8) for j in range(0, image.shape[1], 8)]

    # Применить дискретное косинусное преобразование (ДКП) к каждому блоку для каждого канала цвета
    DCT_blocks = [[dct(dct(block[:,:,c].T, norm='ortho').T, norm='ortho') for c in range(3)] for block in blocks]

    # Вычислить три последовательности значений для каждого канала цвета
    C1 = [np.abs(channel[3, 4]) - np.abs(channel[4, 3]) for block in DCT_blocks for channel in block]
    C2 = [np.abs(channel[3, 5]) - np.abs(channel[5, 3]) for block in DCT_blocks for channel in block]
    C3 = [np.abs(channel[4, 5]) - np.abs(channel[5, 4]) for block in DCT_blocks for channel in block]

    hiden_file.delete("1.0", END)
    hiden_file.insert("1.0", "Высокие центральные вершины и ступенчатый характер гистограмм позволяет предположить о наличии встраиваемой информации.")

    # Проверяем, есть ли значения больше 125
    if any(value > 125 for value in C1) or any(value > 125 for value in C2) or any(value > 125 for value in C3):
        hiden_file.insert(END, "\nСокрытие обнаружено")
    else:
        hiden_file.insert(END, "\nСокрытие не обнаружено")

    # Построить гистограммы для каждой последовательности
    plt.figure(figsize=(15,5))

    plt.subplot(1, 3, 1)
    plt.hist(C1, bins='auto')
    plt.title("C1")

    plt.subplot(1, 3, 2)
    plt.hist(C2, bins='auto')
    plt.title("C2")

    plt.subplot(1, 3, 3)
    plt.hist(C3, bins='auto')
    plt.title("C3")

    plt.show()


def GIF_palitra():
    #gif_path = 'new_file.gif'
    gif_path = 'clearImage.gif'
    with Image.open(gif_path) as im:
        # Проверяем наличие глобальной палитры
        if im.getpalette() is None:
            hiden_file.delete("1.0", END)
            hiden_file.insert("1.0", f"GIF-файл не содержит глобальной палитры.  ")
            return

        # Считываем глобальную палитру
        palette = im.getpalette()
        global_palette_colors = []
        for i in range(0, len(palette), 3):
            global_palette_colors.append((palette[i], palette[i+1], palette[i+2]))

        # Подсчитываем уникальные цвета в глобальной палитре
        unique_palette_colors_count = len(set(global_palette_colors))
        hiden_file.delete("1.0", END)
        hiden_file.insert("1.0", f"Глобальная палитра содержит {unique_palette_colors_count} уникальных цветов.  ")

        # Проходим по каждому кадру GIF-файла
        for frame in ImageSequence.Iterator(im):
            # Считываем цвета кадра
            frame_colors = set()
            for y in range(frame.height):
                for x in range(frame.width):
                    pixel_index = frame.getpixel((x, y))
                    if pixel_index < len(global_palette_colors):
                        frame_colors.add(global_palette_colors[pixel_index])
            frame_colors = list(frame_colors)

            # Подсчитываем уникальные цвета в кадре
            unique_frame_colors_count = len(set(frame_colors))
            hiden_file.insert("1.0", f"Кадр {frame.tell()} содержит {unique_frame_colors_count} уникальных цветов.  ")

            # Сравниваем цвета кадра с глобальной палитрой
            matching_colors_count = len(set(global_palette_colors) & set(frame_colors))
            hiden_file.insert("1.0", f"Кадр {frame.tell()} содержит {matching_colors_count} совпадающих цветов с глобальной палитрой.  ")

            # Проверяем на сокрытие
            if unique_palette_colors_count > unique_frame_colors_count:
                hiden_file.insert("1.0", f"Возможно сокрытие.  ")
            else:
                hiden_file.insert("1.0", f"Сокрытие не обнаружено.  ")


def GIF_dop_blok():
    src = carrier.get("1.0", END)
    gif = Image.open(src[:-1], 'r')

    # Получаем блоки комментариев из файла
    comment_blocks = gif.info.get("comment")

    # Если блоков комментариев нет, устанавливаем размеры в 0
    if comment_blocks is None:
        hiden_file.delete("1.0", END)
        hiden_file.insert("1.0", f"Нет блоков")
    else:
        # Первый блок комментариев — это оригинальный блок комментариев
        original_comment_size = len(comment_blocks[0])

        # Дополнительный блок комментариев — это конкатенация всех блоков комментариев после первого
        additional_comment = "".join(comment_blocks[1:])

        # Размер дополнительного блока комментариев — это общий размер блоков комментариев за вычетом размера оригинального блока комментариев
        additional_comment_size = len(additional_comment)

        # Общий размер всех блоков комментариев
        total_comment_size = sum(len(block) for block in comment_blocks)

    if additional_comment_size == 0:
        hiden_file.delete("1.0", END)
        hiden_file.insert("1.0", f"Сокрытие не обнаружено. Размер доп блока комментария: {additional_comment_size} байт, Общий размер всех блоков комментариев: {total_comment_size} байт")
    else:
        hiden_file.delete("1.0", END)
        hiden_file.insert("1.0", f"Сокрытие обнаружено. Размер доп блока комментария: {additional_comment_size} байт, Общий размер всех блоков комментариев: {total_comment_size} байт")

b1 = Button(text = "Выбор контейнера",width = 15, height = 1)
b1.config(command = open_carrier)
b1.place(x = 10,y = 120)


b2 = Button(text = "Стегоанализ методом Хи-квадрат гистограмма",width = 37, height = 1)
b2.config(command = XI_gistogramm)
b2.place(x = 370,y = 27)

b3 = Button(text = "Стегоанализ методом Хи-квадрат сравнение",width = 37, height = 1)
b3.config(command = XI_sravnenie)
b3.place(x = 370,y = 87)

b4 = Button(text = "Стеганоанализ метода Коха-Жао",width = 30, height = 1)
b4.config(command = Koh_Jao)
b4.place(x = 400,y = 137)

b5 = Button(text = "Стеганоанализ метода палитры",width = 30, height = 1)
b5.config(command = GIF_palitra)
b5.place(x = 400,y = 187)

b6 = Button(text = "Стеганоанализ метода доп блока",width = 30, height = 1)
b6.config(command = GIF_dop_blok)
b6.place(x = 400,y = 237)

window.mainloop()
