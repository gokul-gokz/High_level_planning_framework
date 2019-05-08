from math import sqrt, sin, cos, acos, asin, pi

def spherical(p1, p2):
    x_dis = float(p2[0] - p1[0])
    y_dis = float(p2[1] - p1[1])
    dis = sqrt(x_dis ** 2 + y_dis ** 2)

    #p1 as origin, get the r and theta of p2
    if dis < 1:
        return [0, 0]
    else:
        # in image plane, the x is upside down
        theta = acos(x_dis/dis)
        if y_dis >= 0:
            theta = 2*pi-theta
        return [dis, theta]
