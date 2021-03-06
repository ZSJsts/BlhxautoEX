#模板匹配
import cv2
import numpy as np
# 均值哈希算法
def aHash(img):
    # 缩放为8*8
    img = cv2.resize(img, (8, 8))
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # s为像素和初值为0，hash_str为hash值初值为''
    s = 0
    hash_str = ''
    # 遍历累加求像素和
    for i in range(8):
        for j in range(8):
            s = s + gray[i, j]
    # 求平均灰度
    avg = s / 64
    # 灰度大于平均值为1相反为0生成图片的hash值
    for i in range(8):
        for j in range(8):
            if gray[i, j] > avg:
                hash_str = hash_str + '1'
            else:
                hash_str = hash_str + '0'
    return hash_str


# 差值感知算法
def dHash(img):
    # 缩放8*8
    img = cv2.resize(img, (9, 8))
    # 转换灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hash_str = ''
    # 每行前一个像素大于后一个像素为1，相反为0，生成哈希
    for i in range(8):
        for j in range(8):
            if gray[i, j] > gray[i, j + 1]:
                hash_str = hash_str + '1'
            else:
                hash_str = hash_str + '0'
    return hash_str


# 感知哈希算法(pHash)
def pHash(img):
    # 缩放32*32
    img = cv2.resize(img, (32, 32))  # , interpolation=cv2.INTER_CUBIC

    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 将灰度图转为浮点型，再进行dct变换
    dct = cv2.dct(np.float32(gray))
    # opencv实现的掩码操作
    dct_roi = dct[0:8, 0:8]

    hash = []
    avreage = np.mean(dct_roi)
    for i in range(dct_roi.shape[0]):
        for j in range(dct_roi.shape[1]):
            if dct_roi[i, j] > avreage:
                hash.append(1)
            else:
                hash.append(0)
    return hash


# 通过得到RGB每个通道的直方图来计算相似度
def classify_hist_with_split(image1, image2, size=(256, 256)):
    # 将图像resize后，分离为RGB三个通道，再计算每个通道的相似值
    image1 = cv2.resize(image1, size)
    image2 = cv2.resize(image2, size)
    sub_image1 = cv2.split(image1)
    sub_image2 = cv2.split(image2)
    sub_data = 0
    for im1, im2 in zip(sub_image1, sub_image2):
        sub_data += calculate(im1, im2)
    sub_data = sub_data / 3
    return sub_data


# 计算单通道的直方图的相似值
def calculate(image1, image2):
    hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
    # 计算直方图的重合度
    degree = 0
    for i in range(len(hist1)):
        if hist1[i] != hist2[i]:
            degree = degree + (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
        else:
            degree = degree + 1
    degree = degree / len(hist1)
    return degree


# Hash值对比
def cmpHash(hash1, hash2):
    n = 0
    # hash长度不同则返回-1代表传参出错
    if len(hash1)!=len(hash2):
        return -1
    # 遍历判断
    for i in range(len(hash1)):
        # 不相等则n计数+1，n最终为相似度
        if hash1[i] != hash2[i]:
            n = n + 1
    return n


def template_demo(n):
    tpl =cv2.imread("template/"+n+".png")
    target = cv2.imread("template/target1.png")
    #cv2.namedWindow('template image', cv2.WINDOW_NORMAL)
    #cv2.imshow("template image", tpl)
    #cv2.namedWindow('target image', cv2.WINDOW_NORMAL)
    #cv2.imshow("target image", target)
    methods = [cv2.TM_SQDIFF_NORMED]   #3种模板匹配方法
    th, tw = tpl.shape[:2]
    for md in methods:
        #print(md)
        result = cv2.matchTemplate(target, tpl, md)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        #print(min_val, max_val, min_loc, max_loc)
        if md == cv2.TM_SQDIFF_NORMED:
            tl = min_loc
        else:
            tl = max_loc
        br = (tl[0]+tw, tl[1]+th)   #br是矩形右下角的点的坐标
        #print(tl,br)
        #cv2.rectangle(target, tl, br, (0, 0, 255), 2)
        #cv2.namedWindow("match-" + np.str(md), cv2.WINDOW_NORMAL)
        #cv2.imshow("match-" + np.str(md), target)
        crop_img = target[ tl[1]:br[1],tl[0]:br[0]]
        #cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        #cv2.imshow("image", crop_img)

                
        img1 = tpl  
        img2 = crop_img
        '''
        hash1 = aHash(img1)
        hash2 = aHash(img2)
        n = cmpHash(hash1, hash2)
        print('均值哈希算法相似度：', n)

        hash1 = dHash(img1)
        hash2 = dHash(img2)
        n = cmpHash(hash1, hash2)
        print('差值哈希算法相似度：', n)

        hash1 = pHash(img1)
        hash2 = pHash(img2)
        n = cmpHash(hash1, hash2)
        print('感知哈希算法相似度：', n)
        '''

        n = classify_hist_with_split(img1, img2)
        #print('三直方图算法相似度：', n)
        if n>=0.65:
            cv2.imwrite("template/target2.png",img2)
            return((int((tl[0]+br[0])/2),int((tl[1]+br[1])/2)))
        else:
            return((0,0))

if __name__=='__main__':
    print(template_demo("worldmap"))

