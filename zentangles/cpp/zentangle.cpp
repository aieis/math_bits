#include "zentangle.h"

#include <cstdio>
#include <cmath>
#include <functional>
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


Polygon next_polygon_lerp(Polygon pol, double alpha)
{
    std::vector<Point> nverts;
    for (int i = 0; i < pol.vertices.size(); i++) {
        Point p1 = pol.vertices[i];
        Point p2 = pol.vertices[(i + 1) % pol.vertices.size()];
        nverts.push_back(linear_interp(p1, p2, alpha));
    }

    return {nverts};
}

double prod(int start, int end, std::function<double(int i)> fn)
{
    double acc = 1;

    for (int i = start; i <= end; i++) {
        acc *= fn(i);
    }
    
    return 0;
}

Polygon next_polygon(Polygon pol, double theta)
{
    std::vector<double> zeta;
    std::vector<double> S;
    std::vector<double> A;
    std::vector<double> z;

    std::vector<double> prods;
    double S_theta = std::sin(theta);
    size_t n = pol.vertices.size();
    A.resize(n);
    S.resize(n);
    zeta.resize(n);
    z.resize(n);
    prods.resize(n);

    
    for (int i = 0; i < n; i++) {
        Point p1 = pol.vertices[i];
        Point p2 = pol.vertices[(i + 1) % n];
        Point p3 = pol.vertices[(i + 2) % n];

        Point v1 = {p2.x - p1.x, p2.y - p1.y};
        Point v2 = {p3.x - p2.x, p3.y - p2.y};

        double v1m = std::sqrt(v1.x*v1.x + v1.y * v1.y );
        double v2m = std::sqrt(v2.x*v2.x + v2.y * v2.y );

        double dp = v1.x*v2.x + v1.y * v2.y;
        
        A[i] = M_PI - std::acos(dp / (v1m * v2m));
        S[i] = v1m;
        zeta[i] = M_PI - A[i] - theta;
        prods[i] = (i == 0? 1 : prods[i-1]) * std::sin(zeta[i])/S_theta;
    }

    double znf = 1 + std::pow(-1, n+1)*std::sin(zeta[n-1])/S_theta * prods[n-2];

    double b = 0;
    
    for (int i = 0; i < n - 1; i++) {
        b += std::pow(-1, i+1) * S[i] * (i == 0? 1 : prods[i-1]);        
    }    
    
    b = S[n-1] + std::sin(zeta[n-1])/S_theta * b;

    z[n-1] = b / znf;

    for (int i = n - 2; i >= 0; i--) {
        z[i] = S[i] - (std::sin(zeta[i]) / S_theta) * z[i+1];
    }

    // printf("i | side  | angle | zeta | prods | z \n");
    // for(int i = 0; i < n; i++) {
    //     printf("%d | %f  | %f | %f | %f | %f\n", i, S[i], A[i], zeta[i], prods[i], z[i]);
    // }


    std::vector<Point> nverts;
    for (int i = 0; i < n; i++) {
        Point p1 = pol.vertices[i];
        Point p2 = pol.vertices[(i + 1) % n];
        nverts.push_back(linear_interp(p1, p2, z[i]/S[i]));
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

Polygon regular_polygon(int n, int dim, double factor)
{
    double avl = 0.8 * dim * factor;
    double l = avl * M_PI / n;
    double x = (dim - l) / 2;
    double y = (dim - avl) / 2;
    Point sp = {x, y};

    std::vector<Point> vertices;
    vertices.push_back(sp);

    double omega = M_PI * (n - 2) / n;

    for (int i = 1; i < n; i++) {
        Point p1 = vertices[i-1];

        Point p2 = {l, 0};
        p2 = transform_point(p2, (i-1) * (M_PI - omega), p1);

        vertices.push_back(p2);
    }

    return {vertices};
}



cv::Mat zentangle(Polygon pol, double theta, int num, int dim)
{
    std::vector<Polygon> polys;
    polys.push_back(pol);
    for (int i = 1; i < num; i++) {
        polys.push_back(next_polygon(polys[i-1], theta));
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
    cv::namedWindow(winname, cv::WINDOW_GUI_NORMAL | cv::WINDOW_AUTOSIZE);
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


#ifdef ZENTANGLE_MAIN
int main(int argc, char** argv)
{

    double alpha = M_PI/3 * 2.8;
    int num = 5;

    Polygon pol;

    if (argc <= 1) {
        pol = input_polygon(2048);
    } else {
        pol = regular_polygon(atoi(argv[1]), 2048, 0.5);    
    }
    
    auto im = zentangle(pol, alpha, num, 2048);
    while (cv::waitKey(0) != 'q') {
        cv::imshow("Zentangle", im);
    }
}
#endif
