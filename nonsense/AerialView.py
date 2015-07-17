import cv2
import numpy as np
import cv2.cv as cv

n_boards = 1
board_w = 8
board_h = 5
board_sz = (board_w, board_h)
square_sz = float(1.0)

def main():
	intrinsic_mat = np.asarray(cv.Load('Intrinsics.xml'))
	distortion_coeffs = np.asarray(cv.Load('Distortion.xml'))
	print 'Intrinsic matrix\n', intrinsic_mat
	print 'Distortion coeffs\n', distortion_coeffs
	cv2.namedWindow('Aerial View', cv2.CV_WINDOW_AUTOSIZE)
	image = cv2.imread('2.jpg', cv2.CV_LOAD_IMAGE_COLOR)
	img_h, img_w = image.shape[:2]
	img_sz = (img_w, img_h)

	#Initializa rectification matrix
	map1, map2 = cv2.initUndistortRectifyMap(
		intrinsic_mat, distortion_coeffs, None, None, img_sz, cv2.CV_32FC1)

	#Rectify the image
	rec_img = cv2.remap(image, map1, map2, cv2.INTER_LINEAR)
	cv2.imshow('Aerial View', rec_img)
	cv2.imwrite('2_rec.jpg', rec_img)

	found, corners = cv2.findChessboardCorners(
		image, board_sz, None,
		cv.CV_CALIB_CB_ADAPTIVE_THRESH | cv.CV_CALIB_CB_FILTER_QUADS)
	if not corners is None:
		print len(corners)

	#Get subpixel accuracy on those corners
	gray_image = cv2.cvtColor(image, cv.CV_RGB2GRAY)
	cv2.cornerSubPix(gray_image, corners, (11, 11), (-1, -1),
		(cv.CV_TERMCRIT_EPS + cv.CV_TERMCRIT_ITER, 30, 0.1))

	#Draw it
	cv2.drawChessboardCorners(image, board_sz, corners, found)
	cv2.imshow('Calibration', image)
	cv2.waitKey(500)

	#GET THE IMAGE AND OBJECT POINTS
	obj_pts = np.zeros((4, 2), np.float32)
	img_pts = np.zeros((4, 2), np.float32)
	obj_pts[1][0] = obj_pts[3][0] = (board_w - 1) * square_sz
	obj_pts[2][1] = obj_pts[3][1] = (board_h - 1) * square_sz
	img_pts[0] = np.asarray((193, 194))
	img_pts[1] = np.asarray((472, 201))
	img_pts[2] = np.asarray((154, 312))
	img_pts[3] = np.asarray((515, 320))
	print obj_pts, img_pts

	#FIND THE HOMOGRAPHY
	H = cv2.getPerspectiveTransform(obj_pts, img_pts)
	print 'HOMOGRAPHY\n', H

	key = 0; Z = 25
	flags = cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP | cv.CV_WARP_FILL_OUTLIERS
	while not key == 27:
		H[2][2] = Z
		dct_img = cv2.warpPerspective(image, H, img_sz, None, flags)
		cv2.imshow('Aerial View', dct_img)

		if key == 2490368:
			Z += 0.5
		elif key == 2621440:
			Z -= 0.5
		key = cv2.waitKey(1000)

	cv2.destroyAllWindows()

if __name__ == '__main__':
	main()