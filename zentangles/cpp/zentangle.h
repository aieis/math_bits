#include <vector>
#include <opencv2/core.hpp>

struct Point
{
    double x;
    double y;
};

struct Polygon {
    std::vector<Point> vertices;
};

Polygon regular_polygon(int n, int dim);
Polygon input_polygon(int dim);
cv::Mat zentangle(Polygon pol, double alpha, int num, int dim);
