import asyncio

import cv2
import numpy
import pyautogui
import win32api
import win32con
from PIL import ImageGrab


async def test_stickers(count_stickers):
	bbox = {
		1: (1155, 346, 1185, 941),
		2: (1125, 346, 1155, 941),
		3: (1095, 346, 1125, 941),
		4: (1065, 346, 1095, 941),
		}[count_stickers]

	while True:
		screen = numpy.array(await asyncio.to_thread(ImageGrab.grab, bbox=bbox))
		edges = await asyncio.to_thread(cv2.Canny, screen, 400, 300)
		cv2.imshow('screen', edges)
		cv2.waitKey(1)


async def check_lot_edges(screen, y1, y2):
	global continue_, count

	# These are the coordinates of the stickers.
	#                y1 y2       x1 x2
	borders = screen[y1:y1 + 31, 0:-1]

	# If you want, you can change the values of 400 and 300.
	edges = await asyncio.to_thread(cv2.Canny, borders, 400, 300)

	if cv2.countNonZero(edges) > 5:
		win32api.SetCursorPos((1390, y2))
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP, 0, 0)
		win32api.SetCursorPos((BUY_X, BUY_Y))

		# This doesn't need to be removed because the game has a pop-up animation confirming the purchase.
		await asyncio.sleep(0.05)
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP, 0, 0)
		continue_ = False
		print("Purchased!")
	else:
		# If you want, you can change the value of 2000 (~10 seconds) to something else.
		# I couldn't come up with a better way to do it.
		if count == 2000:
			pyautogui.doubleClick(761, 306, interval=0.1)
			count = 0
			# If you have a good and stable internet connection, you can remove or comment out this line of code.
			await asyncio.sleep(0.05)
		else:
			count += 1


async def main(count_stickers):
	# Please read the requirements regarding this.
	bbox = {
		1: (1155, 346, 1185, 941),  # These are the coordinates of the first sticker.
		2: (1125, 346, 1155, 941),  # These are the coordinates of the second sticker.
		3: (1095, 346, 1125, 941),  # These are the coordinates of the third sticker.
		4: (1065, 346, 1095, 941),  # These are the coordinates of the fourth sticker.
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
# Please read the requirements regarding this.
BUY_X, BUY_Y = 1072, 639
continue_ = True
asyncio.run(main(4))  # This is the number of stickers you want to buy with the skin.
# asyncio.run(test_stickers(1))
