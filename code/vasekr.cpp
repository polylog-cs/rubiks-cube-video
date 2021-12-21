/* Written by Filip Hlasek 2021 */

// asi to není bloom filter


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
void print_state(string& s) {
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
   "         ---------\n"
   , s[ 0], s[ 1], s[ 2], s[ 3], s[ 4], s[ 5], s[ 6], s[ 7], s[ 8], s[ 9]
   , s[10], s[11], s[12], s[13], s[14], s[15], s[16], s[17], s[18], s[19]
   , s[20], s[21], s[22], s[23], s[24], s[25], s[26], s[27], s[28], s[29]
   , s[30], s[31], s[32], s[33], s[34], s[35], s[36], s[37], s[38], s[39]
   , s[40], s[41], s[42], s[43], s[44], s[45], s[46], s[47]
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


// inline void apply_move(string& state, int face) { 
//     for (int p = 0; p < 5; ++p) {
//         auto tmp = state[MOVES[face][p][0]];
//         state[MOVES[face][p][0]] = state[MOVES[face][p][1]];
//         state[MOVES[face][p][1]] = state[MOVES[face][p][2]];
//         state[MOVES[face][p][2]] = state[MOVES[face][p][3]];
//         state[MOVES[face][p][3]] = tmp;
//     }
// }

inline void apply_move(string& state, int face) {
    for (int p = 0; p < 5; ++p) {
      for (int i = 3; i >= 1; i--) {
        std::swap(state[MOVES[face][p][i]], state[MOVES[face][p][i - 1]]);
      }
    }
}

inline pair<ull, ull> compress_state(string& state){
    ull fst = 0;
    ull snd = 0;
    for(int i = 0; i < 24; ++i){ // log_2(6^24) = 62.1
        fst += state[i] - 'F';
        fst *= 6;
    }
    for(int i = 0; i < 24; ++i){
        snd += state[24+i] - 'F';
        snd *= 6;
    }
    return {fst, snd};
}

// inline ull hsh_state(string& state){
//     pair<ull, ull> p = compress_state(state);
//     return p.first ^ p.second;
// }

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

  for(int i = 0; i < 18; ++i){
      for(int t = 0; t < moves[i][1]; ++t){
        apply_move(FELIKS, moves[i][0]);
      }
  }

  //print_state(FELIKS);
}



//#define BITSET_SIZE 17179869184LL
//#define BITSET_SIZE 34359738368LL
//#define BITSET_SIZE 1ULL << 30
const long long BITSET_SIZE = 1ULL << 3; //2;

long long explored = 0;
long long P = (1ULL << 63) - 25;

ofstream dump_states;
    

long long hash_state(string &state) {
  long long hash = 0;

  for (int i = 0; i < 48; ++i) {
    hash = hash * P + (state[i] - 'A');
  }

  // Since we always use odd P and there is an even number of odd elements
  // in the state vector, the resulting hash is always even. We can improve
  // the utility of the hashing function by dividing the hash by two.
  hash >>= 1;

  return hash & (BITSET_SIZE - 1);
}

struct pair_hash {
    size_t operator () (const pair<ull,ull> &p) const {
        return (p.first ^ p.second);  
    }
};

bitset<BITSET_SIZE> bloom_filter;
vector<pair<string, int> > candidates;
int cnt_candidates = 0;
int cnt = 0;

unordered_map<pair<ull, ull>, char, pair_hash> states6;
unordered_map<pair<ull, ull>, char, pair_hash> states7;

void explore_states(
    string& state,
    int depth,
    int max_depth,
    int last_face,
    
    bool first
) {

    ++cnt;

    if(depth == 6){ // some pruning at level 6
        pair<ull, ull> comp_state = compress_state(state);
        if(states6.count(comp_state) && states6[comp_state] <= depth){
            return; //we already visited this state
        }
        states6[comp_state] = depth;
    } 

    // if(depth == 7){ // some pruning at level 7
    //     pair<ull, ull> comp_state = compress_state(state);
    //     if(states7.count(comp_state) && states7[comp_state] <= depth){
    //         return; //we already visited this state
    //     }
    //     states7[comp_state] = depth;
    // } 

    // if(depth == max_depth){
    //     long long h = hash_state(state);

    //     if(first){
    //         bloom_filter.set(h); // put the state in the bloom filter
            
    //         //dump_states << state << " " << h << endl; // write the state into the full dump file
    //     }
    //     else{
    //         if(bloom_filter.test(h)){
    //             ++cnt_candidates;
    //         }
    //     }

    //     return;
    // }
    


    for (int face = 0; face < 6; ++face) {
        //dont move the same face twice, also, fix order of moving independent faces
        if (face == last_face || (face < last_face && (face + last_face == 5)) ) {
            continue;
        }
        for (int step = 0; step < 3; ++step) {
            apply_move(state, face);
            
            if(depth < max_depth){

                explore_states(
                    state,
                    depth + 1,
                    max_depth,
                    face,
                    first
                );
            }
            
        }
        apply_move(state, face); // turn the cube back to the original position
    }
}

int main(int argc, char* argv[]) {
    int max_depth; 
    sscanf(argv[1], "%d", &max_depth);
    //generate the cube of Feliks
    create_feliks_cube();
    //print_state(FELIKS);

//for(int l = 0; l <= 10; ++l)
{
    dump_states.open("dump_states2.txt");
    unordered_map<pair<ull, ull>, char, pair_hash> states;
    bloom_filter.reset();
    explore_states(
        SOLVED,
        0,
        max_depth,
        -1,
        true 
    );
    dump_states.close();
    cout << 6 << " " << states6.size() << endl;
    cout << 7 << " " << states7.size() << endl;
    //cout << "bloom filter utility: " << bloom_filter.count() << " / " << bloom_filter.size() << endl;
    //cout << cnt << endl;
    return 0;

    states.clear();
    explore_states(
        FELIKS,
        0,
        5,
        -1,
        false 
    );
    cout << "no candidates " << cnt_candidates << endl;

    remove("dump_states2.txt");
    cout << "no computations " << cnt << endl;

}
    
    

    return 0;
}
