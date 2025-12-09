# Hash Table

## Overview
In this assignment, you will implement **two different hash table data structures**:

1. **Cuckoo Hashing** (30 points)
2. **Linear Probing Hashing** (30 points)

Your code must pass the provided **GoogleTest unit tests**.  
The total score of this coding part is **60 points**.

## Repository Structure
```
hash_assignment/
├── CMakeLists.txt
├── include/
│   ├── ihash_table.h            # Abstract interface
│   ├── cuckoo_hash.h            # Cuckoo Hashing header (skeleton)
│   └── linear_probing.h         # Linear Probing header (skeleton)
├── src/
│   ├── cuckoo_hash.cc           # Student implementation
│   └── linear_probing.cc        # Student implementation
├── tests/
│   ├── cuckoo_hash_test.cc      # 6 unit tests for Cuckoo Hashing
│   └── linear_probing_test.cc   # 6 unit tests for Linear Probing
└── README.md
```

## Tasks
- Complete the missing methods in:
  - `src/cuckoo_hash.cc`
  - `src/linear_probing.cc`

- Functions to implement:
  - `insert(int key)`
  - `search(int key) const`
  - `remove(int key)`
  - `rehash()` (when necessary)

- **Cuckoo Hashing** must:
  - Use two hash tables and two hash functions.
  - Support displacement with a maximum of `2*m` attempts.
  - Trigger rehash if insertion fails.

- **Linear Probing Hashing** must:
  - Use a single table with linear probing for collisions.
  - Use lazy deletion for `remove`.
  - Trigger rehash when load factor > 0.7.

## Build Instructions
This project uses **CMake** and **GoogleTest**.

```bash
# Build
cmake -S . -B build -DCMAKE_EXPOR_COMPILE_COMMANDS=ON
cmake --build build

# Switch to the build directory
cd ./build/

# Run all tests (macOS or Linux)
ctest --output-on-failure

# Run all tests (Windows)
ctest -C Debug --output-on-failure

# Or run specific test executables (macOS or Linux)
./bin/cuckoo_hash_test
./bin/linear_probing_test

# Or run specific test executables (Windows)
./bin/Debug/cuckoo_hash_test.exe
./bin/Debug/linear_probing_test.exe
```

## Grading

- **Cuckoo Hashing:** 6 tests, 5 points each (30 points).
- **Linear Probing:** 6 tests, 5 points each (30 points).

Passing all tests earns full credit. Partial credit will be given if only basic functionality is correct.

## Notes

* Keys are integers in the range `[0, 10^6]`.
* No need to implement resizing beyond rehash logic already specified.
* Do not change the public interface of the provided classes.
