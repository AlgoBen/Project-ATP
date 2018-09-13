import time, threading

def thread1():
	while 1:
		print("alpha")
		time.sleep(1)

def thread2():
	while 1:
		print("bravo")
		time.sleep(1)

threading.Thread(target = thread1,).start()
threading.Thread(target = thread2,).start()