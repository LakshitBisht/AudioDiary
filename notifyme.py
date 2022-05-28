from src.win10toast.win10toast import ToastNotifier
import os 
import time

def action():
    os.system("AudioDiary.exe")
    
while True:
    noti = ToastNotifier() 
    noti.show_toast('Your Personal Diary','''“Keeping a journal of what’s going on in 
    your life is a good way to help you distill what’s important and what’s not.” 
            -Martina Navratilova''',duration=5, icon_path="images\diary.ico", threaded=True,callback_on_click=action)
    time.sleep(60)