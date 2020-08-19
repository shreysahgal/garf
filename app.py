from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import cv2 as cv
import random
from uuid import uuid4
import os
from PIL import UnidentifiedImageError
from utils import (clear_tmp_dir, urlify, random_date, get_image, parse_img,
                   add_border, hconcat_resize_min, clear_comic_dir)

COMIC_FOLDER = os.path.join('static', 'comic')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = COMIC_FOLDER
Bootstrap(app)


def get_comic():
    try:
        srcs = list()
        fnames = list()
        dates = list()

        for i in range(3):
            date = random_date()
            url = urlify(date)

            srcs.append(url)
            dates.append(date.strftime("%m/%d/%y"))

            im = get_image(url)
            fname = 'tmp/img' + str(i) + '.png'
            im.save(fname)
            print(url)
            fnames.append(fname)
        panels = list()
        for i in range(len(fnames)):
            fname = fnames[i]
            info = parse_img(fname)
            img = info['img']

            j = random.randrange(0, 3)
            x, y, w, h = info['panels'][j]
            cropped = img[y:y+h, x:x+w]
            bordered = add_border(cropped)
            panels.append(bordered)

        combined = hconcat_resize_min(panels)
        comic_name = str(uuid4()) + '.jpg'
        comic_path = os.path.join(app.config['UPLOAD_FOLDER'], comic_name)
        cv.imwrite(comic_path, combined)

        return (comic_path, srcs, dates)
    except (IndexError, UnidentifiedImageError):
        return get_comic()


@app.route('/')
def index():
    clear_comic_dir()
    clear_tmp_dir()
    comic_path, srcs, dates = get_comic()
    print(comic_path)
    return render_template(
        'index.html',
        img_path=comic_path,
        srcs=srcs,
        dates=dates
    )


@app.route('/howitworks')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
