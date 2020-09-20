import cv2
import numpy as np
import copy
import time

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
start_bit = ['on','off','on','off','on','off'] # in 1 sec
temp_bit = []
read_bit = 5
ans_bit = []
stage = 'off'
kernel = np.ones((5,5))
thres = 230
t0 = time.time()
cnt = 0
reading_mode = False
show_ans = False

font = cv2.FONT_HERSHEY_SIMPLEX 
fontScale = 1

width = 20
height = 20
x = [171+width*i for i in range(len(start_bit))]
y1 = 44
box = [[(x1,y1),(x1+width-4,y1+height)] for x1 in x]

x = [25+width*i for i in range(read_bit)]
y1 = 77
box2 = [[(x1,y1),(x1+width-4,y1+height)] for x1 in x]
grey = (30,30,30)
green = (0,255,0)
red = (0,0,255)
orange = (0,100,255)
while True:
    ret, frame = cap.read()
    frameori = copy.copy(frame)
    a = (frame>thres)*1.0
    frame[:,:,:] = a[:,:,:]
    out = cv2.filter2D(frame,3,kernel)
    light = out>24
    pixel = light.sum()
    action = True if pixel>50 else False

    # start bit
    if not reading_mode:
        if action and stage=='off' and temp_bit==[]:
            stage = 'on'
            temp_bit.append('on')
            t0 = time.time()
            print('set new t0')
        if not action and stage=='on' and temp_bit != [] :
            stage = 'off'
            temp_bit.append('off')
        if action and stage=='off' and temp_bit != []:
            stage = 'on'
            temp_bit.append('on')
        if time.time()-t0 > 1.5:
            stage = 'off'
            temp_bit = []
        print(stage, temp_bit)
        if temp_bit == start_bit:
            print('start reading')
            reading_mode = True
            temp_bit = []
            t0 = time.time()
    # read data
    if reading_mode:
        temp_bit.append(action)
        if time.time()-t0 >= 2 and not show_ans:
            t0 = time.time()
            ans = sum(temp_bit)/len(temp_bit)
            ans = True if ans > 0.5 else False 
            temp_bit = []
            ans_bit.append(ans)
            
            print(action, ans_bit)
        
    
    # draw
    color_light = (0,255,0) if action else (0,100,255)
    action = 'light_on' if action else 'light_off'
    frameori[light[:,:,0]] = [255,0,255]
    canvas = cv2.putText(frameori, action, (20,25), font,  
                   fontScale, color_light, 2, cv2.LINE_AA)
    canvas = cv2.putText(canvas, 'start_bit', (20,60), font,  
                   fontScale, (255,255,0), 2, cv2.LINE_AA) 
    #box1
    if not reading_mode:
        color_start_bit = [green for i in range(len(temp_bit))]
        while len(color_start_bit) < 6:
            color_start_bit.append(red)
    else:
        color_start_bit = [green for i in range(len(start_bit))]
    for i,(st, en) in enumerate(box):
        canvas = cv2.rectangle(canvas, st, en, color_start_bit[i], -1)   


    #box2
    if reading_mode:
        color_start_bit = []
        for ans in ans_bit:
            if ans:
                color_start_bit.append(green)
            else:
                color_start_bit.append(orange)
        while len(color_start_bit) < read_bit:
            color_start_bit.append(grey)
    else:
        color_start_bit = [grey for i in range(len(start_bit))]
    for i,(st, en) in enumerate(box2):
        canvas = cv2.rectangle(canvas, st, en, color_start_bit[i], -1)  

    #show ans
    if reading_mode:
        if len(ans_bit) >= read_bit:
            if not show_ans:
                t0_reset = time.time()
            show_ans = True
            
            binary = ''
            for bol in ans_bit:
                binary += str(int(bol))
            ans = chr(int(binary, 2)+65)
            # print('ans=',ans)
            canvas = cv2.putText(canvas, ans, (585,261), font,  
                        3, (255,255,0), 5, cv2.LINE_AA)
            
        else: t0_reset = time.time()
        t_reset = time.time()-t0_reset
        print('time reset',t_reset)
        if t_reset > 3:
            print('reset')
            temp_bit = []
            ans_bit = []
            reading_mode = False
            show_ans = False

    cv2.imshow('inp',canvas)


    key = cv2.waitKey(10)
    if key == ord('a'):
        print('break')
        break
print('out')
cap.release()
cv2.destroyAllWindows()

def check_alphabet():
    for i in range(26):
        alphabet = chr(i+65)
        a = bin(i)
        binary = a[2:].zfill(5)
        print(alphabet,binary)