import os
import requests

BASE_URL = "https://raw.githubusercontent.com/ocornut/imgui/v1.89.4"
SRC_DIR = "."

FILES = [
    "imconfig.h",
    "imgui.cpp",
    "imgui.h",
    "imgui_draw.cpp",
    "imgui_internal.h",
    "imgui_tables.cpp",
    "imgui_widgets.cpp",
    "imstb_rectpack.h",
    "imstb_textedit.h",
    "imstb_truetype.h",
    "/backends/imgui_impl_vulkan.cpp",
    "/backends/imgui_impl_vulkan.h",
    "/backends/imgui_impl_glfw.cpp",
    "/backends/imgui_impl_glfw.h",
]


for fn in FILES:
    uri = f"{BASE_URL}/{fn}"
    req = requests.get(uri)

    with open(f"{SRC_DIR}/{os.path.basename(fn)}", "w") as fd:
        fd.write(req.text)
