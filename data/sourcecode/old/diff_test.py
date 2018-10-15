# -*- coding: utf-8 -*-
import cv2
import numpy as np
import copy
import random
import sys
import csv

def main():

    th = 30    # 差分画像の閾値

    # カメラのキャプチャ
    cap = cv2.VideoCapture("../movie/get_file_name/test.mov")

    # フレーム数を1ずつ飛ばすためのカウンタ
    Flame_count = -1

    # CSVファイル作成
    f = open('../csv/自転車動画tests.csv', 'w')

    # 最初のフレームを背景画像に設定
    ret, bg = cap.read()
    rect = [0,0,0,0]

    while(cap.isOpened()):
        # フレームの取得
        ret,frame = cap.read()

        # フレームのカウント
        Flame_count += 1

        # カーネルの定義
        kernel = np.ones((6, 6), np.uint8)

        # マスク画像の読み込み
        mask_image = cv2.imread("../image/mask_range.png")

        # RGB画像をグレースケールへ
        mask_image_gray = cv2.cvtColor(mask_image, cv2.COLOR_BGR2GRAY)

        # 閾値処理
        diff_mask = cv2.threshold(mask_image_gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]


        # 透明チャンネル(マスク)を追加
        # ビットごとのAND演算で元画像をマスク
        im_diff = cv2.bitwise_and(frame,frame, mask=diff_mask)
        cv2.imshow("Mask_frame", frame)
        cv2.imshow("Mask_im", im_diff)

        # hsvで色指定
        hsv = cv2.cvtColor(im_diff, cv2.COLOR_BGR2HSV)
        height, width, channels = im_diff.shape[:3]
        dst = copy.copy(im_diff)

        # HSVの範囲を定義
        hsv_min = np.array([130,100,100])
        hsv_max = np.array([179,255,255])
        # hsv_min = np.array([110,100,100])
        # hsv_max = np.array([130,255,255])

        # マスク画像を用いて元画像から指定した色を抽出
        hsv_color = cv2.inRange(hsv, hsv_min, hsv_max)
        im_color = cv2.bitwise_and(im_diff,im_diff, mask=hsv_color)

        # RGB画像をグレースケールへ
        gray = cv2.cvtColor(im_color, cv2.COLOR_BGR2GRAY)

        # 閾値処理
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # 膨張処理
        gray = cv2.dilate(gray, kernel, iterations = 1)

        #輪郭を抽出し、一番大きい物を短径で囲う
        image, contours, hierarchy  = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        rects = []
        for contour in contours:
          approx = cv2.convexHull(contour)
          rect = cv2.boundingRect(approx)
          x,y,w,h = cv2.boundingRect(approx)
          rects.append(np.array(rect))

        if len(rects) > 0:
          rect = max(rects, key=(lambda x: x[2] * x[3]))
          cv2.rectangle(gray, tuple(rect[0:2]), tuple(rect[0:2] + rect[2:4]), (255, 0, 0), thickness=2)

        if Flame_count % 2 == 0:
          # 書き込み設定
          writer = csv.writer(f)

          # 配列の初期化
          row = []

          # 配列に追加
          row.append(rect[0])
          row.append(rect[1])

          # 配列をcsvに書き込み
          writer.writerow(row)

        # 結果表示
        cv2.imshow("get_contours",gray)

        # qキーが押されたら途中終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()