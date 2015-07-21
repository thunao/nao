import cv2
import numpy as np

board_w = 5 # number of board corners per row
board_h = 5 # number of board corners per column
square_sz = float(10)	# side length of a single board square
img_filelist = ['2.jpg', '3.jpg', '5.jpg']

def calibrateCamera(board_sz, square_sz, img_filelist):
	board_w, board_h = board_sz
	board_n = board_w * board_h
	cv2.namedWindow('Calibration', cv2.WINDOW_AUTOSIZE)
	#ALLOCATE STORAGE
	image_pts = []
	object_pts = []
	intrinsic_mat = np.zeros((3, 3), np.float32)
	distortion_coeffs = np.zeros((5), np.float32)

	board_pts = np.zeros((np.prod(board_sz), 3), np.float32)
	board_pts[:,:2] = np.indices(board_sz).T.reshape(-1, 2)
	board_pts *= square_sz

	img_h, img_w = 0, 0
	#GET CORNERS
	for img in img_filelist:
		image = cv2.imread(img, cv2.IMREAD_COLOR)
		img_h, img_w = image.shape[:2]
		#Find chessboard corners
		found, corners = cv2.findChessboardCorners(
			image, board_sz, None,
			cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_FILTER_QUADS)
		if corners is None:
			print img, 'Bad input'
			continue

		#Get subpixel accuracy on those corners
		gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
		cv2.cornerSubPix(gray_image, corners, (11, 11), (-1, -1),
			(1 | 2, 30, 0.1)) # criteria params|= =|

		#Draw it
		cv2.drawChessboardCorners(image, board_sz, corners, found)
		cv2.imshow('Calibration', image)
		cv2.waitKey(2000)

		#Add a good board to our data
		if found:
			image_pts.append(corners.reshape(-1, 2))
			object_pts.append(board_pts)
			print img, 'Good image'

	# print image_pts
	# print object_pts
	if len(image_pts) == 0:
		print 'no valid input image'
		return None

	#Initialize the two focal lengths in the intrinsic matrix
	intrinsic_mat[0][0] = intrinsic_mat[1][1] = 1.0

	#CALIBRATE THE CAMERA
	retval, intrinsic_mat, distortion_coeffs, rvecs, tvecs = cv2.calibrateCamera(
		object_pts, image_pts, (img_w, img_h), intrinsic_mat, distortion_coeffs,
		flags = cv2.CALIB_FIX_ASPECT_RATIO)
	print 'Re-projection error', retval
	print 'Intrinsic matrix\n', intrinsic_mat
	print 'Distortion coeffs\n', distortion_coeffs
	print 'Rotation vector\n', rvecs
	print 'Translation vector\n', tvecs
	#Save the results
	np.save('CameraMatrix.npy', intrinsic_mat)
	np.save('DistCoeffs.npy', distortion_coeffs)

	cv2.destroyAllWindows()
	return intrinsic_mat

def saveCameraMatrix():
	cameraMatrix = calibrateCamera((board_w, board_h), square_sz, img_filelist)
	f = open('___.py', 'w')
	f.write('matM = ' + str(cameraMatrix.tolist()))
	f.close()

if __name__ == '__main__':
	saveCameraMatrix()