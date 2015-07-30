import cv2
import numpy as np
from stereo_match import stereosgbm_match

n_boards = 5
board_w = 7
board_h = 4
square_sz = float(10.0)

def drawlines(img1, img2, lines, pts):
    ''' img1 - image on which we draw the epilines for the points in img2
        lines - corresponding epilines '''
    c = img1.shape[1]
    for r, pt in zip(lines, pts):
        color = tuple(np.random.randint(0,255,3).tolist())
        x0, y0 = map(int, [0, -r[2]/r[1]])
        x1, y1 = map(int, [c, -(r[2]+r[0]*c)/r[1]])
        img1 = cv2.line(img1, (x0, y0), (x1, y1), color, 1)
        img2 = cv2.circle(img2, tuple(pt), 4, color, -1)
    return img1,img2

def getMatchedPts():
    #ALLOCATE STORAGE
    image1_pts = []; image2_pts = []; object_pts = []
    img_h, img_w = 0, 0
    image1 = cv2.imread('L2.jpg', cv2.IMREAD_COLOR)
    image2 = cv2.imread('R2.jpg', cv2.IMREAD_COLOR)
    assert image1.shape == image2.shape
    img_h, img_w = image1.shape[:2]

    image1_pts.append((443, 89)); image2_pts.append((156, 82)); object_pts.append((0, 0, 0))
    image1_pts.append((513, 92)); image2_pts.append((226, 94)); object_pts.append((28, 0, 0))
    image1_pts.append((441, 169)); image2_pts.append((157, 164)); object_pts.append((0, 28, 0))
    image1_pts.append((511, 169)); image2_pts.append((226, 167)); object_pts.append((28, 28, 0))
    image1_pts.append((439, 247)); image2_pts.append((158, 244)); object_pts.append((0, 56, 0))
    image1_pts.append((508, 245)); image2_pts.append((226, 240)); object_pts.append((28, 56, 0))
    image1_pts.append((438, 323)); image2_pts.append((159, 322)); object_pts.append((0, 84, 0))
    image1_pts.append((507, 319)); image2_pts.append((227, 311)); object_pts.append((28, 84, 0))

    image1_pts = [np.asarray(image1_pts, np.float32)]
    image2_pts = [np.asarray(image2_pts, np.float32)]
    object_pts = [np.asarray(object_pts, np.float32)]
    return image1, image2, image1_pts, image2_pts, object_pts, (img_w, img_h)

def getMatchedPtsByChessboard(img_idx_list, board_sz, board_pts):
    #ALLOCATE STORAGE
    image1 = []; image2 = []
    image1_pts = []; image2_pts = []; object_pts = []

    img_h, img_w = 0, 0
    #GET CORNERS
    for i in img_idx_list:
        image1 = cv2.imread('L' + str(i) + '.jpg', cv2.IMREAD_COLOR)
        image2 = cv2.imread('R' + str(i) + '.jpg', cv2.IMREAD_COLOR)
        assert image1.shape == image2.shape
        img_h, img_w = image1.shape[:2]
        #Find chessboard corners
        flags = cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_FILTER_QUADS
        found1, corners1 = cv2.findChessboardCorners(
            image1, board_sz, None, flags)
        found2, corners2 = cv2.findChessboardCorners(
            image2, board_sz, None, flags)
        if (corners1 is None) or (corners2 is None):
            print i
            continue

        #Get subpixel accuracy on those corners
        criteria = (1 + 2, 30, 0.1)
        gray_image1 = cv2.cvtColor(image1, cv2.COLOR_RGB2GRAY)
        cv2.cornerSubPix(gray_image1, corners1, (11, 11), (-1, -1), criteria)
        gray_image2 = cv2.cvtColor(image2, cv2.COLOR_RGB2GRAY)
        cv2.cornerSubPix(gray_image2, corners2, (11, 11), (-1, -1), criteria)

        #Draw them
        #cv2.drawChessboardCorners(image1, board_sz, corners1, found1)
        cv2.imshow('Image 1', image1); cv2.imshow('Image 2', image2)
        cv2.waitKey(500)

        #Add a good board to our data
        if found1 and found2:
            image1_pts.append(corners1.reshape(-1, 2))
            image2_pts.append(corners2.reshape(-1, 2))
            object_pts.append(board_pts)

    return image1, image2, image1_pts, image2_pts, object_pts, (img_w, img_h)

def bouguetRectify(points1, points2, imgSize, M1, M2, D1, D2, R, T):
    R1, R2, P1, P2, Q, ROI1, ROI2 = cv2.stereoRectify(M1, D1, M2, D2, imgSize, R, T)
    map1x, map1y = cv2.initUndistortRectifyMap(M1, D1, R1, P1, imgSize, cv2.CV_32FC1)
    map2x, map2y = cv2.initUndistortRectifyMap(M2, D2, R2, P2, imgSize, cv2.CV_32FC1)
    return (map1x, map1y, map2x, map2y), Q

def hartleyRectify(points1, points2, imgSize, M1, M2, D1, D2, F = None):
    F, mask = cv2.findFundamentalMat(points1, points2, cv2.FM_RANSAC, 3, 0.99)
    #print 'mask\n', mask
    retval, H1, H2 = cv2.stereoRectifyUncalibrated(
        points1, points2, F, imgSize)
    retval, M1i = cv2.invert(M1); retval, M2i = cv2.invert(M2)
    R1, R2 = np.dot(np.dot(M1i, H1), M1), np.dot(np.dot(M2i, H2), M2)
    map1x, map1y = cv2.initUndistortRectifyMap(M1, D1, R1, M1, imgSize, cv2.CV_32FC1)
    map2x, map2y = cv2.initUndistortRectifyMap(M2, D2, R2, M2, imgSize, cv2.CV_32FC1)
    return (map1x, map1y, map2x, map2y), F

def write_ply(fn, verts, colors):
    verts = verts.reshape(-1, 3)
    colors = colors.reshape(-1, 3)
    verts = np.hstack([verts, colors])
    with open(fn, 'w') as f:
        np.savetxt(f, verts, '%f %f %f %d %d %d')

def stereoBMMatch(imgL, imgR, Q):
    gray_img1 = cv2.cvtColor(imgL, cv2.COLOR_RGB2GRAY)
    gray_img2 = cv2.cvtColor(imgR, cv2.COLOR_RGB2GRAY)
    cv2.imshow('Image 1', gray_img1); cv2.imshow('Image 2', gray_img2)
    numDisp = 128
    stereoBM = cv2.StereoBM_create(numDisp, 11)
    disp = stereoBM.compute(gray_img1, gray_img2).astype(np.float32)
    cv2.imshow('Disparity', disp / numDisp)

    #SAVE 3D POINTS
    points = cv2.reprojectImageTo3D(disp, Q)
    return disp, points

def ordered_seq(board_sz, square_sz):
    board_pts = np.zeros((np.prod(board_sz), 3), np.float32)
    board_pts[:,:2] = np.indices(board_sz).T.reshape(-1, 2)
    board_pts *= square_sz
    return board_pts

def inverted_seq(board_sz, square_sz):
    board_pts = np.zeros((np.prod(board_sz), 3), np.float32)
    w, h = board_sz
    for i in range(0, h):
        for j in range(0, w):
            board_pts[i * w + j, :] = (h - i - 1, w - j - 1, 0)
    return board_pts

def stereo_rectify(img1fn, img2fn, mapfn, qfn):
    urmaps = np.load(mapfn)
    Q = np.load(qfn)
    img1 = cv2.imread(img1fn, cv2.IMREAD_COLOR)
    img2 = cv2.imread(img2fn, cv2.IMREAD_COLOR)
    imgL = cv2.remap(img1, urmaps[0], urmaps[1], cv2.INTER_LINEAR)
    imgR = cv2.remap(img2, urmaps[2], urmaps[3], cv2.INTER_LINEAR)
    cv2.imshow('Image L', imgL); cv2.imshow('Image R', imgR)
    cv2.waitKey(0)
    return imgL, imgR, Q

def stereoCalibrate():
    board_n = board_w * board_h
    board_sz = (board_w, board_h)
    # cv2.namedWindow('Stereo Calibration', cv2.WINDOW_AUTOSIZE)

    board_pts = inverted_seq(board_sz, square_sz)

    image1, image2, image1_pts, image2_pts, object_pts, imgSize = getMatchedPtsByChessboard(
        [3], board_sz, board_pts)
    #image1, image2, image1_pts, image2_pts, object_pts, imgSize = getMatchedPts()
    # print image1_pts, image2_pts, object_pts, imgSize

    cameraMatrix1 = np.identity(3, np.float32); cameraMatrix2 = np.identity(3, np.float32)
    distCoeffs1 = np.zeros((5), np.float32); distCoeffs2 = np.zeros((5), np.float32)
    #CALIBRATE THE CAMERA
    flags = cv2.CALIB_FIX_ASPECT_RATIO + cv2.CALIB_ZERO_TANGENT_DIST + cv2.CALIB_SAME_FOCAL_LENGTH
    criteria = (1 + 2, 100, 1e-5) # 1 for MAX_ITER and 2 for EPS |= =|
    retval, cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, R, T, E, F = cv2.stereoCalibrate(
        object_pts, image1_pts, image2_pts, cameraMatrix1, distCoeffs1,
        cameraMatrix2, distCoeffs2, imgSize, flags = flags, criteria = criteria)
    print 'Re-projection error', retval
    print 'Intrinsic matrix 1\n', cameraMatrix1
    print 'Intrinsic matrix 2\n', cameraMatrix2
    print 'Distortion coeffs 1\n', distCoeffs1
    print 'Distortion coeffs 2\n', distCoeffs2
    print 'Rotation matrix\n', R
    print 'Translation vector\n', T
    print 'Eigen matrix\n', E
    print 'Fundamental matrix\n', F
    cameraMatrix = cameraMatrix1
    cameraMatrix[:2,2] = (imgSize[0] / 2, imgSize[1] / 2)
    distCoeffs = np.zeros((1, 5), np.float32)
    if True:
        distCoeffs1 = distCoeffs2 = distCoeffs
        cameraMatrix1 = cameraMatrix2 = cameraMatrix
    image1 = cv2.undistort(image1, cameraMatrix1, distCoeffs1)
    image2 = cv2.undistort(image2, cameraMatrix2, distCoeffs2)
    
    #CALIBRATION QUALITY CHECK
    #Using the epipolar geometry constraint: m2' * F * m1 = 0
    assert image1_pts[0].shape == image2_pts[0].shape
    newshape = image1_pts[0].shape
    newshape = (newshape[0], 1, newshape[1])
    #Work in undistorted space (An undocumented signature is used here. @Dstray)
    image1_pts = cv2.undistortPoints(image1_pts[0].reshape(newshape, order = 'F'),
        cameraMatrix1, distCoeffs1, P = cameraMatrix1)
    image2_pts = cv2.undistortPoints(image2_pts[0].reshape(newshape, order = 'F'),
        cameraMatrix2, distCoeffs2, P = cameraMatrix2)
    points1, points2 = image1_pts.reshape(-1, 2), image2_pts.reshape(-1, 2)
    #implemented in opencv 3.0.0
    if False:
        lines1 = cv2.computeCorrespondEpilines(points2, 2, F).reshape(-1, 3)
        lines2 = cv2.computeCorrespondEpilines(points1, 1, F).reshape(-1, 3)
        image1, image2 = drawlines(image1, image2, lines1, points2)
        image2, image1 = drawlines(image2, image1, lines2, points1)
    cv2.imshow('Image 1', image1); cv2.imshow('Image 2', image2)
    cv2.waitKey(0)

    #COMPUTE AND DISPLAY RECTIFICATION
    urmaps, Q = bouguetRectify(image1_pts, image2_pts, imgSize,
        cameraMatrix1, cameraMatrix2, distCoeffs1, distCoeffs2, R, T)
    '''urmaps, F = hartleyRectify(image1_pts, image2_pts, imgSize,
        cameraMatrix1, cameraMatrix2, distCoeffs1, distCoeffs2, F)'''
    print 'Q\n', Q
    Q = np.float32([[1, 0, 0,  -0.5*imgSize[0]],
                    [0, 1, 0,  -0.5*imgSize[1]],
                    [0, 0, 0, cameraMatrix[0][0]],
                    [0, 0, 0.07,      0]])
    #Save the results
    np.save('rectmap.npy', urmaps)
    np.save('Q.npy', Q)

    #RECTIFY THE IMAGES AND FIND DISPARITY MAPS
    #Setup for finding correspondences
    img1r = cv2.remap(image1, urmaps[0], urmaps[1], cv2.INTER_LINEAR)
    img2r = cv2.remap(image2, urmaps[2], urmaps[3], cv2.INTER_LINEAR)
    cv2.imshow('Image 1', img1r); cv2.imshow('Image 2', img2r)
    cv2.waitKey(0)
    
    '''disp, points = stereoBMMatch(img1r, img2r, Q)
    colors = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)
    mask = disp > disp.min()
    points = points[mask]; colors = colors[mask]
    write_ply('_3DPoints.ply', points, colors)'''
    #stereosgbm_match(img1r, img2r, '_3DPoints.ply', Q)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    #stereoCalibrate()
    imgL, imgR, Q = stereo_rectify('L4.jpg', 'R4.jpg', 'rectmap.npy', 'Q.npy')
    stereosgbm_match(imgL, imgR, '_3DPoints.ply', Q, -50)
