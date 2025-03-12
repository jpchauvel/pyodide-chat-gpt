SRC_DIR := src
BUILD_DIR := build
STATIC_JS_DIR := static/js
STATIC_HTML_DIR := static/html

# Define target archive
ARCHIVE := $(BUILD_DIR)/app.tar.gz

# Phony targets
.PHONY: all clean

# Default target
all: clean $(BUILD_DIR) $(ARCHIVE) copy-js copy-html

# Create build directory if it doesn't exist
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Create tar.gz archive of source directory
$(ARCHIVE): $(BUILD_DIR)
	tar -czf $(ARCHIVE) -C $(SRC_DIR) .

# Copy contents of static/js to build directory
copy-js: $(BUILD_DIR)
	cp -r $(STATIC_JS_DIR)/* $(BUILD_DIR)/

# Copy contents of static/html to build directory
copy-html: $(BUILD_DIR)
	cp -r $(STATIC_HTML_DIR)/* $(BUILD_DIR)/

# Clean up build artifacts
clean:
	rm -rf $(BUILD_DIR)
