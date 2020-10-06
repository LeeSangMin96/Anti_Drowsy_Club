'''This script detects if a person is drowsy or not,using dlib and eye aspect ratio
calculations. Uses webcam video feed as input.'''

#Import necessary libraries
from scipy.spatial import distance
from imutils import face_utils
import numpy as np
import pygame #For playing sound
import datetime
import time
import dlib
import cv2
import os
import time
from gtts import gTTS


text ="상민아 뭐해 일어나야지"

tts = gTTS(text=text, lang='ko')
tts.save("%s.mp3" % os.path.join('audio/',"tts"))
# 만들어진 tts를 aduio로 저장

#Initialize Pygame and load music
pygame.mixer.init()
pygame.mixer.music.load('audio/tts.mp3')
#pygame을 이용하여 tts.mp3틀기
#Minimum threshold of eye aspect ratio below which alarm is triggerd
EYE_ASPECT_RATIO_THRESHOLD = 0.3

#Minimum consecutive frames for which eye ratio is below threshold for alarm to be triggered
EYE_ASPECT_RATIO_CONSEC_FRAMES = 50

#COunts no. of consecutuve frames below threshold value
COUNTER = 0

#Load face cascade which will be used to draw a rectangle around detected faces.
face_cascade = cv2.CascadeClassifier("haarcascades/haarcascade_frontalface_default.xml")
# opencv는 haar-cascade 트레이너와 검출기를 모두 제공.
# 예를 들어 haar-cascade 트레이터를 이용하여 자동차에 대한 이미지들을 트레이닝 시킬 수
# 있고, 트레이닝 시킨 학습 데이터를 파일로 저장하여, 검출기를 이용하여 특정이미지에서 
# 자동차를 검출할 수 있다.

# haar-cascade 검출기는 학습데이터를 이용해서 이미지에서 특정 객체를 검출하는 역할을 함.
# 사람의 정면을얼굴과 사람 눈에 대한 haar-cascade를 가지고 있음


#This function calculates and return eye aspect ratio
def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])

    ear = (A+B) / (2*C)
    return ear

#Load face detector and predictor, uses dlib shape predictor file
detector = dlib.get_frontal_face_detector()

# 얼굴 인식용 클래스 생성(기본 제공되는 얼굴 인식 모델 사용)
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
# 인식된 얼굴에서 랜드마크 찾기위한 클래스 생성

#Extract indexes of facial landmarks for the left and right eye
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS['left_eye']
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS['right_eye']

# 비디오 캡쳐 객체를 생성
# 캠이 한개만 부착되어 있으면 0, 2개 이상이면 첫번째 웹캡은 0, 두번깨는 1로 지정 
video_capture = cv2.VideoCapture(0)

# 2초동안 프로세스를 일시정지(캠켜지는 시간을 고려)
time.sleep(2)

# 음악이 끊기지 않게 하기 위한 변수
flag=False
# 시간을 재기 위한 변수
cnt=0

while(True):
    #Read each frame and flip it, and convert to grayscale
    start=time.time() # 시간재기 시작
    ret, frame = video_capture.read() 
    # 비디오의 한 프레임씩 읽어옴. 
    frame = cv2.flip(frame,1)
    # 화면을 좌우 반전시켜줌
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # frame을 흑백으로 변환

    #Detect facial points through detector function
    faces = detector(gray, 0)

    #Detect faces through haarcascade_frontalface_default.xml
    face_rectangle = face_cascade.detectMultiScale(gray, 1.3, 5)
    now = datetime.datetime.now().strftime("%d_%H-%M-%S")
    # 날짜를 표현하는 함수(나중에 사진 캠쳐했을때 이름으로 쓸 예정)
    # d:일수, H:시간, M:분, S:초
    #datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    #Draw rectangle around each face detected
    for (x,y,w,h) in face_rectangle:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)

    #Detect facial points
    for face in faces:

        # 인식된 좌표에서 랜드마크 추출
        shape = predictor(gray, face)
        shape = face_utils.shape_to_np(shape)

        #Get array of coordinates of leftEye and rightEye
        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]

        #Calculate aspect ratio of both eyes
        leftEyeAspectRatio = eye_aspect_ratio(leftEye)
        rightEyeAspectRatio = eye_aspect_ratio(rightEye)

        eyeAspectRatio = (leftEyeAspectRatio + rightEyeAspectRatio) / 2

        #Use hull to remove convex contour discrepencies and draw eye shape around eyes
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        # THreshold만큼 눈이 감기면 졸린걸로 간주
        if(eyeAspectRatio < EYE_ASPECT_RATIO_THRESHOLD):
            COUNTER += 1
            #If no. of frames is greater than threshold frames,
            if COUNTER >= EYE_ASPECT_RATIO_CONSEC_FRAMES:
                if (not flag):
                    pygame.mixer.music.play(-1) # 종료시까지 음악 반복.
                    path="result" #사진 저장할 경로
                    cv2.putText(frame, "You are Drowsy", (160,90), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 2)
                    cv2.imwrite(os.path.join(path, str(now) + ".png"), frame)
                    # 사진 저장 이름과 경로 지정
                    flag=not flag
                cnt+=1
                if (cnt%10000000==1):
                    flag=not flag
        else:
            pygame.mixer.music.stop()
            COUNTER = 0

    #Show video feed
    cv2.imshow('Video', frame)
    if(cv2.waitKey(1) & 0xFF == ord('q')): # q를 누르면 종료
        end=time.time()
        
        break

#Finally when video capture is over, release the video capture and destroyAllWindows
video_capture.release() # 오픈한 캡쳐 객체를 해제
cv2.destroyAllWindows()

all_study_time=end-start
print('오늘의 총 공부시간은:')
print(time.strftime("%H:%M:%S", time.gmtime(all_study_time)))
