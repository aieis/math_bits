import cv2
import numpy as np
import gradio as gr
import subprocess
import multiprocessing as mp

def launch_surf(q):
    cmds = ["electron http://127.0.0.1:7860"]
    s = subprocess.Popen(cmds, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    return s.pid
    
def draw_arc(x1, y1, x2, y2, R):
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


    calc_y = None
    if y1 != y2:
        k = (x2 - x1) / (y1 - y2)
        d = (x1**2 - x2**2 + y1**2 - y2 ** 2) / (2*y1 - 2*y2)

        C = k
        ty1 = (y1 - d)

        a = C ** 2 + 1
        b = (-2*x1 - 2*C*ty1)
        c = (x1**2 + ty1**2 - R**2)



        x_p = b**2 - 4*a*c
        if x_p < 0:
            return im
    
        x = (-b + np.sqrt(x_p)) / (2 * a)
        y = x * C + d

        x_c = x
        y_c = y
        calc_y = lambda in_x : int(np.sqrt(R**2 - (in_x-x_c)**2) + y_c)
    else:
        x = (x1**2 - x2**2 + y1**2 - y2**2) / (2*x1 - 2 * x2)
        y_p = R**2 - (x - x1)**2
        if y_p < 0:
            return im
        
        y = np.sqrt(y_p) + y1
        x_c = x
        y_c = y
        calc_y = lambda in_x : int(np.sqrt(R**2 - (in_x-x_c)**2) + y_c)

    x = int(x)
    y = int(y)

    for x in range(x1, x2, 5):
        draw_point(x, calc_y(x), c3)
    
    #draw_circle(x, y, c3)

    return im

def create_demo(q):
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
        cbtn.click(lambda: q.put(None), None, None)

    demo.launch()

def run():

    q = mp.Queue()
    gr_proc = mp.Process(target=create_demo, args=[q])
    gr_proc.start()

    pid = launch_surf(q)

    q.get()
    gr_proc.terminate()
    gr_proc.join()

    subprocess.Popen(["kill", f"{pid}"])

if __name__ == "__main__":
    run()
