import cv2

# Method to draw boundary around the detected feature
def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, text):
    # Converting image to gray-scale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Detecting features in gray-scale image, returns coordinates, width and height of features
    features = classifier.detectMultiScale(gray_img, scaleFactor, minNeighbors)
    coords = []
    # Drawing rectangle around the feature and labeling it
    for (x, y, w, h) in features:
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        cv2.putText(img, text, (x, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 1, cv2.LINE_AA)
        coords = [x, y, w, h]
    return coords

# Method to detect the features
def detect(img, faceCascade, eyeCascade, noseCascade, mouthCascade):
    color = {"blue": (255, 0, 0), "red": (0, 0, 255), "green": (0, 255, 0), "white": (255, 255, 255)}
    coords = draw_boundary(img, faceCascade, 1.1, 10, color['blue'], "Face")
    # If feature is detected, the draw_boundary method will return the x,y coordinates and width and height of rectangle else the length of coords will be 0
    if len(coords) == 4:
        # Updating region of interest by cropping image
        roi_img = img[coords[1]:coords[1] + coords[3], coords[0]:coords[0] + coords[2]]
        # Passing roi, classifier, scaling factor, Minimum neighbours, color, label text
        draw_boundary(roi_img, eyeCascade, 1.1, 12, color['red'], "Eye")
        draw_boundary(roi_img, noseCascade, 1.1, 4, color['green'], "Nose")
        draw_boundary(roi_img, mouthCascade, 1.1, 20, color['white'], "Mouth")
    return img

# Loading classifiers
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eyeCascade = cv2.CascadeClassifier('haarcascade_eye.xml')
noseCascade = cv2.CascadeClassifier('Nariz.xml')
mouthCascade = cv2.CascadeClassifier('Mouth.xml')

# Check if cascade classifiers are loaded correctly
if faceCascade.empty() or eyeCascade.empty() or noseCascade.empty() or mouthCascade.empty():
    print("Error loading cascade classifiers")
    exit()

# Capturing real-time video stream. 0 for built-in webcams, 1 or -1 for external webcams
video_capture = cv2.VideoCapture(0)

# Check if video capture is opened
if not video_capture.isOpened():
    print("Error: Could not open video stream")
    exit()

while True:
    # Reading image from video stream
    ret, img = video_capture.read()
    if not ret:
        print("Failed to capture image")
        break
    # Call method we defined above
    img = detect(img, faceCascade, eyeCascade, noseCascade, mouthCascade)
    # Writing processed image in a new window
    cv2.imshow("Face Detection", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Releasing webcam
video_capture.release()
# Destroying output window
cv2.destroyAllWindows()
