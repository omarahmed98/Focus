import cv2 as cv
import numpy as np
import dlib
import math

# variables
fonts = cv.FONT_HERSHEY_COMPLEX




# colors
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)



# to detect faces
detectFace = dlib.get_frontal_face_detector()
# landmarks detector
predictor = dlib.shape_predictor("Predictor/shape_predictor_68_face_landmarks.dat")


def midpoint(pts1, pts2):
    """
    calculate the middle of two points in x and y directions
    pts1: point one carry the value of x and y
    pts1: point two carry the value of x and y
    return: the middle of x and y of two points
    """
    x, y = pts1
    x1, y1 = pts2
    xOut = int((x + x1) / 2)
    yOut = int((y1 + y) / 2)
    # print(xOut, x, x1)
    return (xOut, yOut)



def faceDetector(image, gray, Drawing=True):
    """
    measure the coordinates of the face on the image
    image: the image which I would to detect face from
    gray: the gray image which I would to detect face from
    Drawing: if true draw rectangle for coordinates
    return: the image , detected face
    """
    cord1 = (0, 0)  # coordinate 1
    cord2 = (0, 0)  # coordinate 2
    # getting faces detected
    faces = detectFace(gray)
    face = None

    for face in faces:
        cord1 = (face.left(), face.top())  # get left and top coordinates
        cord2 = (face.right(), face.bottom())  # get right and bottom coordinates

        # draw rectangle if draw is True.
        if Drawing == True:
            cv.rectangle(image, cord1, cord2, BLUE, 1)
    return image, face





def eucaldainDistance(pts1, pts2):
    """
    calculate the eculidian distance of two points in x and y directions
    pts1: point one carry the value of x and y
    pts1: point two carry the value of x and y
    return: the eculedian distance of two points
    """
    x, y = pts1
    x1, y1 = pts2
    eucaldainDist = math.sqrt((x1 - x) ** 2 + (y1 - y) ** 2)

    return eucaldainDist

def blinkDetector(eyePoints):
    """
    track the eye to detect the blincks and the position through the video
    eyePoints: the points of top and bottom eyes
    return: the ratio of all of blincks, top middle and bottom midle.
    """
    top = eyePoints[1:3]  # points of top eye
    bottom = eyePoints[4:6]  # points of bottom eye
    topMid = midpoint(top[0], top[1])
    bottomMid = midpoint(bottom[0], bottom[1])
    # get the actual width and height eyes
    VDistance = eucaldainDistance(topMid, bottomMid)  # get vertical distance
    HDistance = eucaldainDistance(eyePoints[0], eyePoints[3])  # get horizontal distance
    blinkingRatio = (HDistance / (VDistance+0.00001))
    return blinkingRatio, topMid, bottomMid




def landmarkDetector(image, gray, face):
    """
    get all landmarks of face including eye landmark
    image: the image which I would to get landmark from
    gray: the gray image which I would to get landmark from
    face: detected face in image
    return: the image , points of land mark
    """
    landmarks = predictor(gray, face)
    points = []
    for n in range(0, 68):
        pointposition = (landmarks.part(n).x, landmarks.part(n).y)
        # get position of points
        points.append(pointposition)
    return image, points




def Position(ValuesList):
    """
    get the action which the eye aleady did
    valuesList: the list of value of the eye coordinates
    return: the status of the eye and color rerpesenting each state
    """
    maxIndex = ValuesList.index(max(ValuesList))
    posEye = ''
    color = [BLACK,WHITE]
    if maxIndex == 0:
        posEye = "Right"
        color = [BLACK, WHITE]
    elif maxIndex == 1:
        posEye = "Center"
        color = [BLACK, WHITE]
    elif maxIndex == 2:
        posEye = "Left"
        color = [BLACK, WHITE]
    else:
        posEye = "Eye Closed"
        color = [BLACK, WHITE]
    return posEye, color


def EyeTracking(image, gray, eyePoints):
    """
    track the eye so we could get the position to know the state of the student Right,Lft or Center.
    image: the image which I would to get position of eye from
    gray: the gray image which I would to get position of eye from
    eyePoints: the points of eye which I want to concern on
    return: mask of the dimension of the image, state of the eye, color presenting the state
    """
    dimension = gray.shape
    mask = np.zeros(dimension, dtype=np.uint8)
    # convert eyePoints into arrays.
    pointsarr = np.array(eyePoints, dtype=np.int32)
    # Fill the Eyes with white color
    cv.fillPoly(mask, [pointsarr], 255)
    # apply mask and get eyeimage
    eyeImage = cv.bitwise_and(gray, gray, mask=mask)

    # get the max and min points of eye to crop eye from eyeimage
    minX = (min(eyePoints, key=lambda item: item[0]))[0]
    maxX = (max(eyePoints, key=lambda item: item[0]))[0]
    minY = (min(eyePoints, key=lambda item: item[1]))[1]
    maxY = (max(eyePoints, key=lambda item: item[1]))[1]
    # eye area will be black - make other white
    eyeImage[mask == 0] = 255
    eye = eyeImage[minY:maxY, minX:maxX]
    height, width = eye.shape
    divWidth = int(width / 3)
    pos=None
    color=WHITE

    ret, thresholdEye = cv.threshold(eye, 100, 255, cv.THRESH_BINARY)
    # divide eye width into 3 parts
    if(len(thresholdEye)):
        rightPart = thresholdEye[0:height, 0:divWidth]
        centerPart = thresholdEye[0:height, divWidth:divWidth + divWidth]
        leftPart = thresholdEye[0:height, divWidth + divWidth:width]
        # count Black pixel in each part.
        rightBlackPixels = np.sum(rightPart == 0)
        centerBlackPixels = np.sum(centerPart == 0)
        leftBlackPixels = np.sum(leftPart == 0)
        pos, color = Position([rightBlackPixels, centerBlackPixels, leftBlackPixels])

    return mask, pos, color
