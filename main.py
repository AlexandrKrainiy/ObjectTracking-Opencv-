from threading import Thread

from time import sleep
import cv2
import dlib
import tkinter as tk
from tkinter import *
from tkinter import Label, Canvas
from tkinter.filedialog import askopenfile
from tkinter.ttk import *

import imutils
from PIL import Image,ImageTk
def check_point(points):
    out=[]
    for point in points:
        #to find min and max x coordinates
        if point[0]<point[2]:
            minx=point[0]
            maxx=point[2]
        else:
            minx=point[2]
            maxx=point[0]
        #to find min and max y coordinates
        if point[1]<point[3]:
            miny=point[1]
            maxy=point[3]
        else:
            miny=point[3]
            maxy=point[1]
        out.append((minx,miny,maxx,maxy))

    return out
def run():
    global corrected_point
    im=cv2.imread('selected.png')
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    im_disp = im.copy()
    im_draw = im.copy()
    window_name = "Select objects to be tracked here."
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.imshow(window_name, im_draw)

    # List containing top-left and bottom-right to crop the image.
    pts_1 = []
    pts_2 = []

    rects = []
    run.mouse_down = False

    def callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            run.mouse_down = True
            pts_1.append((x, y))
        elif event == cv2.EVENT_LBUTTONUP and run.mouse_down == True:
            run.mouse_down = False
            pts_2.append((x, y))
            print ("Object selected at [{}, {}]".format(pts_1[-1], pts_2[-1]))
        elif event == cv2.EVENT_MOUSEMOVE and run.mouse_down == True:
            im_draw = im.copy()
            cv2.rectangle(im_draw, pts_1[-1], (x, y), (255,255,255), 3)
            cv2.imshow(window_name, im_draw)

    print ("Press and release mouse around the object to be tracked. \n You can also select multiple objects.")
    cv2.setMouseCallback(window_name, callback)

    print ("Press key `d` to discard the last object selected.")
    print ("Press key `q` to quit the program.")

    while True:
        # Draw the rectangular boxes on the image
        window_name_2 = "Objects to be tracked."
        for pt1, pt2 in zip(pts_1, pts_2):
            rects.append([pt1[0],pt2[0], pt1[1], pt2[1]])
            cv2.rectangle(im_disp, pt1, pt2, (255, 255, 255), 3)
        # Display the cropped images
        cv2.namedWindow(window_name_2, cv2.WINDOW_AUTOSIZE)
        cv2.imshow(window_name_2, im_disp)
        key = cv2.waitKey(30)
        if key == ord('q'):
            # Press key `s` to return the selected points
            # cv2.destroyAllWindows()
            # point= [(tl + br) for tl, br in zip(pts_1, pts_2)]
            # corrected_point=check_point(point)
            break
        elif key == ord('d'):
            # Press ket `d` to delete the last rectangular region
            if run.mouse_down == False and pts_1:
                print ("Object deleted at  [{}, {}]".format(pts_1[-1], pts_2[-1]))
                pts_1.pop()
                pts_2.pop()
                im_disp = im.copy()
            else:
                print ("No object to delete.")
    cv2.destroyAllWindows()
    point= [(tl + br) for tl, br in zip(pts_1, pts_2)]
    corrected_point=check_point(point)
    frame=im_disp.copy()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = imutils.resize(frame, width=500)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(img)
    panelB = Label(image=img)
    panelB.image = img
    panelB.place(x=1200, y=100)
def videoLoop():
    global vimage, vflag
    while True:
        if vflag==0:
            continue
        elif vflag==2:
            break
        print("thread start")
        imag0 = imutils.resize(vimage, width=500)
        imag1 = Image.fromarray(imag0)
        imag =ImageTk.PhotoImage(imag1)
        panelC = Label(image=imag)
        panelC.configure(image=imag)
        panelC.image = imag
        panelC.place(x=20, y=100)

def tracking():
    global vimage, vflag,cap
    points = corrected_point
    img = cv2.imread('selected.png')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    tracker = [dlib.correlation_tracker() for _ in range(len(points))]
    [tracker[i].start_track(img, dlib.rectangle(*rect)) for i, rect in enumerate(points)]
    while True:
        # Read frame from device or file
        retval, img = cap.read()
        if not retval:
            break
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Update the tracker
        for i in range(len(tracker)):
            tracker[i].update(img)
            rect = tracker[i].get_position()
            pt1 = (int(rect.left()), int(rect.top()))
            pt2 = (int(rect.right()), int(rect.bottom()))
            cv2.rectangle(img, pt1, pt2, (255, 255, 255), 3)
            print("Object {} tracked at [{}, {}] \r".format(i, pt1, pt2))
        vflag = 1
        vimage=img.copy()
    vflag = 2
    cap.release()
def video_show():
    try:
        global vimage,vflag,cap
        vflag=0
        cap = cv2.VideoCapture(filename)
        cap.set(cv2.CAP_PROP_POS_FRAMES, number)
        img = cv2.imread('selected.png')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        vimage=img.copy()
        t1 = Thread(target=tracking, args=())
        t2 = Thread(target=videoLoop, args=())
        t1.start()
        t2.start()
    except:
        pass
def tkButtonCreate(text,command):
    tk.Button(window,text=text,command=command).pack()
def drasWindwo(w,h):
    window=tk.Tk()
    window.title("Object Tracking")
    window.geometry("%dx%d+0+0" %(w,h))
    window.resizable(0,0)
    return window
def Closing():
    window.destroy()
def Open_path():
    global cap,filename
    directory = askopenfile()
    filename = directory.name
    tex.delete(1.0, END)
    tex.insert(tk.END, filename)
    tex1.delete(1.0, END)
    tex1.insert(tk.END, '0')
    cap = cv2.VideoCapture(filename)
def select_frame():
    global number
    cs=str(tex1.get(1.0,END)).replace('\n','')
    try:
        number=int(cs)
        cap.set(cv2.CAP_PROP_POS_FRAMES, number)
        ret, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        save_img=frame.copy()
        img = imutils.resize(frame, width=500)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(img)
        panelA = Label(image=img)
        panelA.image = img
        panelA.place(x=600, y=100)
        cv2.imwrite('selected.png',save_img)

    except:
        pass
def main():
    global window,tex,canvas,canvas1,canvas2,tex1
    window =drasWindwo(1800,700)
    lab=Label(window,text="Path",font=('comicsans',10))
    lab.place(x=20,y=30)
    tex = tk.Text(window, height=1, width=80, font=('comicsans', 9))
    tex.place(x=55, y=30)
    OpenBtn = tk.Button(window, width=5, text='Open', fg='white', bg='purple', font=('comicsans', 10), command=Open_path)
    OpenBtn.place(x=640, y=28)
    tex1 = tk.Text(window, height=1, width=10, font=('comicsans', 9))
    tex1.place(x=750, y=30)
    viewBtn = tk.Button(window, width=5, text='Set', fg='white', bg='purple', font=('comicsans', 10),
                        command=select_frame)
    viewBtn.place(x=850, y=28)

    SetobjBtn = tk.Button(window, width=10, text='Select object', fg='white', bg='purple', font=('comicsans', 10),
                       command=run)
    SetobjBtn.place(x=1250, y=28)
    trackBtn = tk.Button(window, width=10, text='Track', fg='white', bg='purple', font=('comicsans', 10),
                          command=video_show)
    trackBtn.place(x=350, y=70)
    lab1 = Label(window, text="Video", font=('comicsans', 10))
    lab1.place(x=150, y=80)
    canvas = tk.Canvas(window, width=500, height=500,bd=2,bg='white')
    canvas.place(x=20,y=100)
    lab2 = Label(window, text="Select object", font=('comicsans', 10))
    lab2.place(x=850, y=80)
    canvas1 = tk.Canvas(window, width=500, height=500, bd=2, bg='white')
    canvas1.place(x=600, y=100)
    lab3 = Label(window, text="object selected", font=('comicsans', 10))
    lab3.place(x=1450, y=80)
    canvas2 = tk.Canvas(window, width=500, height=500, bd=2, bg='white')
    canvas2.place(x=1200, y=100)
    window.protocol('WM_DELETE_WINDOW',Closing)
    window.mainloop()

if __name__ == "__main__":
    main()