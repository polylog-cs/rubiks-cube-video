/* 
Written by Filip Hlasek 2021 
some changes by Vaclav Rozhon and Vaclav Volhejn

This is a demonstration of the meet in the middle technique
used to find a fastest solution of a particular Rubik's cube. 

We ran it on a cluster as follows: ./rubik_mitm_solution 8 10
The program ran for ~4 hours and needed ~90GB of memory. 

There are much more efficient algorithms for this task! 
For example, look here: http://kociemba.org/cube.htm
*/

#include <cassert>
#include <cstdio>
#include <algorithm>
#include <bitset>
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <fstream>

typedef unsigned long long ull;
using namespace std;

string SOLVED =
               "C""C""C"
               "C"   "C"
               "C""C""C"

   "B""B""B"   "A""A""A"   "E""E""E"   "F""F""F"
   "B"   "B"   "A"   "A"   "E"   "E"   "F"   "F"
   "B""B""B"   "A""A""A"   "E""E""E"   "F""F""F"

               "D""D""D"
               "D"   "D"
               "D""D""D";


/** A simple function to print a formatted the state of a cube. */
void print_state(string & s) {
  printf(
    "         ---------\n"
    "         | %c %c %c |\n"
    "         | %c C %c |\n"
    "         | %c %c %c |\n"
    " ---------------------------------\n"
    " | %c %c %c | %c %c %c | %c %c %c | %c %c %c |\n"
    " | %c B %c | %c A %c | %c E %c | %c F %c |\n"
    " | %c %c %c | %c %c %c | %c %c %c | %c %c %c |\n"
    " ---------------------------------\n"
    "         | %c %c %c |\n"
    "         | %c D %c |\n"
    "         | %c %c %c |\n"
    "         ---------\n", 
    s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8], s[9], s[10], s[11], s[12], s[13], s[14], s[15], s[16], s[17], s[18], s[19], s[20], s[21], s[22], s[23], s[24], s[25], s[26], s[27], s[28], s[29], s[30], s[31], s[32], s[33], s[34], s[35], s[36], s[37], s[38], s[39], s[40], s[41], s[42], s[43], s[44], s[45], s[46], s[47]
  );
}

const int MOVES[6][5][4] = {
  {{11, 13, 33, 31}, {12, 23, 32, 22}, { 5, 14, 42, 30}, { 6, 24, 41, 21}, { 7, 34, 40, 10}}, // face A
  {{ 8, 10, 30, 28}, { 9, 21, 29, 20}, { 0, 11, 40, 39}, { 3, 22, 43, 27}, { 5, 31, 45, 19}}, // face B
  {{ 0,  2,  7,  5}, { 1,  4,  6,  3}, {19, 16, 13, 10}, {18, 15, 12,  9}, {17, 14, 11,  8}}, // face C
  {{40, 42, 47, 45}, {41, 44, 46, 43}, {31, 34, 37, 28}, {32, 35, 38, 29}, {33, 36, 39, 30}}, // face D
  {{14, 16, 36, 34}, {15, 25, 35, 24}, { 7, 17, 47, 33}, { 4, 26, 44, 23}, { 2, 37, 42, 13}}, // face E
  {{17, 19, 39, 37}, {18, 27, 38, 26}, { 2,  8, 45, 36}, { 1, 20, 46, 25}, { 0, 28, 47, 16}}  // face F
};


inline void apply_move(string & state,
  const int face) {
  for (int p = 0; p < 5; ++p) {
    for (int i = 3; i >= 1; i--) {
      std::swap(state[MOVES[face][p][i]], state[MOVES[face][p][i - 1]]);
    }
  }
}

inline pair < ull, ull > compress_state(const string & state) {
  ull fst = 0;
  ull snd = 0;
  for (int i = 0; i < 24; ++i) { // log_2(6^24) = 62.1
    fst *= 6;
    fst += state[i] - 'A';
  }
  for (int i = 0; i < 24; ++i) {
    snd *= 6;
    snd += state[24 + i] - 'A';
  }
  return {
    fst,
    snd
  };
}


// Create the starting configuration of Feliks
string FELIKS;
void create_feliks_cube(){
  int moves[18][2] = {
    //U2     F       L2      U2     R2      F       L2       F2       L' 
    {2, 2}, {0, 1}, {1, 2}, {2, 2}, {4, 2}, {0, 1}, {1, 2}, {0, 2}, {1, 3},
    //D'     B2      R       D2      R'      B'      U'      L'      B'
    {3, 3}, {5, 2}, {4, 1}, {3, 2}, {4, 3}, {5, 3}, {2, 3}, {1, 3}, {5, 3}
  };

  FELIKS = SOLVED;

  for (int i = 0; i < 18; ++i) {
    for (int t = 0; t < moves[i][1]; ++t) {
      apply_move(FELIKS, moves[i][0]);
    }
  }
}

long long explored = 0;

struct pair_hash {
  size_t operator()(const pair < ull, ull > & p) const {
    return (p.first ^ p.second);
  }
};

ull cnt = 0;
bool explore_states(
  string & state,
  char depth,
  const char max_depth,
  int last_face,
  const char max_memo_depth, // max depth to which we memoize
  unordered_map < pair < ull, ull > , char, pair_hash > & explored_states, // memoization
  const bool first, //first or second run
  unordered_map < pair < ull, ull > , char, pair_hash > & crosscheck_states // for second run
) {

  ++cnt;

  pair < ull, ull > comp_state = compress_state(state);

  //memoization of states until max_memo_depth 
  if (depth <= max_memo_depth) {
    if (explored_states.count(comp_state) && explored_states[comp_state] <= depth) {
      return false; //we already visited this state
    }
    explored_states[comp_state] = depth;
  }

  // crosschecking found states with the already computed ones 
  if (!first) {
    if (crosscheck_states.count(comp_state)) {
      cout << "We found a cube in the middle! " << endl;
      print_state(state);
      return true;
    }
  }

  //continue exploration    
  if (depth != max_depth) {
    for (int face = 0; face < 6; ++face) {
      //dont move the same face twice, also, fix the order of moving independent faces
      if (face == last_face || (face < last_face && (face + last_face == 5))) {
        continue;
      }
      for (int step = 0; step < 3; ++step) {
        apply_move(state, face);

        bool ret = explore_states(
          state,
          depth + 1,
          max_depth,
          face,
          max_memo_depth,
          explored_states,
          first,
          crosscheck_states
        );
        if ((!first) && ret) {
          return true;
        }
      }
      apply_move(state, face); // turn the cube back to the original position
    }
  }
  return false;
}

int main(int argc, char * argv[]) {
  int max_depth1, max_depth2;
  sscanf(argv[1], "%d", & max_depth1);
  sscanf(argv[2], "%d", & max_depth2);

  //generate the cube of Feliks
  create_feliks_cube();

  // first run of the search
  string starting_state = SOLVED;
  unordered_map < pair < ull, ull > , char, pair_hash > found_states_first;
  unordered_map < pair < ull, ull > , char, pair_hash > dummy;

  explore_states(
    starting_state,
    0,
    max_depth1,
    -1,
    max_depth1,
    found_states_first,
    true,
    dummy // there are no crosscheck states 
  );

  cout << "first search finished" << endl;

  starting_state = FELIKS;
  unordered_map < pair < ull, ull > , char, pair_hash > found_states_second; // memoization to speed up second search

  bool ret = explore_states(
    starting_state,
    0,
    max_depth2,
    -1,
    7, // we memoize until this depth
    found_states_second,
    false,
    found_states_first
  );

  if (!ret) {
    cout << "we did not find a hit" << endl;
  }

  cout << "number of explored configurations: " << cnt << endl;

  return 0;
}