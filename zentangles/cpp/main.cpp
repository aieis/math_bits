#include <stdio.h>          // printf, fprintf
#include <stdlib.h>         // abort

#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>
#define GLFW_INCLUDE_NONE
#define GLFW_INCLUDE_VULKAN
#include <GLFW/glfw3.h>
#include <vulkan/vulkan.h>

#include "imgui.h"
#include "imgui_impl_glfw.h"
#include "imgui_impl_vulkan.h"

#include "vulkan_interop.h"
#include "zentangle.h"

#if defined(_MSC_VER) && (_MSC_VER >= 1900) && !defined(IMGUI_DISABLE_WIN32_FUNCTIONS)
#pragma comment(lib, "legacy_stdio_definitions")
#endif

//#define IMGUI_UNLIMITED_FRAME_RATE
#ifdef _DEBUG
#define IMGUI_VULKAN_DEBUG_REPORT
#endif

static void check_vk_result(VkResult err)
{
    if (err == 0)
        return;
    fprintf(stderr, "[vulkan] Error: VkResult = %d\n", err);
    if (err < 0)
        abort();
}

static void glfw_error_callback(int error, const char* description)
{
    fprintf(stderr, "Glfw Error %d: %s\n", error, description);
}

int main(int, char**)
{
    
    glfwSetErrorCallback(glfw_error_callback);
    if (!glfwInit())
        return 1;

    glfwWindowHint(GLFW_CLIENT_API, GLFW_NO_API);

    const GLFWvidmode * mode = glfwGetVideoMode(glfwGetPrimaryMonitor());

    int DisplayWidth = mode->width;
    int DisplayHeight = mode->height;

    const int dim = DisplayWidth > DisplayHeight? DisplayHeight * 0.9 : DisplayWidth * 0.9;
    
    GLFWwindow* window = glfwCreateWindow(dim, dim, "Zentangle", NULL, NULL);

    // Setup Vulkan
    if (!glfwVulkanSupported())
    {
        printf("GLFW: Vulkan Not Supported\n");
        return 1;
    }

    VulkanInterface interface{};
    uint32_t extensions_count = 0;
    const char** extensions = glfwGetRequiredInstanceExtensions(&extensions_count);
    interface.SetupVulkan(extensions, extensions_count);

    // Create Window Surface
    VkSurfaceKHR surface;
    VkResult err = glfwCreateWindowSurface(interface.g_Instance, window, interface.g_Allocator, &surface);
    check_vk_result(err);

    // Create Framebuffers
    int w, h;
    glfwGetFramebufferSize(window, &w, &h);
    ImGui_ImplVulkanH_Window* wd = &interface.g_MainWindowData;
    interface.SetupVulkanWindow(wd, surface, w, h);

    // Setup Dear ImGui context
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO(); (void)io;
    io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;     // Enable Keyboard Controls
    
    
    ImGui::StyleColorsDark();
    
    ImGui_ImplGlfw_InitForVulkan(window, true);

    ImGui_ImplVulkan_InitInfo init_info = interface.makeInfo();
    ImGui_ImplVulkan_Init(&init_info, wd->RenderPass);


    int nsides = 3;
    int number_polys = 2;
    float alpha = 0.5;
    
    TextureData my_texture;
    Polygon pol = regular_polygon(nsides, dim);
    cv::Mat im = zentangle(pol, alpha, number_polys, dim);
    
    int image_size = im.cols * im.rows * 4;
    bool ret = interface.LoadTextureFromData(&my_texture, im.data, im.cols, im.rows);
    
    IM_ASSERT(ret);
    {
        VkCommandPool command_pool = wd->Frames[wd->FrameIndex].CommandPool;
        VkCommandBuffer command_buffer = wd->Frames[wd->FrameIndex].CommandBuffer;

        err = vkResetCommandPool(interface.g_Device, command_pool, 0);
        check_vk_result(err);
        VkCommandBufferBeginInfo begin_info = {};
        begin_info.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;
        begin_info.flags |= VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;
        err = vkBeginCommandBuffer(command_buffer, &begin_info);
        check_vk_result(err);

        ImGui_ImplVulkan_CreateFontsTexture(command_buffer);

        VkSubmitInfo end_info = {};
        end_info.sType = VK_STRUCTURE_TYPE_SUBMIT_INFO;
        end_info.commandBufferCount = 1;
        end_info.pCommandBuffers = &command_buffer;
        err = vkEndCommandBuffer(command_buffer);
        check_vk_result(err);
        err = vkQueueSubmit(interface.g_Queue, 1, &end_info, VK_NULL_HANDLE);
        check_vk_result(err);

        err = vkDeviceWaitIdle(interface.g_Device);
        check_vk_result(err);
        ImGui_ImplVulkan_DestroyFontUploadObjects();
    }

    ImVec4 clear_color = ImVec4(0.45f, 0.55f, 0.60f, 1.00f);

    bool show_menu = true;
    

    // Main loop
    while (!glfwWindowShouldClose(window))
    {
        glfwPollEvents();


        if (ImGui::IsKeyPressed(ImGuiKey_A)) {
            show_menu = !show_menu;
        }

        if (ImGui::IsKeyPressed(ImGuiKey_Q)) {
            break;
        }

        if (interface.g_SwapChainRebuild)
        {
            int width, height;
            glfwGetFramebufferSize(window, &width, &height);
            if (width > 0 && height > 0)
            {
                ImGui_ImplVulkan_SetMinImageCount(interface.g_MinImageCount);
                ImGui_ImplVulkanH_CreateOrResizeWindow(interface.g_Instance, interface.g_PhysicalDevice, interface.g_Device, &interface.g_MainWindowData, interface.g_QueueFamily, interface.g_Allocator, width, height, interface.g_MinImageCount);
                interface.g_MainWindowData.FrameIndex = 0;
                interface.g_SwapChainRebuild = false;
            }
        }

        ImGui_ImplVulkan_NewFrame();
        ImGui_ImplGlfw_NewFrame();
        ImGui::NewFrame();

        ImGui::SetNextWindowPos(ImVec2(0.0f, 0.0f));
        ImGui::SetNextWindowSize(ImGui::GetIO().DisplaySize);
        ImGui::PushStyleVar(ImGuiStyleVar_WindowRounding, 0.0f);
        ImGui::Begin("Window", NULL, ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoResize);
        ImGui::Image((ImTextureID)my_texture.DS, ImVec2(my_texture.Width, my_texture.Height));
        ImGui::End();
        ImGui::PopStyleVar(1);

        if (show_menu) {
            ImGui::SetNextWindowPos(ImVec2(10, 10));
            ImGui::SetNextWindowSize(ImVec2(ImGui::GetIO().DisplaySize / 3));
            ImGui::Begin("Config", NULL, ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoResize);
            ImGui::SliderFloat("Alpha", &alpha, 0.0, 1.0);
            ImGui::SliderInt("Sides", &nsides, 3, 50);
            ImGui::SliderInt("Number of Polygons", &number_polys, 1, 1000);
            ImGui::End();
        }
        

        ImGui::Render();
        ImDrawData* draw_data = ImGui::GetDrawData();
        const bool is_minimized = (draw_data->DisplaySize.x <= 0.0f || draw_data->DisplaySize.y <= 0.0f);
        if (!is_minimized)
        {
            wd->ClearValue.color.float32[0] = clear_color.x * clear_color.w;
            wd->ClearValue.color.float32[1] = clear_color.y * clear_color.w;
            wd->ClearValue.color.float32[2] = clear_color.z * clear_color.w;
            wd->ClearValue.color.float32[3] = clear_color.w;

            interface.FrameRender(wd, draw_data);
            interface.FramePresent(wd);

            Polygon pol = regular_polygon(nsides, dim);
            cv::Mat im = zentangle(pol, alpha, number_polys, dim);
            interface.UpdateTexture(&my_texture, im.data, image_size);
        }
    }

    err = vkDeviceWaitIdle(interface.g_Device);
    check_vk_result(err);
    interface.RemoveTexture(&my_texture);
    ImGui_ImplVulkan_Shutdown();
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();

    interface.CleanupVulkanWindow();
    interface.CleanupVulkan();
    
    glfwDestroyWindow(window);
    glfwTerminate();

    return 0;
}
