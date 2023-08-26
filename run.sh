#!/bin/sh

poetry run python src/py-cppbuild.py --action "build" --root_path "../../." --deps "bgfx" "spdlog" "fmt" "glfw3"
