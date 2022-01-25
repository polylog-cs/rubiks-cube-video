
/* Written by Filip Hlasek 2021 */

#include <cassert>
#include <cstdio>
#include <algorithm>
#include <bitset>

/**
 * The state of the Rubik's cube is represented as a string of 48 characters.
 * Since the entire cube is never rotated, we maintain the relative position
 * of the faces. Therefore, the middle cell of each face doesn't have to be
 * stored in the state and only 8 characters are necessary to describe the
 * state of one face.
 * The middle cell of the first face is colored 'A', the second face 'B', etc.
 * The faces are numbered as on a regular dice, but 0-indexed. The relative
 * position of the cube's faces is illustrated here:
 *
 *      2
 *    1 0 4 5
 *      3
 */

const char *SOLVED =
               "C""C""C"
               "C"   "C"
               "C""C""C"

   "B""B""B"   "A""A""A"   "E""E""E"   "F""F""F"
   "B"   "B"   "A"   "A"   "E"   "E"   "F"   "F"
   "B""B""B"   "A""A""A"   "E""E""E"   "F""F""F"

               "D""D""D"
               "D"   "D"
               "D""D""D";

// https://en.wikipedia.org/wiki/Superflip
// Each corner is correctly placed, but the colors at the edges are 'flipped'.
const char *SUPERFLIP =
               "C""F""C"
               "B"   "E"
               "C""A""C"

   "B""C""B"   "A""C""A"   "E""C""E"   "F""C""F"
   "F"   "A"   "B"   "E"   "A"   "F"   "E"   "B"
   "B""D""B"   "A""D""A"   "E""D""E"   "F""D""F"

               "D""A""D"
               "B"   "E"
               "D""F""D";

/** A simple function to print a formatted the state of a cube. */
void print_state(const char *s) {
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

/*
 * The array below describes all valid moves with the 3x3 Rubik's cube.
 * The moves are groupped by the face which they are rotating.
 * For each face, the possible rotations are described by a set of 5
 * lists of 4 cells. Each of these lists represent a permutation of cells
 * which is applied to the colors when the particular face is turned 90
 * degrees clockwise. The first 2 of the 5 lists rotate the 8 cells on the face
 * while the next 3 lists rotate the 12 surrounding cells neighboring the face.
 * If all the 5 permutations are applied to the colored state once, that
 * performs a quarter turn clockwise move, if applied twice, that is a half
 * turn of that face, three times is a counter-clockwise quarter turn and
 * four applications turn the face around to the same position.
 *
 * For convenience we include a schema of all the cell numbers:
 *
 *            ------------
 *            |  0  1  2 |
 *            |  3  C  4 |
 *            |  5  6  7 |
 * ---------------------------------------------
 * |  8  9 10 | 11 12 13 | 14 15 16 | 17 18 19 |
 * | 20  B 21 | 22  A 23 | 24  E 25 | 26  F 27 |
 * | 28 29 30 | 31 32 33 | 34 35 36 | 37 38 39 |
 * ---------------------------------------------
 *            | 40 41 42 |
 *            | 43  D 44 |
 *            | 45 46 47 |
 *            ------------
 */

const int MOVES[6][5][4] = {
  {{11, 13, 33, 31}, {12, 23, 32, 22}, { 5, 14, 42, 30}, { 6, 24, 41, 21}, { 7, 34, 40, 10}}, // face A
  {{ 8, 10, 30, 28}, { 9, 21, 29, 20}, { 0, 11, 40, 39}, { 3, 22, 43, 27}, { 5, 31, 45, 19}}, // face B
  {{ 0,  2,  7,  5}, { 1,  4,  6,  3}, {19, 16, 13, 10}, {18, 15, 12,  9}, {17, 14, 11,  8}}, // face C
  {{40, 42, 47, 45}, {41, 44, 46, 43}, {31, 34, 37, 28}, {32, 35, 38, 29}, {33, 36, 39, 30}}, // face D
  {{14, 16, 36, 34}, {15, 25, 35, 24}, { 7, 17, 47, 33}, { 4, 26, 44, 23}, { 2, 37, 42, 13}}, // face E
  {{17, 19, 39, 37}, {18, 27, 38, 26}, { 2,  8, 45, 36}, { 1, 20, 46, 25}, { 0, 28, 47, 16}}  // face F
};

/**
 * This function modifies the given state of the Rubik's cube by applying
 * the move corresponding to the provided face.
 * Optionally, it performs the operation 'count' times.
 */
void apply_move(char *state, int face, int count = 1) {
  while (count--) {
    for (int p = 0; p < 5; ++p) {
      for (int i = 3; i >= 1; i--) {
        std::swap(state[MOVES[face][p][i]], state[MOVES[face][p][i - 1]]);
      }
    }
  }
}

/**
 * A simple unit test checking the correct oprtation of moves.
 * According to the Wikipedia page https://en.wikipedia.org/wiki/Superflip
 * the following sequence of 20 moves should generate the Superflip position
 * from the solved cube:
 *
 * U R2 F B R B2 R U2 L B2 R U' D' R2 F R' L B2 U2 F2
 *
 * A = F(ront), B = L(eft), C = U(p), D = D(own), E = R(ight), F = B(ack)
 */
void test_superflip_generation() {
  // The first number represent the face, the second number how many
  // quarter turns of that face need to be applied clockwise.
  int moves[20][2] = {
    // U      R2      F       B       R       B2      R       U2      L       B2
    {2, 1}, {4, 2}, {0, 1}, {5, 1}, {4, 1}, {5, 2}, {4, 1}, {2, 2}, {1, 1}, {5, 2},

    // R      U'      D'      R2      F       R'      L       B2      U2      F2
    {4, 1}, {2, 3}, {3, 3}, {4, 2}, {0, 1}, {4, 3}, {1, 1}, {5, 2}, {2, 2}, {0, 2}
  };

  char state[48];
  for (int i = 0; i < 48; ++i) {
    state[i] = SOLVED[i];
  }

  for (int i = 0; i < 20; ++i) {
    print_state(state);
    printf(
        "\nTurning face %d(%c) clockwise by %d quarter turns.\n",
        moves[i][0], moves[i][0] + 'A', moves[i][1]);
    apply_move(state, moves[i][0], moves[i][1]);
  }

  print_state(state);
  for (int i = 0; i < 48; ++i) {
    assert(state[i] == SUPERFLIP[i]);
  }

}

/**
 * A function which calculates a simple polynomial rolling hash function
 * for the given state. More specifically, it returns:
 *
 * (state[0] * P**47 + ... + state[47] * P**0) & mod_mask
 */
long long hash_state(char *state, long long P, long long mod_mask) {
  long long hash = 0;

  for (int i = 0; i < 48; ++i) {
    hash = hash * P + (state[i] - 'A');
  }

  // Since we always use odd P and there is an even number of odd elements
  // in the state vector, the resulting hash is always even. We can improve
  // the utility of the hashing function by dividing the hash by two.
  hash >>= 1;

  return hash & mod_mask;
}

// #define BITSET_SIZE 17179869184LL
#define BITSET_SIZE 34359738368LL

long long explored = 0;

void explore_states(
    char *state,
    int depth,
    int max_depth,
    long long P,
    long long mod_mask,
    std::bitset<BITSET_SIZE>* states,
    long long crosscheck_P,
    long long crosscheck_mod_mask,
    const std::bitset<BITSET_SIZE>* crosscheck_states,
    int last_face = -1,
    bool symmetrical = false
) {

  if (depth == max_depth) {
    if (crosscheck_P == -1) {
      states->set(hash_state(state, P, mod_mask));
    } else {
      long long crosscheck_hash = hash_state(state, crosscheck_P, crosscheck_mod_mask);
      if (crosscheck_states->test(crosscheck_hash)) {
        states->set(hash_state(state, P, mod_mask));
        // fprintf(stderr, "Present %lld\n", crosscheck_hash);
      } else {
        // fprintf(stderr, "Not Present %lld\n", crosscheck_hash);
      }
    }

    explored++;
    const int X = 1000000000;
    if (explored % X == 0) {
      long long maximum = 18;
      for (int i = 0; i + 1 < max_depth; ++i) {
        maximum *= 15;
      }

      fprintf(stderr, "%lld / %lld, ", explored / X, maximum / X);
      fprintf(stderr, "Bitset utility: %zu / %zu\n", states->count(), states->size());
    }
    return;
  }

  for (int face = 0; face < 6; ++face) {
     if (face == last_face || (face < last_face && (face + last_face == 5)) ) {
      continue;
    }
    for (int step = 0; step < 3; ++step) {
      apply_move(state, face);
      explore_states(
          state,
          depth + 1,
          max_depth,
          P,
          mod_mask,
          states,
          crosscheck_P,
          crosscheck_mod_mask,
          crosscheck_states,
          face
      );
    }
    apply_move(state, face); // turn the cube back to the original position

    if (symmetrical) {
      break;
    }
  }
}

void save_bitset(FILE *f, std::bitset<BITSET_SIZE>* bitset) {
  for (long long i = 0; i < BITSET_SIZE; i += 8) {
    char c = 0;
    for (int j = 0; j < 8; ++j) if (bitset->test(i + j)) {
      c |= 1 << j;
    }
    fprintf(f, "%c", c);
  }
}

std::bitset<BITSET_SIZE>* parse_bitset(FILE *f) {
  std::bitset<BITSET_SIZE>* bitset = new std::bitset<BITSET_SIZE>();
  for (long long i = 0; i < BITSET_SIZE; i += 8) {
    char c;
    fscanf(f, "%c", &c);;
    for (int j = 0; j < 8; ++j) if (c & (1 << j)) {
      bitset->set(i + j);
    }
  }
  return bitset;
}

std::bitset<BITSET_SIZE>* explore_states(
    int max_depth,
    const char *start_state,
    long long P,
    long long mod_mask,
    long long crosscheck_P,
    long long crosscheck_mod_mask,
    const std::bitset<BITSET_SIZE>* crosscheck_states,
    bool symmetrical
) {

  std::bitset<BITSET_SIZE>* ans = new std::bitset<BITSET_SIZE>();
  char state[49];
  for (int i = 0; i < 48; ++i) {
    state[i] = start_state[i];
  }
  state[48] = '\0'; // for printing

  explore_states(
      state,
      0,
      max_depth,
      P,
      mod_mask,
      ans,
      crosscheck_P,
      crosscheck_mod_mask,
      crosscheck_states,
      -1,
      symmetrical
  );

  return ans;
}

/**
 * ./rubik.cpp max_depth P output_filename [from_solved crosscheck_P crosscheck_filename]
 */
int main(int argc, char* argv[]) {
  // test_superflip_generation();

  int max_depth;
  sscanf(argv[1], "%d", &max_depth);
  long long P;
  sscanf(argv[2], "%lld", &P);

  int from_solved = true;
  long long crosscheck_P = -1;
  std::bitset<BITSET_SIZE>* crosscheck_states = NULL;
  if (argc > 4) {
    sscanf(argv[4], "%d", &from_solved);
    sscanf(argv[5], "%lld", &crosscheck_P);
    FILE *f = fopen(argv[6], "r");
    crosscheck_states = parse_bitset(f);
    fclose(f);
    fprintf(stderr, "Crosscheck utility: %zu / %zu\n", crosscheck_states->count(), crosscheck_states->size());
  }

  auto states = explore_states(
      max_depth,
      from_solved ? SOLVED : SUPERFLIP,
      P,
      BITSET_SIZE - 1,
      crosscheck_P,
      BITSET_SIZE - 1,
      crosscheck_states,
      from_solved ? false : true
  );
  fprintf(stderr, "Bitset utility: %zu / %zu\n", states->count(), states->size());
  return 0;
  FILE *f = fopen(argv[3], "w");
  save_bitset(f, states);
  fclose(f);

  delete states;
  if (crosscheck_states != NULL) {
    delete crosscheck_states;
  }

  return 0;
}