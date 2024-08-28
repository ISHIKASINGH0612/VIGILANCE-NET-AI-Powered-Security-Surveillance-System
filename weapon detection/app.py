# import os
# import cv2
# import streamlit as st
# from ultralytics import YOLO
# import supervision as sv
# #import st_pages
# # dependencies

# model_path = 'yolov8sbest.pt'
# # the path of your YOLO model goes here

# cams = 0
# # the number of cams

# # counts the number of cameras connected to the system using some estimate 'n' by trying to open cameras
# for i in range(10):
#     cam = cv2.VideoCapture(i, cv2.CAP_DSHOW)
#     if cam.isOpened():
#         cams += 1
#         cam.release()
#     else:
#         break

# root_dir = os.getcwd()
# # the root directory for use

# # creating captures directory
# cap_dir = f"{root_dir}\\CAPTURES"
# try:
#     os.mkdir(cap_dir)
# except:
#     pass

# # create the image directories corresponding to each camera
# for i in range(cams):
#     try:
#         cam_dir = f"{cap_dir}\\CAMERA{i+1}"
#         os.mkdir(cam_dir)
#     except:
#         pass

# # some front end beautification, not much!
# st.title("Security Surviellence")
# st.subheader("automatically capture real time footage from all connected cameras to the system and monitor them for threats and such.")
# st.sidebar.text(f"available cameras in the system: {cams}")

# st.sidebar.write("---")
# st.sidebar.info("to access the security footage, click on the corresponding icons in the upper part of the sidebar.")
# st.sidebar.write("---")

# page_list = [st_pages.Page("app.py", "HomePage", "👁️")]
# # inital page list for sidebar
# #pages_from_cams = [st_pages.Page(f"{root_dir}\\pages\\camera{i}.py", f"Camera Feed {i+1}", "📹", in_section=True) for i in range(cams)]
# # wot da fuck?? emojis in strings?? man UTF rocks
# pages_from_cams = [st_pages.Page(f"{root_dir}\\pages\\camera{i}.py", f"Camera Feed {i+1}", "📹") for i in range(cams)]

# page_list.extend(pages_from_cams)
# # yea extended the page list!

# st_pages.show_pages(page_list)
# # this should work?

# num = 0
# for i in range(cams):
#     files = os.listdir(f"{cap_dir}\\CAMERA{i+1}")
#     num += len(files)
# # counts number of images

# st.metric(label="captured instances", value=num, delta=num, delta_color='inverse')





import os
import cv2
import streamlit as st
from ultralytics import YOLO
import supervision as sv
import datetime

# Constants
model_path = 'yolov8sbest.pt'
cams = 0

# Detect number of connected cameras
for i in range(10):
    cam = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if cam.isOpened():
        cams += 1
        cam.release()
    else:
        break

# Create directories for captured images
root_dir = os.getcwd()
cap_dir = os.path.join(root_dir, "CAPTURES")
os.makedirs(cap_dir, exist_ok=True)

for i in range(cams):
    cam_dir = os.path.join(cap_dir, f"CAMERA{i+1}")
    os.makedirs(cam_dir, exist_ok=True)

def process_camera(id):
    cam = cv2.VideoCapture(id, cv2.CAP_DSHOW)
    model = YOLO(model_path)
    ctr, rst = 0, False
    an1 = sv.BoundingBoxAnnotator()
    an2 = sv.LabelAnnotator()
    win = st.empty()
    images_directory = os.path.join("CAPTURES", f"CAMERA{id+1}")

    warning = st.empty()
    def reset():
        warning.write()
        cam.release()
    st.button("Reset Alerts", on_click=reset)

    st.subheader(f"This is camera {id+1}")

    try:
        while True:
            flag, frame = cam.read()
            if not flag:
                st.write(f"Camera {id} not working!")
                continue

            result = model(frame)[0]
            detections = sv.Detections.from_ultralytics(result)

            if not detections.confidence.size:
                win.image(frame)
                continue

            rst = False
            for val in detections.confidence:
                if val > 0.4:
                    ctr += 1
                    rst = True
                    break

            if not rst:
                ctr = 0
            if ctr < 5:
                win.image(frame)
                continue

            labels = [f"{model.model.names[class_id]} {confidence:.2f}" for class_id, confidence in zip(detections.class_id, detections.confidence)]
            annotated_image = an1.annotate(scene=frame, detections=detections)
            annotated_image = an2.annotate(scene=annotated_image, detections=detections, labels=labels)
            win.image(annotated_image)

            if ctr % 10 == 0:
                ts = datetime.datetime.now().strftime("_%Y-%m-%d_%H-%M-%S")
                filepath = os.path.join(images_directory, ts + ".png")
                cv2.imwrite(filepath, annotated_image)
                warning.error("ALERT! SUSPICIOUS ACTIVITY! CHECK LOGS!")
                
    finally:
        cam.release()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["HomePage"] + [f"Camera Feed {i+1}" for i in range(cams)])

# Home Page
if page == "HomePage":
    st.title("Security Surveillance")
    st.subheader("Automatically capture real-time footage from all connected cameras to the system and monitor them for threats.")
    st.sidebar.text(f"Available cameras in the system: {cams}")

    st.sidebar.write("---")
    st.sidebar.info("To access the security footage, click on the corresponding icons in the sidebar.")
    st.sidebar.write("---")

    # Count the number of captured instances
    num = 0
    for i in range(cams):
        files = os.listdir(os.path.join(cap_dir, f"CAMERA{i+1}"))
        num += len(files)

    st.metric(label="Captured Instances", value=num, delta=num, delta_color='inverse')

# Camera Feed Pages
else:
    cam_id = int(page.split()[-1]) - 1
    st.subheader(f"This is camera {cam_id+1}")
    process_camera(cam_id)
