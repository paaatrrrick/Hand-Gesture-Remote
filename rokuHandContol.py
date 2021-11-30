import cv2
import mediapipe as mp
import time
import requests

#ENTER API KEY HERE
ROKU_API_KEY = 'ENTER API KEY HERE!!!!!!!'

#Build Webcam
wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)

#Define hand Recognition
mpHands = mp.solutions.hands
hands = mpHands.Hands(min_detection_confidence=0.75)
mpDraw = mp.solutions.drawing_utils

#Global Variables
FRAMES_RESET = 7
COUNTER_FRAME = 0
slopeStrLastTime = ''
historyOfMotionsArr = [0] * 33

zPointerFingerCoordinates = [0,0,0,0,0,0]

tipIds = [8,12,16,20]
highPalmIds = [5,9,13,17]

pointerTapZDistanceMin = 0.022
pointerTapZDistanceMax = 0.04
pointFramesRequired = 3
isPointerFingerUp = False

isTvOn = False

def moveTheTV(direction):
    global COUNTER_FRAME
    COUNTER_FRAME = 0

    global isTvOn
    if isTvOn:
        if direction == 'select':
            response = requests.post(ROKU_API_KEY +'/keypress/' + direction)
            print(direction)
        else:
            if direction == historyOfMotionsArr[(len(historyOfMotionsArr) -1)] and direction != 'nil':
                response = requests.post(ROKU_API_KEY +'/keypress/' + direction)
                print(direction)
    else:
        isTvOn = True
        print('turnOn')
        response = requests.post(ROKU_API_KEY + '/keypress/power')




def findHands(img, draw=True):
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            if draw:
                mpDraw.draw_landmarks(img, handLms,
                                          mpHands.HAND_CONNECTIONS)
    return img

def findPosition(img, handNo=0, draw=True):
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    lmList = []
    if results.multi_hand_landmarks:
        myHand = results.multi_hand_landmarks[handNo]
        for id, lm in enumerate(myHand.landmark):
            h, w, c = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            if id == 8:
                lmList.append([id,cx,cy,lm.z])
            else:
                lmList.append([id,cx,cy])
            if draw:
                cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

    return lmList


def leastSqrsRegressionLine(arr):
    length = 0
    nexyFirst = 0
    totalXYFirst = 0
    totalXSecond = 0
    totalYThird = 0
    nexsFourth = 0
    totalX2Fourth = 0
    for ar in arr:
        length = length + 1
        totalX2Fourth = totalX2Fourth + ar[0] * ar[0]
        totalXSecond = totalXSecond + ar[0]
        totalYThird = totalYThird + ar[1]
        totalXYFirst = totalXYFirst + (ar[0] * ar[1])
    nexyFirst = length * totalXYFirst
    nexsFourth = length * totalX2Fourth
    sqrdXSumFifth = totalXSecond * totalXSecond
    slope = (nexyFirst - (totalXSecond * totalYThird)) / (nexsFourth - sqrdXSumFifth)
    return slope




def rightCheck(lmList, motion_Path):
    shouldSwipeRight = False
    firstCheckCounterRight = 0
    for id in range (0,4):
        if lmList[tipIds[id]][1] < lmList[tipIds[id] - 3][1]:
            firstCheckCounterRight = firstCheckCounterRight + 1
    if firstCheckCounterRight == 4:
        secondCheckCounterRight = 0
        for id in range(0, 4):
            if lmList[tipIds[id]][1] < lmList[tipIds[id] - 1][1]:
                secondCheckCounterRight = secondCheckCounterRight + 1
        if secondCheckCounterRight == 4:
            motion_Path = 'right'
            shouldSwipeRight = True
            if historyOfMotionsArr[(len(historyOfMotionsArr) - 1)] == motion_Path and historyOfMotionsArr[(len(historyOfMotionsArr) - 2)] != motion_Path:
                moveTheTV(motion_Path)
    return shouldSwipeRight, motion_Path

def leftCheck(lmList, motion_Path):
    shouldSwipeLeft = False
    checkCounter = 0
    for id in range(0, 4):
        #0 is center Palm and #2 is middleThumb
        if lmList[highPalmIds[id]][1] > lmList[0][1] and lmList[highPalmIds[id]][1] > lmList[2][1]:
            checkCounter = checkCounter + 1
    if checkCounter == 4:
        motion_Path = 'left'
        shouldSwipeLeft = True
        if historyOfMotionsArr[(len(historyOfMotionsArr) - 1)] == motion_Path and historyOfMotionsArr[(len(historyOfMotionsArr) - 2)] != motion_Path:
            moveTheTV(motion_Path)
    return shouldSwipeLeft, motion_Path





def upCheck(lmList, motion_Path):
    shouldSwipeUp = False
    checkCounter = 0
    for id in range(0, 4):
        # 0 is center Palm and #2 is middleThumb
        if lmList[tipIds[id]][2] < lmList[0][2] and lmList[tipIds[id]][2] < lmList[tipIds[id]-1][2]:
            checkCounter = checkCounter + 1
    if checkCounter == 4:
        motion_Path = 'up'
        shouldSwipeUp = True
        if historyOfMotionsArr[(len(historyOfMotionsArr) - 1)] == motion_Path and historyOfMotionsArr[(len(historyOfMotionsArr) - 2)] != motion_Path:
            moveTheTV(motion_Path)
    return shouldSwipeUp, motion_Path

def downCheck(lmList, motion_Path):
    shouldSwipeDown = False
    checkCounter = 0
    for id in range(0, 4):
        # 0 is center Palm and #2 is middleThumb
        if lmList[tipIds[id]][2] > lmList[0][2]:
            checkCounter = checkCounter + 1
    if checkCounter == 4:
        motion_Path = 'down'
        shouldSwipeDown = True
        if historyOfMotionsArr[(len(historyOfMotionsArr) - 1)] == motion_Path and historyOfMotionsArr[(len(historyOfMotionsArr) - 2)] != motion_Path:
            moveTheTV(motion_Path)
    return shouldSwipeDown, motion_Path


def pointerFingerTap(zArr, motion_Path):
    shouldSelect = False
    mostRecentZ = zArr[(len(zArr) - 1)]



    if mostRecentZ < (zArr[(len(zArr) - 1 - pointFramesRequired)] - pointerTapZDistanceMin) and  mostRecentZ > (zArr[(len(zArr) - 1 - pointFramesRequired)] - pointerTapZDistanceMax):
        shouldContinue = True
        for id in range (1,10):
            if historyOfMotionsArr[(len(historyOfMotionsArr) - id)] == 'select':
                shouldContinue = False
        if shouldContinue == True:
            motion_Path = 'select'
            moveTheTV(motion_Path)

    return shouldSelect, motion_Path



while True:
    #Find Image
    print(historyOfMotionsArr)
    success, img = cap.read()
    #find Hand
    img = findHands(img)
    #lmList is an array of landmarks on the hand
    lmList = findPosition(img, draw=False)
    motion_Path = 'nil'


    if len(lmList) != 0:



        # LeastSqrd Regression Line ArrayBuilder
        leastSqrdArray = []
        for id in range(0, 4):
            x = lmList[tipIds[id]][1]
            y = lmList[tipIds[id]][2]
            leastSqrdArray.append([x, y])

        slope = leastSqrsRegressionLine(leastSqrdArray)
        slopeStr = ''

        if slope < 0.8 and slope > -0.8:
            slopeStr = 'hor'




        #DeclareMotionPath
        didTestWork, motion_Path = rightCheck(lmList, motion_Path)
        if didTestWork == False:
            didTestWork, motion_Path = leftCheck(lmList, motion_Path)

            if didTestWork == False:

                if slopeStr == 'hor' and slopeStrLastTime == 'hor':
                    didTestWork, motion_Path = upCheck(lmList, motion_Path)

                if didTestWork == False:
                    if slopeStr == 'hor' and slopeStrLastTime == 'hor':
                        didTestWork, motion_Path = downCheck(lmList, motion_Path)

                    if didTestWork == False:
                        didTestWork = False
                        fingersDownCounter = 0
                        for id in range(1, 4):
                            if lmList[tipIds[id]][2] > lmList[tipIds[id] - 2][2]:
                                fingersDownCounter = fingersDownCounter + 1
                        if fingersDownCounter == 3 and lmList[tipIds[0]][2] < lmList[tipIds[0] - 1][2]:
                            isPointerFingerUp = True
                            didTestWork, motion_Path = pointerFingerTap(zPointerFingerCoordinates, motion_Path)
                            didTestWork = True

        slopeStrLastTime = slopeStr


        #Call the Remote Move Function
        if COUNTER_FRAME == FRAMES_RESET:
            if motion_Path != 'select':
                moveTheTV(motion_Path)
        else:
            COUNTER_FRAME = COUNTER_FRAME + 1


        #Update the History of Motions Array
        historyOfMotionsArr.pop(0)
        historyOfMotionsArr.append(motion_Path)

        zPointerFingerCoordinates.pop(0)
        if isPointerFingerUp:
            zPointerFingerCoordinates.append(lmList[8][3])
        else:
            zPointerFingerCoordinates.append(0)



    #print(motion_Path)

    cv2.imshow("image", img)
    cv2.waitKey(1)



