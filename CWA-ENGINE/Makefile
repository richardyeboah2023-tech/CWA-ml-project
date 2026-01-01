# Compiler
CC = gcc
SRC = Source/cwa_estimater.c
LIB_DIR = lib

# Detect OS
UNAME_S := $(shell uname -s)

# Default target
all: build

# Build library
build:
	@mkdir -p $(LIB_DIR)
ifeq ($(UNAME_S),Linux)
	@echo "Building for Linux..."
	$(CC) -fPIC -shared $(SRC) -o $(LIB_DIR)/libcwa.so
else ifeq ($(UNAME_S),Darwin)
	@echo "Building for macOS..."
	$(CC) -dynamiclib $(SRC) -o $(LIB_DIR)/libcwa.dylib
else ifeq ($(OS),Windows_NT)
	@echo "Building for Windows..."
	$(CC) -shared -o $(LIB_DIR)/libcwa.dll $(SRC)
else
	$(error Unsupported OS: $(UNAME_S))
endif

# Clean
clean:
ifeq ($(UNAME_S),Linux)
	rm -f $(LIB_DIR)/libcwa.so
else ifeq ($(UNAME_S),Darwin)
	rm -f $(LIB_DIR)/libcwa.dylib
else ifeq ($(OS),Windows_NT)
	del $(LIB_DIR)\libcwa.dll
endif
