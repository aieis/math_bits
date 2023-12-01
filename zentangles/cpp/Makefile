DEPS=opencv4 vulkan glfw3
EINC = $(foreach D,$(DEPS),$(shell pkg-config --cflags $(D)))
ELIB = $(foreach D,$(DEPS),$(shell pkg-config --libs $(D)))

INCS = -I../../extern/imgui

CC = g++ -g
CFLAGS =  $(INCS) $(EINC)
LDFLAGS = $(ELIB)

main: main.o deps.o vulkan_interop.o zentangle.o
	$(CC) -o main main.o deps.o vulkan_interop.o zentangle.o $(LDFLAGS)

main.o: main.cpp
	$(CC) -o main.o -c main.cpp $(CFLAGS)

deps.o: inc.cpp
	$(CC) -o deps.o -c inc.cpp $(CFLAGS)

vulkan_interop.o: vulkan_interop.cpp vulkan_interop.h
	$(CC) -o vulkan_interop.o -c vulkan_interop.cpp $(CFLAGS)

zentangle.o: zentangle.cpp zentangle.h
	$(CC) -o zentangle.o -c zentangle.cpp $(CFLAGS) $(LDFLAGS)

poly: zentangle.cpp
	$(CC) -o poly zentangle.cpp $(CFLAGS) $(LDFLAGS)
