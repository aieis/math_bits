#include "zentangle.h"

#include <cstdio>
#include <cmath>
#include <math.h>

#include <opencv2/core.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>


Point transform_point(Point p, double rotation, Point translation)
{
    double C = std::cos(rotation);
    double S = std::sin(rotation);
    double x = p.x * C - p.y * S + translation.x;
    double y = p.x * S + p.y * C + translation.y;
    return {x, y};
}


Point linear_interp(Point p1, Point p2, double alpha)
{
    double x = (p2.x - p1.x) * alpha + p1.x;
    double y = (p2.y - p1.y) * alpha + p1.y;
    return {x, y};
}


Polygon next_polygon(Polygon pol, double alpha)
{
    std::vector<Point> nverts;
    for (int i = 0; i < pol.vertices.size(); i++) {
        Point p1 = pol.vertices[i];
        Point p2 = pol.vertices[(i + 1) % pol.vertices.size()];
        nverts.push_back(linear_interp(p1, p2, alpha));
    }

    return {nverts};
}

void draw_polygon(cv::Mat& im, Polygon pol)
{
    int h = im.rows;
    
    for (int i = 0; i < pol.vertices.size(); i++) {
        Point p1 = pol.vertices[i];
        Point p2 = pol.vertices[(i + 1) % pol.vertices.size()];
        cv::line(im, {static_cast<int>(p1.x), static_cast<int>(h - p1.y)}, {static_cast<int>(p2.x), static_cast<int>(h - p2.y)}, {0, 0, 0, 255}, 3);
    }        
}

Polygon regular_polygon(int n, int dim)
{
    const double pi = M_PI;
    double avl = 0.8 * dim;
    double l = avl * pi / n;
    double x = (dim - l) / 2;
    double y = (dim - avl) / 2;
    Point sp = {x, y};

    std::vector<Point> vertices;
    vertices.push_back(sp);

    double omega = pi * (n - 2) / n;

    for (int i = 1; i < n; i++) {
        Point p1 = vertices[i-1];

        Point p2 = {l, 0};
        p2 = transform_point(p2, (i-1) * (pi - omega), p1);

        vertices.push_back(p2);
    }

    return {vertices};
}

cv::Mat zentangle(Polygon pol, double alpha, int num, int dim)
{
    std::vector<Polygon> polys;
    polys.push_back(pol);
    for (int i = 1; i < num; i++) {
        polys.push_back(next_polygon(polys[i-1], alpha));
    }

    cv::Mat im(dim, dim, CV_8UC4, {255, 255, 255, 255});
    for (auto && pol : polys) {
        draw_polygon(im, pol);
    }

    return im;
}



struct UserData {
    std::vector<Point> vertices;
    double cx = 0;
    double cy = 0;
    int h;
};

void callback(int  event, int  x, int  y, int  flag, void *param) {


    UserData* data = (UserData*) param;

    if (event == cv::EVENT_LBUTTONUP) {
        data->vertices.push_back({static_cast<double>(x), static_cast<double>(data->h - y)});
    }

    else if (event == cv::EVENT_RBUTTONUP) {
        data->vertices.pop_back();
    }

    else if (event == cv::EVENT_MOUSEMOVE) {
        data->cx = x;
        data->cy = data->h - y;
    }
};

Polygon input_polygon(int dim)
{
    int h = dim;
    cv::Mat im(dim, dim, CV_8UC3, {255, 255, 255});

    std::vector<Point> vertices;
    double cx = 0;
    double cy = 0;

    UserData d {vertices, cx, cy, h};    
    
    const char* winname = "polygon drawing window";
    cv::namedWindow(winname, cv::WINDOW_GUI_NORMAL);
    cv::setWindowTitle(winname, "Draw your polygon!");
    cv::setMouseCallback(winname, callback, (void*) &d);

    while (true) {
        while (true) {
            cv::Mat drw = im.clone();
            vertices = d.vertices;

            int s = d.vertices.size();
            for (int i = 0; i < s - 1; i++) {
                Point p1 = d.vertices[i];
                Point p2 = d.vertices[(i + 1) % s];
                cv::line(drw, {static_cast<int>(p1.x), static_cast<int>(h - p1.y)}, {static_cast<int>(p2.x), static_cast<int>(h - p2.y)}, {0}, 3);
            }

            if (s > 0) {
                Point p1 = vertices[s-1];
                cv::line(drw, {static_cast<int>(p1.x), static_cast<int>(h - p1.y)}, {static_cast<int>(d.cx), static_cast<int>(h - d.cy)}, {127, 127, 127}, 3);
            }

            if (s > 1) {
                Point p1 = vertices[s-1];
                Point p2 = vertices[0];
                cv::line(drw, {static_cast<int>(p1.x), static_cast<int>(h - p1.y)}, {static_cast<int>(p2.x), static_cast<int>(h - p2.y)}, {50 , 50, 200}, 3);
            }

            cv::imshow(winname, drw);

            int k = cv::waitKey(1);

            if (k == 'y') {
                break;
            }        
        }
        
        cv::Mat drw = im.clone();
        vertices = d.vertices;

        draw_polygon(drw, {d.vertices});

        cv::imshow(winname, drw);
        cv::setWindowTitle(winname, "This is your polygon. Press 'y' to finish.");

        if(cv::waitKey(0) == 'y') {
                break;
        }

    }

    cv::destroyWindow(winname);

    return {d.vertices};
}


// int main(int argc, char** argv)
// {

//     double alpha = 0.5;
//     int num = 10;

//     Polygon pol;

//     if (argc <= 1) {
//         pol = input_polygon(1024);
//     } else {
//         pol = regular_polygon(atoi(argv[1]), 1024);    
//     }
    
//     auto im = zentangle(pol, alpha, num, 1024);
//     while (cv::waitKey(0) != 'q') {
//         cv::imshow("Zentangle", im);
//     }
// }
