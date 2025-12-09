#include "cuckoo_hash.h"
#include <gtest/gtest.h>
#include <random>

TEST(CuckooHash, BasicInsertSearch) {
  CuckooHashTable ht(11);
  EXPECT_TRUE(ht.insert(10));
  EXPECT_TRUE(ht.insert(21));
  EXPECT_TRUE(ht.search(10));
  EXPECT_TRUE(ht.search(21));
  EXPECT_FALSE(ht.search(99));
}

TEST(CuckooHash, Remove) {
  CuckooHashTable ht(11);
  EXPECT_TRUE(ht.insert(10));
  EXPECT_TRUE(ht.search(10));
  EXPECT_TRUE(ht.remove(10));
  EXPECT_FALSE(ht.search(10));
}

TEST(CuckooHash, Displacement) {
  CuckooHashTable ht(3);
  EXPECT_TRUE(ht.insert(1));
  EXPECT_TRUE(ht.insert(4));
  EXPECT_TRUE(ht.search(1));
  EXPECT_TRUE(ht.search(4));
}

TEST(CuckooHash, Rehash) {
  CuckooHashTable ht(2);
  for (int i = 0; i < 20; i++) {
    EXPECT_TRUE(ht.insert(i));
  }
  for (int i = 0; i < 20; i++) {
    EXPECT_TRUE(ht.search(i));
  }
}

TEST(CuckooHash, DuplicateInsert) {
  CuckooHashTable ht(11);
  EXPECT_TRUE(ht.insert(42));
  EXPECT_TRUE(ht.insert(42));
  EXPECT_TRUE(ht.search(42));
  EXPECT_TRUE(ht.remove(42));
  EXPECT_FALSE(ht.search(42));
}

TEST(CuckooHash, LargeScale) {
  CuckooHashTable ht(101);
  for (int i = 0; i < 5000; i++) {
    EXPECT_TRUE(ht.insert(i));
  }
  for (int i = 0; i < 5000; i++) {
    EXPECT_TRUE(ht.search(i));
  }
}

TEST(CuckooHash, BoundaryValuesTest) {
  CuckooHashTable ht(11);
  
  EXPECT_TRUE(ht.insert(0)) << "Failed to insert minimum boundary value 0";
  EXPECT_TRUE(ht.search(0)) << "Failed to find minimum boundary value 0";
  
  EXPECT_TRUE(ht.insert(1000000)) << "Failed to insert maximum boundary value 10^6";
  EXPECT_TRUE(ht.search(1000000)) << "Failed to find maximum boundary value 10^6";
  
  EXPECT_TRUE(ht.insert(1)) << "Failed to insert value 1";
  EXPECT_TRUE(ht.insert(999999)) << "Failed to insert value 999999";
  EXPECT_TRUE(ht.search(1)) << "Failed to find value 1";
  EXPECT_TRUE(ht.search(999999)) << "Failed to find value 999999";
  
  EXPECT_TRUE(ht.remove(0)) << "Failed to remove minimum boundary value 0";
  EXPECT_FALSE(ht.search(0)) << "Found minimum boundary value 0 after removal";
  EXPECT_TRUE(ht.remove(1000000)) << "Failed to remove maximum boundary value 10^6";
  EXPECT_FALSE(ht.search(1000000)) << "Found maximum boundary value 10^6 after removal";
}

TEST(CuckooHash, RandomLargeDataTest) {
  const int num_elements = 10000;
  const int seed = 42;
  
  std::mt19937 gen(seed);
  std::uniform_int_distribution<int> dis(0, 1000000);
  
  std::vector<int> test_data;
  test_data.reserve(num_elements);
  
  for (int i = 0; i < num_elements; i++) {
    test_data.push_back(dis(gen));
  }
  
  CuckooHashTable ht(101);
 
  for (int i = 0; i < num_elements; i++) {
    EXPECT_TRUE(ht.insert(test_data[i]))
        << "Failed to insert random element at index " << i << " with value " << test_data[i];
  }
  
  for (int i = 0; i < num_elements; i++) {
    EXPECT_TRUE(ht.search(test_data[i]))
        << "Failed to find random element at index " << i << " with value " << test_data[i];
  }
  
  for (int i = 0; i < 100; i++) {
    int idx = dis(gen) % num_elements;
    EXPECT_TRUE(ht.remove(test_data[idx]))
        << "Failed to remove random element at index " << idx;
    EXPECT_FALSE(ht.search(test_data[idx]))
        << "Found removed element at index " << idx;
    EXPECT_TRUE(ht.insert(test_data[idx]))
        << "Failed to re-insert random element at index " << idx;
    EXPECT_TRUE(ht.search(test_data[idx]))
        << "Failed to find re-inserted element at index " << idx;
  }
}

TEST(CuckooHash, WorstCaseConflictTest) {
  CuckooHashTable ht(7);
  
  std::vector<int> conflict_keys = {7, 14, 21, 28, 35, 42, 49, 56, 63, 70};
  
  for (int key : conflict_keys) {
    EXPECT_TRUE(ht.insert(key)) << "Failed to insert key with high conflict potential: " << key;
  }
  
  for (int key : conflict_keys) {
    EXPECT_TRUE(ht.search(key)) << "Failed to find key with high conflict potential: " << key;
  }
  
  for (int i = 1; i <= 50; i++) {
    int key = i * 7;
    EXPECT_TRUE(ht.insert(key)) << "Failed to insert key " << key << " during stress test";
    EXPECT_TRUE(ht.search(key)) << "Failed to find key " << key << " during stress test";
  }
}

TEST(CuckooHash, MaxDisplacementLimitTest) {
  const int table_size = 5;
  CuckooHashTable ht(table_size);
  
  std::vector<int> keys;
  for (int i = 0; i < table_size * 2; i++) {
    keys.push_back(i * table_size + 1);
  }
  
  for (size_t i = 0; i < keys.size(); i++) {
    EXPECT_TRUE(ht.insert(keys[i]))
        << "Failed to insert key " << keys[i] << " at position " << i
        << " (may exceed 2*m displacement limit)";
  }
  
  for (int key : keys) {
    EXPECT_TRUE(ht.search(key)) << "Failed to find key " << key << " after max displacement test";
  }
  
  for (int i = 0; i < 10; i++) {
    int key = keys.size() + i * 1000;
    EXPECT_TRUE(ht.insert(key)) << "Failed to insert additional key " << key << " triggering rehash";
    EXPECT_TRUE(ht.search(key)) << "Failed to find additional key " << key << " after rehash";
  }
}

TEST(CuckooHash, DeleteInsertCycleTest) {
  const int num_cycles = 100;
  const int num_keys = 20;
  
  CuckooHashTable ht(13);
  std::vector<int> test_keys;
  
  for (int i = 0; i < num_keys; i++) {
    test_keys.push_back(i * 1000 + 123);
  }
  
  for (int key : test_keys) {
    EXPECT_TRUE(ht.insert(key)) << "Failed initial insert of key " << key;
  }
  
  for (int cycle = 0; cycle < num_cycles; cycle++) {
    for (int key : test_keys) {
      EXPECT_TRUE(ht.remove(key)) << "Failed to remove key " << key << " in cycle " << cycle;
      EXPECT_FALSE(ht.search(key)) << "Found removed key " << key << " in cycle " << cycle;
    }
    
    for (int key : test_keys) {
      EXPECT_TRUE(ht.insert(key)) << "Failed to re-insert key " << key << " in cycle " << cycle;
      EXPECT_TRUE(ht.search(key)) << "Failed to find re-inserted key " << key << " in cycle " << cycle;
    }
  }
  
  for (int key : test_keys) {
    EXPECT_TRUE(ht.search(key)) << "Failed to find key " << key << " after all cycles";
  }
}

TEST(CuckooHash, MixedOperationStressTest) {
  const int num_operations = 5000;
  const int initial_size = 101;
  const int seed = 12345;
  
  std::mt19937 gen(seed);
  std::uniform_int_distribution<int> op_dis(0, 2);
  std::uniform_int_distribution<int> key_dis(0, 1000000);
  
  CuckooHashTable ht(initial_size);
  std::vector<int> inserted_keys;
  
  for (int op = 0; op < num_operations; op++) {
    int operation = op_dis(gen);
    int key = key_dis(gen);
    
    switch (operation) {
      case 0:
        EXPECT_TRUE(ht.insert(key)) << "Failed to insert key " << key << " at operation " << op;
        inserted_keys.push_back(key);
        break;
        
      case 1:
        if (inserted_keys.empty()) {
          EXPECT_FALSE(ht.search(key)) << "Found unexpected key " << key << " in empty table";
        } else {
          int search_key = inserted_keys[op % inserted_keys.size()];
          EXPECT_TRUE(ht.search(search_key))
              << "Failed to find existing key " << search_key << " at operation " << op;
        }
        break;
        
      case 2:
        if (!inserted_keys.empty()) {
          int remove_key = inserted_keys.back();
          EXPECT_TRUE(ht.remove(remove_key))
              << "Failed to remove key " << remove_key << " at operation " << op;
          inserted_keys.pop_back();
          EXPECT_FALSE(ht.search(remove_key))
              << "Found removed key " << remove_key << " after removal at operation " << op;
        }
        break;
    }
  }
  
  for (int key : inserted_keys) {
    EXPECT_TRUE(ht.search(key)) << "Failed to find remaining key " << key << " in final verification";
  }
}