import asyncio
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy
import pyautogui
import pytesseract
import win32api
import win32con
from PIL import ImageGrab

# Тут я хотел, чтобы программа сама определяла окно LDPlayer и определяла пиксели уже относительно его, а не экрана
# def get_window_coordinates(title):
# 	try:
# 		window = gw.getWindowsWithTitle(title)[0]
# 		return window.left, window.top, window.width, window.height
# 	except IndexError:
# 		print(f"No window found with title: {title}")
# 		return None
#
#
# def calculate_relative_coordinates(x1, y1, x2, y2, title):
# 	window_x, window_y, window_width, window_height = get_window_coordinates(title)
# 	original_width = 1920
# 	original_height = 1050
#
# 	relative_x1 = window_x + (x1 / original_width) * window_width
# 	relative_y1 = window_y + (y1 / original_height) * window_height
# 	relative_x2 = window_x + (x2 / original_width) * window_width
# 	relative_y2 = window_y + (y2 / original_height) * window_height
#
# 	return relative_x1, relative_y1, relative_x2, relative_y2

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Путь до tesseract.exe
tesseract_config = r'--oem 3 --psm 6'


async def buy_lot(buy_lot_y):
	global to_continue

	win32api.SetCursorPos((1370, buy_lot_y))
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP, 0, 0)
	win32api.SetCursorPos((BUY_X, BUY_Y))

	await asyncio.sleep(0.05)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP, 0, 0)

	to_continue = False
	print("Purchased!")


# pyautogui.doubleClick(761, 306, interval=0.1)


async def test_stickers(count_stickers):
	bbox = {
		1: (1228, 434, 1274, 456),
		# 1: (1155, 346, 1185, 941),
		2: (1125, 346, 1155, 941),
		3: (1095, 346, 1125, 941),
		4: (1065, 346, 1095, 941),
		}[count_stickers]

	while True:
		screen = numpy.array(await asyncio.to_thread(ImageGrab.grab, bbox=bbox))
		# edges = await asyncio.to_thread(cv2.Canny, screen, 400, 300)
		cv2.imshow('screen', screen)
		cv2.waitKey(1)


def process_image(image):
	try:
		return float(pytesseract.image_to_string(image, config=tesseract_config).replace(' ', ''))
	except ValueError:
		pass


async def check_lot_price(screen, price_y1, buy_price_lot_y):
	border = screen[price_y1:price_y1 + 23, 0:-1]
	loop = asyncio.get_event_loop()

	with ThreadPoolExecutor() as executor:
		price_lot = await loop.run_in_executor(executor, process_image, border)

	try:
		if price_lot <= price:
			await buy_lot(buy_price_lot_y)
	except TypeError:
		pass


async def check_lot_edges(screen, sticker_y1, buy_sticker_lot_y, price_y1=None, price_y2=None):
	global to_continue, count

	borders = screen[sticker_y1:sticker_y1 + 31, 0:-1]

	# Создание GpuMat и загрузка изображения в память GPU
	gpu_borders = cv2.cuda_GpuMat()
	gpu_borders.upload(borders)

	# Создание GpuMat для хранения результата
	gpu_edges = cv2.cuda_GpuMat(gpu_borders.size(), cv2.CV_8UC1)

	# Применение Canny на GPU
	cv2.cuda.createCannyEdgeDetector(400, 300).detect(gpu_borders, gpu_edges)

	# Загрузка результата обратно в память CPU
	edges = gpu_edges.download()

	if cv2.countNonZero(edges) > 5:
		await buy_lot(buy_sticker_lot_y)

	else:
		if count == 10000:
			pyautogui.doubleClick(761, 306, interval=0.1)
			count = 0

			await asyncio.sleep(0.05)
		else:
			count += 1


async def main():
	bbox_price = (1228, 351, 1274, 942)

	# Я бы это сделал, но не могу по объективным причинам, если хотите, сделайте сами
	if count_stickers and price:
		...

	elif count_stickers:
		bbox = {
			1: (1155, 346, 1185, 941),
			2: (1125, 346, 1155, 941),
			3: (1095, 346, 1125, 941),
			4: (1065, 346, 1095, 941),
			}[count_stickers]

		while to_continue:
			screen_stickers = numpy.array(await asyncio.to_thread(ImageGrab.grab, bbox=bbox))
			tasks = (check_lot_edges(screen_stickers, *coords) for coords in (
				(0, 386),
				(83, 467),
				(166, 548),
				(246, 630),
				(329, 664),
				(456, 745),
				(492, 827),
				(578, 908),
				))
			await asyncio.gather(*tasks)
	elif price:
		while to_continue:
			screen_price = numpy.array(await asyncio.to_thread(ImageGrab.grab, bbox=bbox_price))
			tasks = (check_lot_price(screen_price, *coords) for coords in (
				(0, 386),
				(81, 467),
				(162, 548),
				(243, 630),
				(324, 664),
				(405, 745),
				(486, 827),
				(567, 908),
				))
			await asyncio.gather(*tasks)


count = 0
BUY_X, BUY_Y = 1073, 666
to_continue = True
count_stickers = None
price = None

params = input("Введите количество наклеек и/или цену, меньше которой надо купить лот >>> ").split()

if len(params) == 1:
	if (par := params[0]).isdigit():
		count_stickers = int(par)
	else:
		price = float(par)
else:
	count_stickers = int(params[0])
	price = float(params[1])

asyncio.run(main())
# Закомментируйте строчку выше и раскомментируйте строчку ниже, чтобы проверить, правильно ли находятся наклейки
# asyncio.run(test_stickers(1))
