import cv2
import numpy as np
from argparse import ArgumentParser


def process_num(n, border):
    if n < 0:
        return 0
    if n > border:
        return border-1
    return round(n)


def bias(x1, y1, x2, y2, b=1):
    global height
    global width
    
    nx = (y2-y1)/(((x1-x2)**2+(y1-y2)**2)**0.5)
    ny = (x1-x2)/(((x1-x2)**2+(y1-y2)**2)**0.5)
    return process_num(x1 + nx*b, width), process_num(y1 + ny*b, height), \
           process_num(x2 + nx*b, width), process_num(y2 + ny*b, height)


def isInQuatrefoil(x, y, x1, y1, x2, y2, x3, y3):
    d = (x3 - x2) * (y1 - y2) - (x1 - x2) * (y3 - y2)
    return 0 <= (y1 - y2) * (x - x2) - (x1 - x2) * (y - y2) and \
                (y1 - y2) * (x - x2) - (x1 - x2) * (y - y2) <= d and \
           0 <= (x3 - x2) * (y - y2) - (y3 - y2) * (x - x2) and \
                (x3 - x2) * (y - y2) - (y3 - y2) * (x - x2) <= d


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--image', '-i', type=str, help='Path to image', required=True)
    parser.add_argument('--x1', type=int, help='X1 coordinate of pipe', required=True)
    parser.add_argument('--y1', type=int, help='Y1 coordinate of pipe', required=True)
    parser.add_argument('--x2', type=int, help='X2 coordinate of pipe', required=True)
    parser.add_argument('--y2', type=int, help='Y2 coordinate of pipe', required=True)
    args = vars(parser.parse_args())

    img = cv2.imread(args['image'])
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    height, width = gray.shape
    x1, y1 = args['x1'], args['y1']#524, 215
    x2, y2 = args['x2'], args['y2']#545, 0 
    lesser_bias, bigger_bias = 20, 100

    # PIPE
    pipe_x1_pos, pipe_y1_pos, pipe_x2_pos, pipe_y2_pos = bias(x1, y1, x2, y2, lesser_bias)
    pipe_x1_neg, pipe_y1_neg, pipe_x2_neg, pipe_y2_neg = bias(x1, y1, x2, y2, -1*lesser_bias)

    # ENV
    env_x1_pos, env_y1_pos, env_x2_pos, env_y2_pos = bias(x1, y1, x2, y2, bigger_bias)
    env_x1_neg, env_y1_neg, env_x2_neg, env_y2_neg = bias(x1, y1, x2, y2, -1*bigger_bias)

    value_env = []
    value_nenv = []

    for row in range(height):
        for pix in range(width):
            if isInQuatrefoil(pix, row, env_x1_neg, env_y1_neg, env_x1_pos, env_y1_pos, env_x2_pos, env_y2_pos):
                if not isInQuatrefoil(pix, row, pipe_x1_neg, pipe_y1_neg, pipe_x1_pos, pipe_y1_pos, pipe_x2_pos, pipe_y2_pos):
                    value_env.append(gray[row][pix])
            else:
                value_nenv.append(gray[row][pix])

    value_env = np.array(value_env)
    value_nenv = np.array(value_nenv)
    value_nenv.sort()
    value_nenv = value_nenv[int(len(value_nenv)*0.08):-int(len(value_nenv)*0.08)]

    print(f"Трубы нагрели окружение на {round(value_env.mean()/value_nenv.mean() * 100 - 100, 2)}%")

