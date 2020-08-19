from PIL import Image
import requests
from io import BytesIO
import random
import datetime
import cv2 as cv
import os


def random_date():
    start_date = datetime.date(1978, 6, 19)
    end_date = datetime.date.today()

    random_number_of_days = random.randrange((end_date - start_date).days)
    rand_date = start_date + datetime.timedelta(days=random_number_of_days)

    return rand_date


def urlify(date):
    # ex. October, 1988 --> http://pt.jikos.cz/garfield/1988/10/

    url = date.strftime("http://images.ucomics.com/comics/ga/%Y/ga%y%m%d.gif")
    return url


def get_image(url):
    response = requests.get(url)
    im = Image.open(BytesIO(response.content))
    return im


def gif2png(im):
    i = 0
    pal = im.getpalette()
    try:
        while 1:
            im.putpalette(pal)
            new_im = Image.new("RGBA", im.size)
            new_im.paste(im)
            i += 1
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return new_im


def clear_comic_dir():
    root = os.path.abspath(os.path.dirname(__file__))
    tmp_dir = os.path.join(root, 'static', 'comic')
    filelist = [f for f in os.listdir(tmp_dir)]
    for f in filelist:
        os.remove(os.path.join(tmp_dir, f))


def clear_tmp_dir():
    root = os.path.abspath(os.path.dirname(__file__))
    tmp_dir = os.path.join(root, 'tmp')
    filelist = [f for f in os.listdir(tmp_dir)]
    for f in filelist:
        os.remove(os.path.join(root, 'tmp', f))


def hconcat_resize_min(im_list, interpolation=cv.INTER_CUBIC):
    h_min = max(im.shape[0] for im in im_list)
    im_list_resize = [cv.resize(
                                    im,
                                    (int(im.shape[1] * h_min / im.shape[0]),
                                     h_min),
                                    interpolation=interpolation
                                )
                      for im in im_list]
    return cv.hconcat(im_list_resize)


def add_border(img, border_size=3, padding_size=7):
    border_color = [0, 0, 0]
    padding_color = [255, 255, 255]

    bordered = cv.copyMakeBorder(
        img,
        top=border_size,
        bottom=border_size,
        left=border_size,
        right=border_size,
        borderType=cv.BORDER_CONSTANT,
        value=border_color
    )

    padded = cv.copyMakeBorder(
        bordered,
        top=padding_size,
        bottom=padding_size*6,
        left=padding_size,
        right=padding_size,
        borderType=cv.BORDER_CONSTANT,
        value=padding_color
    )

    return padded


def parse_img(fname):

    img = cv.imread(fname)
    size = list(img.shape[:2])
    size.reverse()

    infos = {
                'img': img,
                'filename': os.path.relpath(fname, 'tmp'),
                'size': size,
                'panels': []
            }

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    cv.imwrite('gray.jpg', gray)

    ret, thresh = cv.threshold(gray, 220, 225, cv.THRESH_BINARY_INV)
    contours = cv.findContours(thresh,
                               cv.RETR_EXTERNAL,
                               cv.CHAIN_APPROX_SIMPLE)
    cv.imwrite('threshold.jpg', thresh)

    contours, hierarchy = cv.findContours(thresh,
                                          cv.RETR_EXTERNAL,
                                          cv.CHAIN_APPROX_SIMPLE)[-2:]

    for contour in contours:
        arclength = cv.arcLength(contour, True)

        epsilon = 0.01 * arclength
        approx = cv.approxPolyDP(contour, epsilon, True)

        x, y, w, h = cv.boundingRect(approx)

        if w < infos['size'][0]/8 or h < infos['size'][1]/8:
            continue

        # contourSize = int(sum(infos['size']) / 2 * 0.004)
        # cv.drawContours(img, [approx], 0, (0, 0, 255), contourSize)

        panel = [x, y, w, h]
        infos['panels'].append(panel)

    if len(infos['panels']) == 0:
        infos['panels'].append([0, 0, infos['size'][0], infos['size'][1]])

    # for debugging, writes numbers on panels
    # fontRatio = sum(infos['size']) / 2 / 400
    # font = cv.FONT_HERSHEY_SIMPLEX
    # fontScale = 1 * fontRatio
    # fontColor = (0, 0, 255)
    # lineType = 2
    # n = 0
    # for panel in infos['panels']:
    #     n += 1
    #     position = (int(panel[0] + panel[2]/2), int(panel[1]+panel[3]/2))
    #     cv.putText(
    #                   img,
    #                   str(n),
    #                   position,
    #                   font, fontScale,
    #                   fontColor,
    #                   lineType
    #               )

    # cv.imwrite(fname + '-panels.jpg', img)
    return infos
