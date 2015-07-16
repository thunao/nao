import cv2
import numpy as np
import cv2.cv as cv

n_boards = 5
board_w = 8
board_h = 5
square_sz = float(1.0)

def main():
	board_n = board_w * board_h
	board_sz = (board_w, board_h)
	cv2.namedWindow('Calibration', cv2.CV_WINDOW_AUTOSIZE)
	#ALLOCATE STORAGE
	image_pts = []
	object_pts = []
	# intrinsic_mat = np.zeros((3, 3), np.float32)
	# distortion_coeffs = np.zeros((5), np.float32)

	board_pts = np.zeros((np.prod(board_sz), 3), np.float32)
	board_pts[:,:2] = np.indices(board_sz).T.reshape(-1, 2)
	board_pts *= square_sz

	img_h, img_w = 0, 0
	#GET CORNERS
	for i in range(0, n_boards):
		image = cv2.imread(str(i) + '.jpg', cv2.CV_LOAD_IMAGE_COLOR)
		img_h, img_w = image.shape[:2]
		#Find chessboard corners
		found, corners = cv2.findChessboardCorners(
			image, board_sz, None,
			cv.CV_CALIB_CB_ADAPTIVE_THRESH | cv.CV_CALIB_CB_FILTER_QUADS)
		if corners is None:
			print i
			continue

		#Get subpixel accuracy on those corners
		gray_image = cv2.cvtColor(image, cv.CV_RGB2GRAY)
		cv2.cornerSubPix(gray_image, corners, (11, 11), (-1, -1),
			(cv.CV_TERMCRIT_EPS + cv.CV_TERMCRIT_ITER, 30, 0.1))

		#Draw it
		cv2.drawChessboardCorners(image, board_sz, corners, found)
		cv2.imshow('Calibration', image)
		cv2.waitKey(500)

		#Add a good board to our data
		if found:
			image_pts.append(corners.reshape(-1, 2))
			object_pts.append(board_pts)

	# print image_pts
	# print object_pts

	#Initialize the two focal lengths in the intrinsic matrix
	# intrinsic_mat[0][0] = intrinsic_mat[1][1] = 1.0

	#CALIBRATE THE CAMERA
	retval, intrinsic_mat, distortion_coeffs, rvecs, tvecs = cv2.calibrateCamera(
		object_pts, image_pts, (img_w, img_h))
	print 'Re-projection error', retval
	print 'Intrinsic matrix\n', intrinsic_mat
	print 'Distortion coeffs\n', distortion_coeffs
	print 'Rotation vector\n', rvecs
	print 'Translation vector\n', tvecs
	cv.Save("Intrinsics.xml", cv.fromarray(intrinsic_mat))
	cv.Save("Distortion.xml", cv.fromarray(distortion_coeffs))

	cv2.destroyAllWindows()

if __name__ == '__main__':
	main()