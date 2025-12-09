#include "linear_probing.h"
#include <gtest/gtest.h>
#include <random>
#include <iostream>
#include <set>

TEST(LinearProbing, BasicInsertSearch) {
  LinearProbingHashTable ht(11);
  EXPECT_TRUE(ht.insert(10));
  EXPECT_TRUE(ht.insert(21));
  EXPECT_TRUE(ht.search(10));
  EXPECT_TRUE(ht.search(21));
  EXPECT_FALSE(ht.search(99));
}

TEST(LinearProbing, Remove) {
  LinearProbingHashTable ht(11);
  EXPECT_TRUE(ht.insert(10));
  EXPECT_TRUE(ht.search(10));
  EXPECT_TRUE(ht.remove(10));
  EXPECT_FALSE(ht.search(10));
  EXPECT_TRUE(ht.insert(10));
  EXPECT_TRUE(ht.search(10));
}

TEST(LinearProbing, CollisionHandling) {
  LinearProbingHashTable ht(5);
  EXPECT_TRUE(ht.insert(5));
  EXPECT_TRUE(ht.insert(10));
  EXPECT_TRUE(ht.insert(15));
  EXPECT_TRUE(ht.search(5));
  EXPECT_TRUE(ht.search(10));
  EXPECT_TRUE(ht.search(15));
}

TEST(LinearProbing, Rehash) {
  LinearProbingHashTable ht(5);
  for (int i = 0; i < 10; i++) {
    EXPECT_TRUE(ht.insert(i));
  }
  for (int i = 0; i < 10; i++) {
    EXPECT_TRUE(ht.search(i));
  }
}

TEST(LinearProbing, DuplicateInsert) {
  LinearProbingHashTable ht(11);
  EXPECT_TRUE(ht.insert(42));
  EXPECT_TRUE(ht.insert(42));
  EXPECT_TRUE(ht.search(42));
  EXPECT_TRUE(ht.remove(42));
  EXPECT_FALSE(ht.search(42));
}

TEST(LinearProbing, LargeScale) {
  LinearProbingHashTable ht(101);
  for (int i = 0; i < 5000; i++) {
    EXPECT_TRUE(ht.insert(i));
  }
  for (int i = 0; i < 5000; i++) {
    EXPECT_TRUE(ht.search(i));
  }
}

TEST(LinearProbing, BoundaryValuesTest) {
  LinearProbingHashTable ht(11);
  
  EXPECT_TRUE(ht.insert(0)) << "Failed to insert minimum value 0";
  EXPECT_TRUE(ht.search(0)) << "Failed to find minimum value 0";
  
  EXPECT_TRUE(ht.insert(1000000)) << "Failed to insert maximum value 1000000";
  EXPECT_TRUE(ht.search(1000000)) << "Failed to find maximum value 1000000";
  
  EXPECT_TRUE(ht.insert(999999)) << "Failed to insert near-maximum value 999999";
  EXPECT_TRUE(ht.search(999999)) << "Failed to find near-maximum value 999999";
  
  EXPECT_TRUE(ht.remove(0)) << "Failed to remove minimum value 0";
  EXPECT_FALSE(ht.search(0)) << "Minimum value 0 should not exist after removal";
  
  EXPECT_TRUE(ht.remove(1000000)) << "Failed to remove maximum value 1000000";
  EXPECT_FALSE(ht.search(1000000)) << "Maximum value 1000000 should not exist after removal";
  
  EXPECT_TRUE(ht.insert(0)) << "Failed to re-insert minimum value 0";
  EXPECT_TRUE(ht.search(0)) << "Failed to find re-inserted minimum value 0";
}


TEST(LinearProbing, RandomLargeDataTest) {
  LinearProbingHashTable ht(101);
  const int test_size = 10000;
  
  std::mt19937 gen(42);
  std::uniform_int_distribution<int> dis(0, 1000000);
  
  std::vector<int> test_data;
  test_data.reserve(test_size);
  std::set<int> used_values;
  
  for (int i = 0; i < test_size; i++) {
    int value;
    do {
      value = dis(gen);
    } while (used_values.find(value) != used_values.end());
    
    used_values.insert(value);
    test_data.push_back(value);
    bool success = ht.insert(value);
    if (!success) {
      std::cout << "Warning: Failed to insert value: " << value << std::endl;
    }
  }
  
  int found_count = 0;
  for (int value : test_data) {
    if (ht.search(value)) {
      found_count++;
    }
  }
  
  EXPECT_GE(found_count, test_size * 95 / 100)
    << "Only found " << found_count << " out of " << test_size << " inserted values";
  
  int successful_removals = 0;
  for (int i = 0; i < test_size / 2; i++) {
    int value = test_data[i];
    if (ht.remove(value)) {
      successful_removals++;
      EXPECT_FALSE(ht.search(value)) << "Removed value should not exist: " << value;
    }
  }
  
  EXPECT_GE(successful_removals, (test_size / 2) * 90 / 100)
    << "Only successfully removed " << successful_removals << " out of " << (test_size / 2) << " attempts";
  
  int remaining_found = 0;
  for (int i = test_size / 2; i < test_size; i++) {
    if (ht.search(test_data[i])) {
      remaining_found++;
    }
  }
  
  EXPECT_GE(remaining_found, (test_size / 2) * 90 / 100)
    << "Only found " << remaining_found << " out of " << (test_size / 2) << " remaining values";
}

TEST(LinearProbing, WorstCaseClusteringTest) {
  LinearProbingHashTable ht(23); // 浣跨敤璐ㄦ暟澶у皬
  const int cluster_size = 15;
  
  std::vector<int> cluster_keys;
  for (int i = 0; i < cluster_size; i++) {
    int key = i * 23;
    cluster_keys.push_back(key);
    EXPECT_TRUE(ht.insert(key)) << "Failed to insert clustering key: " << key;
  }
  
  for (int key : cluster_keys) {
    EXPECT_TRUE(ht.search(key)) << "Failed to find clustering key: " << key;
  }
  
  EXPECT_TRUE(ht.remove(cluster_keys[cluster_size / 2]))
    << "Failed to remove middle cluster key";
  
  for (int i = 0; i < cluster_size; i++) {
    if (i != cluster_size / 2) {
      EXPECT_TRUE(ht.search(cluster_keys[i]))
        << "Failed to find cluster key after removal: " << cluster_keys[i];
    }
  }
  
  int new_key = 100;
  EXPECT_TRUE(ht.insert(new_key)) << "Failed to insert new key into clustered table";
  EXPECT_TRUE(ht.search(new_key)) << "Failed to find newly inserted key: " << new_key;
}

TEST(LinearProbing, LoadFactorBoundaryTest) {
  LinearProbingHashTable ht(10);

  for (int i = 0; i < 6; i++) {
    EXPECT_TRUE(ht.insert(i)) << "Failed to insert element before rehash threshold: " << i;
  }
  
  EXPECT_TRUE(ht.insert(6)) << "Failed to insert element at boundary: " << 6;
  
  EXPECT_TRUE(ht.insert(7)) << "Failed to insert element triggering rehash: " << 7;
  
  for (int i = 0; i < 8; i++) {
    EXPECT_TRUE(ht.search(i)) << "Failed to find element after rehash: " << i;
  }
  
  LinearProbingHashTable ht2(7);
  
  for (int i = 0; i < 4; i++) {
    EXPECT_TRUE(ht2.insert(i)) << "Failed to insert before threshold: " << i;
  }
  
  EXPECT_TRUE(ht2.insert(4)) << "Failed to insert element crossing threshold: " << 4;
  
  for (int i = 0; i < 5; i++) {
    EXPECT_TRUE(ht2.search(i)) << "Failed to find element after rehash: " << i;
  }
}

TEST(LinearProbing, LazyDeletionStressTest) {
  LinearProbingHashTable ht(11);
  const int test_size = 100;
  
  std::vector<int> test_data;
  for (int i = 0; i < test_size; i++) {
    test_data.push_back(i * 1000 % 1000000);
    EXPECT_TRUE(ht.insert(test_data[i])) << "Failed to insert: " << test_data[i];
  }
  
  for (int i = 0; i < test_size / 2; i++) {
    EXPECT_TRUE(ht.remove(test_data[i])) << "Failed to remove: " << test_data[i];
    EXPECT_FALSE(ht.search(test_data[i])) << "Removed element should not exist: " << test_data[i];
  }
  
  for (int i = 0; i < test_size / 2; i++) {
    EXPECT_TRUE(ht.insert(test_data[i])) << "Failed to re-insert deleted element: " << test_data[i];
    EXPECT_TRUE(ht.search(test_data[i])) << "Failed to find re-inserted element: " << test_data[i];
  }
  
  for (int i = test_size; i < test_size + 50; i++) {
    int new_value = i * 1000 % 1000000;
    EXPECT_TRUE(ht.insert(new_value)) << "Failed to insert new value: " << new_value;
  }
  
  for (int i = 0; i < test_size / 2; i++) {
    EXPECT_TRUE(ht.search(test_data[i])) << "Should find re-inserted element: " << test_data[i];
  }
  
  for (int i = test_size / 2; i < test_size; i++) {
    EXPECT_TRUE(ht.search(test_data[i])) << "Should find original element: " << test_data[i];
  }
  
  for (int i = test_size; i < test_size + 50; i++) {
    int new_value = i * 1000 % 1000000;
    EXPECT_TRUE(ht.search(new_value)) << "Should find new element: " << new_value;
  }
}

TEST(LinearProbing, MixedOperationStressTest) {
  LinearProbingHashTable ht(23);
  const int operation_count = 1000;
  std::vector<int> active_keys;
  
  std::mt19937 gen(12345);
  std::uniform_int_distribution<int> value_dis(0, 1000000);
  std::uniform_int_distribution<int> op_dis(0, 2);
  
  for (int i = 0; i < operation_count; i++) {
    int operation = op_dis(gen);
    
    switch (operation) {
      case 0: { // Insert
        int value = value_dis(gen);
        bool success = ht.insert(value);
        if (success) {
          active_keys.push_back(value);
        }
        EXPECT_TRUE(ht.search(value)) << "Failed to find newly inserted value: " << value;
        break;
      }
      case 1: { // Search
        if (!active_keys.empty()) {
          int index = gen() % active_keys.size();
          int value = active_keys[index];
          EXPECT_TRUE(ht.search(value)) << "Failed to find active value: " << value;
        }
        break;
      }
      case 2: { // Remove
        if (!active_keys.empty()) {
          int index = gen() % active_keys.size();
          int value = active_keys[index];
          EXPECT_TRUE(ht.remove(value)) << "Failed to remove active value: " << value;
          EXPECT_FALSE(ht.search(value)) << "Removed value should not exist: " << value;
          active_keys.erase(active_keys.begin() + index);
        }
        break;
      }
    }
  }
  
  for (int value : active_keys) {
    EXPECT_TRUE(ht.search(value)) << "Final verification failed for value: " << value;
  }
  
  std::vector<int> final_test_values;
  for (int i = 0; i < 100; i++) {
    int value = (i * 12345) % 1000000;
    final_test_values.push_back(value);
    EXPECT_TRUE(ht.insert(value)) << "Final insert failed for: " << value;
  }
  
  for (int value : final_test_values) {
    EXPECT_TRUE(ht.search(value)) << "Final search failed for: " << value;
  }
}