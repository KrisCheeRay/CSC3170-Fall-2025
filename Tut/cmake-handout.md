# 📌 CMake Installation & Basic Usage Guide

> **Read this before you write or submit your assignment.**  
> Many build errors stem from misconfigured environment or misunderstandings of CMake. Follow this guide step by step.

## Installing CMake via Package Managers

### 🪟 Windows (using Chocolatey)

1. If you don’t have Chocolatey installed yet, install it first via directions at [chocolatey.org](https://chocolatey.org/install). Follow the instructions carefully, especially the part about setting execution policy:

    ```powershell
    # Open PowerShell as Administrator and set execution policy:
    Set-ExecutionPolicy AllSigned

    # Then install Chocolatey:
    Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    ```

2. Open **PowerShell as Administrator** and run:

    ```powershell
    choco install cmake
    ```

    This installs CMake and tries to add it to your system `PATH`.

3. After installation, open a new PowerShell window and run:

   ```powershell
   cmake --version
   ```

   If you see a version number, you succeeded.

> **Tip:** If "cmake is not recognized" still shows, you may need to manually add the `bin` folder of CMake to your system `PATH`. And you should also make sure you have cpp compiler (like MSVC or MinGW) installed and available in your `PATH`.

### 🍏 macOS (using Homebrew)

1. If Homebrew isn’t installed yet, visit [Homebrew’s site](https://docs.brew.sh/Installation) and follow its install instructions.

   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```


2. Open **Terminal**, then run:

   ```bash
   brew install cmake
   ```

   This installs the command-line version of CMake.

3. After installation, test with:

   ```bash
   cmake --version
   ```

   If a version prints out, you’re all set.

## Basic CMake Usage Workflow

Here’s a minimal, clean workflow you and I both can rely on:

### Project layout example

```
project-root/
├── src/
│    main.cpp
└── CMakeLists.txt
```

### Example `CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.10)
project(MyProject)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(my_executable src/main.cpp)
```

### Recommended workflow

1. run CMake to configure the project and generate build files in a separate `build/` directory:

   ```bash
   cd project-root
   cmake -S . -B build # other config options go here
   ```

   This command tells CMake to read the `CMakeLists.txt` in the project root directory and generate appropriate files for your platform (Makefiles, Xcode project, Visual Studio solution, etc.).

2. Build / compile:

   ```bash
   cmake --build build
   ```

3. Run the produced executable:

   ```bash
   cd build/bin # or wherever your executable is located
   ./my_executable
   ```

## Useful Links & References

* [CMake Official Downloads & Documentation](https://cmake.org/download/)
* [“Modern CMake” — Getting Started / Introduction](https://cliutils.gitlab.io/modern-cmake/chapters/intro/installing.html)
* [Homebrew CMake Formula Page](https://formulae.brew.sh/formula/cmake)
* Notes on Chocolatey + PATH issues when installing CMake (for Windows)

## 📝 Tips & Common Pitfalls

* **Always test `cmake --version` after install.** If it fails, you haven’t properly set up your PATH.
* **Use a separate `build/` directory.** Don’t generate build files into your source tree.
* **Be explicit about build types.** If ambiguous, you might accidentally build a debug binary when you wanted release.
* If any CMake or build error occurs, **copy and paste the full error message** into your question or email — vague reports (“it didn’t work”) are hard to debug.

Good luck. If your environment fails, please email me or bring your laptop in tutorials — I’ll help you debug rather than let you waste time.