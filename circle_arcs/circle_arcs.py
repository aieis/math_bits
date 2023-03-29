import cv2
import numpy as np
import gradio as gr
import subprocess
import multiprocessing as mp

def launch_surf():
    cmds = ["surf", "http://127.0.0.1:7860"]
    subprocess.run(cmds, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def draw_arc(x1, y1, x2, y2, R):
    #C = ((x2 - x1) + x1**2 - x2**2 + y1**2 - y2 ** 2) / (y1 - y2)

    k = (x2 - x1) / (y1 - y2)
    d = (x1**2 - x2**2 + y1**2 - y2 ** 2) / (2*y1 - 2*y2)

    C = k
    ty1 = (y1 - d)

    a = C ** 2 + 1
    b = (-2*x1 - 2*C*ty1)
    c = (x1**2 + ty1**2 - R**2)

    print(C, k, d, a, b, c)

    print(a, b, c, (b**2 - 4 * a * c))
    x = (-b + np.sqrt(b**2 - 4*a*c)) / (2 * a)

    y = x * C + d
    print(x, y)

    
    im = np.ones((1024, 1024, 3), np.uint8) * 255

    c1 = (185, 0, 0)
    c2 = (0, 0, 185)
    c3 = (185, 0, 185)

    s = 5
    th = 3

    def draw_point(px, py, c):
        nx = px
        ny = 1024 - py
        cv2.circle(im, (nx, ny), s, c, -1)

    def draw_circle(px, py, c):
        nx = px
        ny = 1024 - py
        cv2.circle(im, (nx, ny), R, c, th)

    draw_point(x1, y1, c1)
    draw_circle(x1, y1, c1)

    draw_point(x2, y2, c2)
    draw_circle(x2, y2, c2)

    x = int(x)
    y = int(y)

    draw_point(x, y, c3)
    draw_circle(x, y, c3)

    return im


def run():
    def close_inf():
        demo.close()
        demo.clear()
        
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column():
                x1 = gr.Slider(minimum = 0, maximum = 1024, value=200)
                y1 = gr.Slider(minimum = 0, maximum = 1024, value=200)
                x2 = gr.Slider(minimum = 0, maximum = 1024, value=300)
                y2 = gr.Slider(minimum = 0, maximum = 1024, value=500)
                R =  gr.Slider(minimum = 0, maximum = 1024, value=200)

                with gr.Row():
                    cbtn = gr.Button(value="Close")
                    
            with gr.Column():
                im = gr.Image()

        x1.change(draw_arc, [x1, y1, x2, y2, R], im)
        y1.change(draw_arc, [x1, y1, x2, y2, R], im)                
        x2.change(draw_arc, [x1, y1, x2, y2, R], im)                
        y2.change(draw_arc, [x1, y1, x2, y2, R], im)                
        R.change(draw_arc, [x1, y1, x2, y2, R], im)

        demo.load(draw_arc, [x1, y1, x2, y2, R], im)
        cbtn.click(close_inf, None, None)


    proc = mp.Process(target=launch_surf)
    proc.start()

    demo.launch()
    proc.terminate()
    proc.join()
    # while cv2.waitKey(1) != ord("q"):
    #     im = draw_arc(200, 200, 300, 500, 200)
    #     cv2.imshow("circle_arcs", im)

if __name__ == "__main__":
    run()
