#!/usr/bin/env python3

import sys

alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

class Board(object):
    def __init__(self, board=None, good_letters=None, bad_guesses=None):
        if not board:
            board = '.....'
        if not good_letters:
            good_letters = ''
        if not bad_guesses:
            bad_guesses = []
        self.board = board.upper()
        self.good_letters = set([x.upper() for x in good_letters])
        self.bad_guesses = [x.upper() for x in bad_guesses]
        self.bad_letters = set()
        for guess in bad_guesses:
            for i,ch in enumerate(guess.upper()):
                if board[i] != ch and not ch in self.good_letters:
                    self.bad_letters.add(ch)

        self.valid_global = [x for x in alpha if x not in self.bad_letters]
        self.valid = []

        for i in range(5):
            if self.board[i] != '.':
                self.valid.append([self.board[i]])
            else:
                vl = self.valid_global.copy()
                for guess in self.bad_guesses:
                    if guess[i] in self.good_letters:
                        if guess[i] in vl:
                            vl.remove(guess[i])
                self.valid.append(vl)


    def __repr__(self):
        ret = "%s\nGood letters: %s\nBad letters : %s\n" % (','.join(self.bad_guesses), self.good_letters, self.bad_letters)
        ret = '%s\n' % self.board
        # i=0
        # good = True
        # while good:
        #     good = False
        #     for j in range(5):
        #         if len(self.valid[j]) > i:
        #             ret += self.valid[j][i]
        #             good = True
        #         else:
        #             ret += ' '
        #     ret += '\n'
        #     i += 1
        
        return ret


    def size(self):
        return 5

    def get_valid_letters(self):
        return self.valid_global

    def get_pos_valid(self, pos):
        return self.valid[pos]


class WordList(object):
    def __init__(self, fname):
        self._global_freq = None
        self._pos_freq = None

        self.words = set()
        self.board = '.....'
        with open(fname, 'rt') as f:
            for line in f:
                bad=False
                if len(line.strip()) == 5:
                    for ch in line.strip().upper():
                        if ch not in alpha:
                            bad=True
                            break

                    if not bad:
                        self.words.add(line.strip().upper())
    
    def size(self):
        return len(self.words)


    def prune(self, board):
        self.board = board
        newwords = set()
        for word in self.words:
            good = True
            
            for ch in board.good_letters:
                if not ch in word:
                    good = False
                    break

            if good:
                for i,ch in enumerate(word):
                    if ch not in board.get_pos_valid(i):
                        good = False
                        break

                if good:
                    newwords.add(word)

        self.words = newwords



    def global_freq(self, ch):
        if not self._global_freq:
            freq = {}

            for ch in alpha:
                acc = 0
                for word in self.words:
                    if ch in word:
                        acc += 1
                freq[ch] = acc / self.size()
            
            self._global_freq = freq

        return self._global_freq[ch]

    def pos_freq(self, i, ch):
        if not self._pos_freq:
            ret = []
            for j in range(5):
                freq = {}
                for ch1 in alpha:
                    acc = 0
                    for word in self.words:
                        if ch1 == word[j]:
                            acc += 1
                    freq[ch1] = acc / self.size()
                ret.append(freq)
            self._pos_freq = ret

        return self._pos_freq[i][ch]


    def find_best(self, words, scores=1, verbose=False):

        best_scores = []
        best_words = []

        for word in sorted(words):
            score = self._pos_score(word)
            best_scores.append((-score, word))

            best_scores = sorted(best_scores)
            best_scores = best_scores[:scores]
        
        return [(-x, y) for x,y in best_scores]


    def _pos_score(self, word):
        letter_scores = {}

        for i, ch in enumerate(word):
            if not ch in letter_scores:
                letter_scores[ch] = 0

            # If we don't know this letter, try to figure it out
            if self.board.board[i] == '.':
                letter_scores[ch] = max(letter_scores[ch], self.pos_freq(i,ch))
            else:
                # if we do know this letter, then use the global frequency -- this position
                # isn't informative... if we already know the letter's position, it isn't informative at all

                if ch not in self.board.board:
                    letter_scores[ch] = max(letter_scores[ch], self.global_freq(ch))
                    
        
        acc = 0
        for i in letter_scores:
            if letter_scores[i] < 0.5:
                acc += letter_scores[i]/(1-letter_scores[i])
            else:
                acc += (1-letter_scores[i])/letter_scores[i]
        
        return acc


class TestWord(object):
    def __init__(self, word):
        self.word = word.upper()
    
    def play_word(self, word):
        # return a new board and valid letters

        valid = set()
        board = ''

        for i, ch in enumerate(word):
            if ch == self.word[i]:
                board+=ch
            else:
                board+='.'
            
            if ch in self.word:
                valid.add(ch)

        return board, ''.join(valid)


    def solve(self, good_fname='data/good.txt', valid_fname='data/valid.txt', hard_mode=False):
        all_board = '.....'
        all_good_letters = set()
        all_guesses = []

        guess = ''
        while guess != self.word:
    #        print("=====")
    #        print("Guess #%s" % (len(all_guesses)+1))
            b = Board(all_board, all_good_letters, all_guesses)
    #        print(b)
            good_words = WordList(good_fname)
            valid_words = WordList(valid_fname)

            good_words.prune(b)
    #        print("%s [%s]" % (good_words.size(), ','.join(good_words.words) if good_words.size() < 11 else '...'))
            if hard_mode:
                valid_words.prune(b)

            if good_words.size()== 0:
                print("No valid guesses!")
                sys.exit(1)
            elif (good_words.size()) <= 2:
                # if there is one or two valid words, then take the first.
                guess = sorted(good_words.words)[0]
                score = 1/good_words.size()
            else:
                score, guess = good_words.find_best(valid_words.words)[0]
                

            board, good_letters = self.play_word(guess)
            all_guesses.append(guess)

            tmp = ''
            for i in range(5):
                if all_board[i] != '.':
                    tmp += all_board[i]
                elif board[i] != '.':
                    tmp += board[i]
                else:
                    tmp += '.'
            all_board = tmp

            for ch in good_letters:
                all_good_letters.add(ch)

    #        print (">> %s |  %s => %s, %s" % (guess, board, all_board, all_good_letters))

        return all_guesses


def help():
    print("Usage: solver.py board good_letters guess1 {guess2...}")
    print("Usage: solver.py auto work")
    sys.exit(1)


if __name__ == '__main__':

    good_fname = 'data/good.txt'
    valid_fname = 'data/valid.txt'

    last = None
    cmd = ''
    words = []
    all_board = None
    all_good_letters = None
    all_guesses = []
    hard_mode = False
    verbose = False
    show_guesses = 1


    for arg in sys.argv[1:]:
        if arg in ['--help', '-h', 'help']:
            help()
        elif arg == '-v':
            verbose = True
        elif arg == '--hard':
            hard_mode = True
        elif arg in ['--good', '--valid', '--guesses']:
            last = arg
        elif last == '--guesses':
            show_guesses = int(arg)
            last = None
        elif last == '--valid':
            valid_fname = arg
            last = None
        elif last == '--good':
            good_fname = arg
            last = None
        elif arg == 'auto':
            cmd = 'auto'
        elif arg == 'benchmark':
            cmd = 'benchmark'
        elif cmd == 'auto':
            words.append(arg)
        elif not cmd:
            if not all_board:
                all_board = arg
            elif all_good_letters is None:
                all_good_letters = arg.upper()
            else:
                all_guesses.append(arg)

    
    if cmd == 'auto':
        for word in words:
            print("%s => %s" % (word, ','.join(TestWord(word).solve(good_fname, valid_fname, hard_mode))))
            
    elif cmd == 'benchmark':
        # Run a benchmark
        scores = []

        allwords = []

        with open(good_fname, 'rt') as f:
            for line in f:
                allwords.append(line.strip().upper())
        
        for i,word in enumerate(allwords):
            if verbose and i % 10 == 0:
                print("%s/%s" % (i, len(allwords)))

            guesses = TestWord(word).solve(good_fname, valid_fname, hard_mode)
            scores.append(len(guesses))

        min_score = min(scores)
        max_score = max(scores)
        mean_score = sum(scores)/len(scores)

        print ("Min: %s" % min_score)
        print ("Max: %s" % max_score)
        print ("Ave: %s" % mean_score)

        for i in range(max(scores)+1):
            acc = 0
            for score in scores:
                if score == i:
                    acc += 1
            if acc:
                print ("%s guess: %s" % (i, acc))

    else:
        b = Board(all_board, all_good_letters, all_guesses)
        good_words = WordList(good_fname)
        valid_words = WordList(valid_fname)

        good_words.prune(b)

        if hard_mode:
            valid_words.prune(b)

        if good_words.size()== 0:
            print("No valid guesses!")
            sys.exit(1)

        if good_words.size() <= show_guesses:
            i=0
            print("Possible words: %s" % ','.join(sorted(good_words.words)))

        if good_words.size() <= 2:
            for i, guess in enumerate(sorted(good_words.words)):
                if i == 0:
                    print("Guess: %s %.3f (%s word(s) left)" % (guess, 1/good_words.size(), good_words.size()))
                else:
                    print("       %s %.3f" % (guess, 1/good_words.size()))

        else:
            guess_score = good_words.find_best(valid_words.words, show_guesses)

            for i, (score, guess) in enumerate(guess_score):
                if i == 0:
                    print("Guess: %s %.3f (%s words left)" % (guess, score, good_words.size()))
                else:
                    print("       %s %.3f" % (guess, score))


