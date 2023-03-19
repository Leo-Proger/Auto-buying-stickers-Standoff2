import asyncio
import time

import cv2
import numpy
import pyautogui
import win32api
import win32con
from PIL import ImageGrab


async def check_lot_edges(screen, y1, y2):
	global continue_, count
	borders = screen[y1:y1 + 31, 0:-1]
	edges = await asyncio.to_thread(cv2.Canny, borders, 400, 300)

	non_zero_pixels = cv2.countNonZero(edges)
	if non_zero_pixels > 5:
		win32api.SetCursorPos((1390, y2))
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP, 0, 0)
		win32api.SetCursorPos((BUY_X, BUY_Y))
		await asyncio.sleep(0.05)
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP, 0, 0)
		continue_ = False
		print("Куплено!")
	else:
		if count == 2000:
			pyautogui.doubleClick(761, 306, interval=0.1)
			count = 0
		# await asyncio.sleep(0.05)
		else:
			count += 1


async def main(count_stickers):
	bbox = {
		1: (1155, 346, 1185, 941),
		2: (1125, 346, 1155, 941),
		3: (1095, 346, 1125, 941),
		4: (1065, 346, 1095, 941),
		}[count_stickers]

	while continue_:
		screen = numpy.array(await asyncio.to_thread(ImageGrab.grab, bbox=bbox))
		tasks = (check_lot_edges(screen, *coords) for coords in [
			(0, 364),
			(83, 444),
			(166, 527),
			(246, 607),
			(329, 688),
			(409, 769),
			(492, 851),
			(578, 918),
			])
		await asyncio.gather(*tasks)


count = 0
BUY_X, BUY_Y = 1072, 639
continue_ = True
asyncio.run(main(4))
