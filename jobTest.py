####################################################################
#                                                                  # 
#         II         II     II     IIIIIII      IIIIIIII           #
#         II          II   II      II          II                  #
#         II           IIII        IIIIIII     II                  #
#         II            II         II          II                  #
#         IIIIII        II         IIIIIII      IIIIIIII           #
#                                                                  #
#                -- Knight Online Upgrade Bot --                   #
#                                                                  #
####################################################################
from PIL import ImageGrab
import cv2 as cv
print("Opencv Version : " + cv.__version__)
import numpy as np
print("LYEC TEST")
import serial
import time
import sys
import threading
import datetime as t
ConnectOK = False
try:
    lyec_arduino = serial.Serial('COM11', 9600, timeout=.1)  ##bağlı olduğu com port değişebilir 
    ConnectOK = True
except:
    print("HID Bağlı Değil.")   
    ConnectOK = False
####################################################################
## Job List ##
####################################################################
KoStartJ = 0
LoginJ = 1
serverSelectJ = 2
NullJ = 999 ## END
####################################################################
## Item List ##
####################################################################
NotNull = -1 # boş değil fakat bu itemi tanımıyorum!!
NullItem = 0
MiddleUpScroll = 1
####################################################################
## Var List ##
####################################################################
JOBOK  = 200
JOBERR = 404
DEBUG_PRNT = True
JobListArr = ['KoStartJ','LoginJ','serverSelectJ','NullJ']
JobdCount = 0 ## yapılan iş adımı
Job = {'nextJob': 'LoginJ',
       'selectJob': 'KoStartJ',
       'backJob': 'LoginJ',
       'JobTryCount': 2}  
TempList = {'KoStartJ' : 'find/ko_icon.jpg',
            'maradon' : 'find/maradon.jpg',
            'coinref' : 'find/coinref.jpg',
            'Null' : 'find/nullinv.jpg',
            'paper_gogusluk' : 'find/paper_gogusluk.jpg',
            'paper_donluk' : 'find/paper_donluk.jpg',
            'paper_ayaklik' : 'find/paper_ayaklik.jpg',
            'paper_kolluk' : 'find/paper_kolluk.jpg',
            'paper_kafalik' : 'find/paper_kafalik.jpg',
            'mage_gogusluk' : 'find/mage_gogusluk.jpg',
            'mage_kolluk' : 'find/mage_kolluk.jpg',
            'mage_ayaklik' : 'find/mage_ayaklik.jpg'}    
searchItemArr = ['paper_gogusluk','paper_donluk','paper_ayaklik','paper_kolluk','paper_kafalik','mage_gogusluk','mage_kolluk','mage_ayaklik','Null']            
## envanterdeki item eğer biriktirilemeyen yani tek itemse itemCount değeri bu itemin upgrade değeridir ##
## EX: {'itemName' : paperPants ,'itemCount' : 4}        +4 paper donluk 
## EX: {'itemName' : MiddleUpScroll ,'itemCount' : 40}   40 adet middle class scroll
KoInventory = [[{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0}],
               [{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0}],
               [{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0}],
               [{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0},{'itemName':NullItem,'itemCount':0},{'itemName':MiddleUpScroll,'itemCount':0}]]

map_x = "0" ## bunları string olarak sakladım istenilirse dönüştürülebilir.
map_y = "0"
####################################################################
        
def JobPrnt():
    print("\n|===== JOB =====|")
    print("selectJob : " + str(Job['selectJob']))
    print("nextJob : " + str(Job['nextJob']))
    print("backJob : " + str(Job['backJob']))
    print("JobTryCount : " + str(Job['JobTryCount']))
    print("|===============| \n")

def KoInventoryPrnt():
    rowString = ""
    for column in range(0,4):
        for row in range(0,7):
            rowString = rowString + "Slot"+ str(row+1) + ": [" + str(KoInventory[column][row]['itemName']) + "," + str(KoInventory[column][row]['itemCount']) + "] || "
        print("[column"+str(column+1)+"] => "+ rowString )
        rowString = ""
    
def nextJob():
    JobdCount = JobListArr.index(Job['nextJob'])
    Job['backJob'] = Job['selectJob']
    Job['selectJob'] = Job['nextJob']
    JobdCount = JobdCount + 1 # next job
    if(JobdCount < len(JobListArr)):
        Job['nextJob'] = JobListArr[JobdCount]
    else:
        Job['nextJob'] = JobListArr[JobListArr.index('NullJ')]
    ####  DEBUG_PRNT #####
    if DEBUG_PRNT == True:
        JobPrnt() 
    ####  DEBUG_PRNT #####
    
def backJob():
    JobdCount = JobListArr.index(Job['selectJob'])
    Job['nextJob'] = Job['selectJob']
    Job['selectJob'] = Job['backJob']
    if(JobdCount != 0):
        JobdCount = JobdCount - 1 
    else:
        JobdCount = JobListArr[0]
    Job['backJob'] = JobListArr[JobdCount]        
    ####  DEBUG_PRNT #####
    if DEBUG_PRNT == True:
        JobPrnt() 
    ####  DEBUG_PRNT #####

def searchTemp(_img,temp):
    rX = 0
    rY = 0
    find = False
    try:
        gray = cv.cvtColor(_img, cv.COLOR_BGR2GRAY)
        tem = cv.imread(TempList[temp],0)
        res = cv.matchTemplate(gray,tem,cv.TM_CCOEFF_NORMED)
        loc = np.where( res >= 0.98)  
        for pt in zip(*loc[::-1]):
            rX = pt[0]
            rY = pt[1]
            find = True
    except:
        find = False
    if find == True:
        rTemp = temp
    else:
        rTemp = 'notnull'
    return [rX,rY,find,rTemp]

def doJob(sImage):
    r = JOBERR
    search = searchTemp(sImage,Job['selectJob'])
    if(search[2] == True):
         print("buldum")
    ####  DEBUG_PRNT #####
    if DEBUG_PRNT == True: 
        print("Select Job : " + str(Job['selectJob']))
    ####  DEBUG_PRNT #####
 
 
def searchItem(_selectInvImg):
    for search in range(0,len(searchItemArr)):
        rTemp = searchTemp(_selectInvImg,searchItemArr[search])
        if(rTemp[2] == True): ## bulursa döngüyü durdursun
            break;
    return(rTemp[3])
    
 
def getNullSlotCount():
    nullSlotCount = 0
    for column in range(0,4):
        for row in range(0,7):
            if(KoInventory[column][row]['itemName'] == 'Null'):
                nullSlotCount = nullSlotCount + 1
    ####  DEBUG_PRNT #####
    if DEBUG_PRNT == True: 
        print("NullSlotCount : " + str(nullSlotCount))
    ####  DEBUG_PRNT #####
    return nullSlotCount
 
def CheckInventory(_img,detail):
    grayImg = cv.cvtColor(_img, cv.COLOR_BGR2GRAY)
    r = JOBERR
    if(detail==True):  ## envanterdeki tanıdığı itemlerin upgrade değerlerine ve adetlerini kontrol eder
        pass
    else:              ## sadece envanterinde ki itemlerin yerlerini kontrol eder 
        tem = cv.imread(TempList['coinref'],0)
        w, h = tem.shape[::-1]
        res = cv.matchTemplate(grayImg,tem,cv.TM_CCOEFF_NORMED)
        loc = np.where( res >= 0.95)  
        for pt in zip(*loc[::-1]):
             r = JOBOK
             invStartY = [pt[1]+46,pt[1]+88]
             invStartX = [pt[0]-10,pt[0]+34]
             invSpaceXY = 49      
             for searchColumn in range(0,4):
                 for searchRow in range(0,7):
                    tX = [invStartX[0]+(searchRow*invSpaceXY),invStartX[1]+(searchRow*invSpaceXY)] 
                    tY = [invStartY[0]+(searchColumn*invSpaceXY),invStartY[1]+(searchColumn*invSpaceXY)]
                    target = _img[tY[0]:tY[1],tX[0]:tX[1]]
                    KoInventory[searchColumn][searchRow]['itemName'] = searchItem(target)             
    ####  DEBUG_PRNT #####
    if DEBUG_PRNT == True:
        KoInventoryPrnt() 
        print("CheckInventory : " + str(r))
    ####  DEBUG_PRNT #####
    return r

def getCoordinate(_img): ## Haritada bulunduğu kordinatı oku
    global map_x
    global map_y
    maradonOK = False
    detectMaradon = [0,0]
    digits = []
    find_d = [          ## aranacak olan digitler
    ['digits/0.png',0], ## dosya yolu , digit 
    ['digits/1.png',1],
    ['digits/2.png',2],
    ['digits/3.png',3],
    ['digits/4.png',4],
    ['digits/5.png',5],
    ['digits/6.png',6],
    ['digits/7.png',7],
    ['digits/8.png',8],
    ['digits/9.png',9]]
    pDigits =['','','','','','']
    ##### önce maradon yazısını bul #####
    grayImg = cv.cvtColor(_img, cv.COLOR_BGR2GRAY)
    tem = cv.imread(TempList['maradon'],0)
    res = cv.matchTemplate(grayImg,tem,cv.TM_CCOEFF_NORMED)
    loc = np.where( res >= 0.9)  
    for pt in zip(*loc[::-1]):
        detectMaradon[0] = pt[0] ## x kordinatı
        detectMaradon[1] = pt[1] ## y kordinatı
        maradonOK = True ## maradon yazısı bulundu
    if maradonOK == True:
        _img = _img[detectMaradon[1]:detectMaradon[1]+12,detectMaradon[0]+45:detectMaradon[0]+100] 
        digits.append(_img[0:12,0:9])
        digits.append(_img[0:12,9:16])
        digits.append(_img[0:12,16:23])
        digits.append(_img[0:12,29:36])
        digits.append(_img[0:12,36:43])
        digits.append(_img[0:12,43:50]) 
        for digi in range(6):
            c = cv.cvtColor(digits[digi], cv.COLOR_BGR2GRAY)
            for d in range(9):       
                tem = cv.imread(find_d[d][0],0)
                res = cv.matchTemplate(c,tem,cv.TM_CCOEFF_NORMED)
                loc = np.where( res >= 0.9)  ## %90 doğrulukla kontrol ediyorum bu belki biraz düşürülebilir ama hata artar.
                for pt in zip(*loc[::-1]):  
                    pDigits[digi] = (find_d[d][1])
        for h in range(6):
            if pDigits[h] == '': ## 9 digitini bulurken arada karıştırıp boş döndürüyor ondan boş dönerse 9 olarak kabul ediyorum
                pDigits[h] = '9'
        map_x = (str(pDigits[0])+str(pDigits[1])+str(pDigits[2]))
        map_y = (str(pDigits[3]) + str(pDigits[4]) + str(pDigits[5]))
    ####  DEBUG_PRNT #####
    if DEBUG_PRNT == True:
        if maradonOK == True:
            print("MAP : " + map_x+","+map_y)
        else:
            print("Maradon haritasında değil")
    ####  DEBUG_PRNT #####
    return ([map_x,map_y])

def setKey(cKey,cDelay):
    if (ConnectOK == True):
        command = "K#" + str(cKey) + "#" + str(cDelay) +  "#Y"
        send = bytes(command, encoding='utf-8')
        ####  DEBUG_PRNT #####
        if DEBUG_PRNT == True:
            print("Send Data : " + send)
        ####  DEBUG_PRNT #####
        lyec_arduino.write(send)
        time.sleep(1)
    else:
        ####  DEBUG_PRNT #####
        if DEBUG_PRNT == True:
            print("Bağlantı yok")
        ####  DEBUG_PRNT #####

def setMouse(x,y,clickdelay,clickcount):
    if (ConnectOK == True):
        command = "M#" + str(x) + "#" + str(y) + "#" + str(clickdelay) + "#" + str(clickcount) +  "#Y"
        send = bytes(command, encoding='utf-8')
        ####  DEBUG_PRNT #####
        if DEBUG_PRNT == True:
            print("Send Data : " + send)
        ####  DEBUG_PRNT #####
        lyec_arduino.write(send)
        while lyec_arduino.readline()[:-2] != b'ok!':
            if DEBUG_PRNT == True:
                print("going to coordinate...")
        ####  DEBUG_PRNT #####
        if DEBUG_PRNT == True:
            print("Mouse : OK")
        ####  DEBUG_PRNT #####
    else:
        ####  DEBUG_PRNT #####
        if DEBUG_PRNT == True:
            print("Bağlantı yok")
        ####  DEBUG_PRNT #####
    
def clearXY():
    if (ConnectOK == True):
        lyec_arduino.write(b'R')
        ####  DEBUG_PRNT #####
        if DEBUG_PRNT == True:
            print("firstMoved : false")
        ####  DEBUG_PRNT #####
    else:
        ####  DEBUG_PRNT #####
        if DEBUG_PRNT == True:
            print("Bağlantı yok")
        ####  DEBUG_PRNT #####

testimg = cv.imread('test1.jpg')

def init():
    clearXY()
    ####  DEBUG_PRNT #####
    if DEBUG_PRNT == True:
        print("init : OK!")
    ####  DEBUG_PRNT #####


if __name__ == '__main__':  ## Ana Program     
    init()
    doJob(testimg)
    #img_np = np.array(testimg) 
    #CheckInventory(testimg,False)
    #cv.imshow("test",img_np)
    #print(getCoordinate(img_np))
    #getNullSlotCount()
#    while True:
#        if cv.waitKey(1) & 0xFF == ord('q'):
#            break