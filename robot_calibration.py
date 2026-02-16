import cv2
import numpy as np

img_pts = np.array([
    [274, 229],
    [416, 312],
    [371, 88],
    [206, 330],
    [307, 182],
    [377, 224]
], dtype=np.float32)


robot_pts = np.array([
    [350, 0],
    [250, 50],
    [275, -75],
    [400, 50], 
    [325, -25],  
    [275, 0]
], dtype=np.float32)

# Calculate homography

H, _ = cv2.findHomography(img_pts, robot_pts, method=0)
print("Homography matrix H:")
print(H)

#define a function for mapping

def pixel_to_robot(u, v, H):
    p = np.array([u, v, 1.0], dtype=np.float32).reshape(3,1)
    pr = H @ p
    pr = pr / pr[2, 0]
    X = pr[0, 0]
    Y = pr[1, 0]

    return X, Y

# testing with one calibration point

X_pred, Y_pred = pixel_to_robot(307, 182, H)
print(f'Predicted X: {round(X_pred, 2)}, Predicted Y: {round(Y_pred, 2)}')
print(f'Expected X: 325, Expected Y: -25')
print(f'Error in X: {round(X_pred - 325, 2)}, Error in Y: {round(Y_pred + 25, 2)}')

errors = []

for i in range(len(img_pts)):
    u, v = img_pts[i]
    x_true, y_true = robot_pts[i]
    x_pred, y_pred = pixel_to_robot(u, v, H)
    error_x = x_pred - x_true
    error_y = y_pred - y_true
    errors.append((error_x, error_y))


print(f'Maximum Error: {np.max(errors):.2f} mm')

# Testing with object on the display

img = cv2.imread('img/test_image.png')

def click_event(event, u, v, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:

        X_rob, Y_rob = pixel_to_robot(u, v, H)

        print(f"Clicked at pixel: ({u}, {v}) -> Robot coordinates: ({X_rob}, {Y_rob})")

        cv2.circle(img, (u,v), 2, (0, 0, 255), -1)
        coordinates = f"({X_rob:.2f}, {Y_rob:.2f})"
        cv2.putText(img, coordinates, (int(u + 15), int(v - 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.imshow("Final Image", img)
cv2.namedWindow("Final Image")

if img is None:
    raise FileNotFoundError("img/test_image.png not found")
cv2.imshow("Final Image", img)  

# creates the window so callback can be set
cv2.setMouseCallback("Final Image", click_event)
while True:
    cv2.imshow('Final Image', img)
    key = cv2.waitKey(1) & 0xFF

    if key == 27:

        file_path = "img/final_calibrated_image.png"
        cv2.imwrite(file_path, img)
        print("Image Saved")
        break

cv2.destroyAllWindows()
