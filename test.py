#testing out different filters. Ignore this lol
import cv2
import numpy as np
import matplotlib as plt

img = cv2.imread('output_videos\WhatsApp Image 2024-09-15 at 21.20.04_f87b58f8.jpg')

data = np.asarray(img)

print(data.shape)

grey_img = cv2.cvtColor(data, cv2.COLOR_BGR2GRAY)
data2 = np.asarray(grey_img)
cv2.imshow('greyscale',grey_img )
print(data2.shape)

filter = (np.array([
    [-8,0,8],
    [-8,0,8],
    [-8,0,8]
], dtype = np.float32))

output = cv2.filter2D(grey_img, -1, filter)
convolved_image_uint8 = cv2.normalize(output, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

cv2.imshow('convolved image', convolved_image_uint8)
cv2.waitKey(0)
cv2.destroyAllWindows()