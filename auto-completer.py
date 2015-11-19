import marisa_trie
import pickle
import random
# import sys
import crossword_visualizer as xword
from crossword_visualizer import GenericBox

#random.seed(30)


#  Loading from the saved state from crossword_visualizer.py's output
#INPUT_XWORD = raw_input('Enter the crossword filename to auto-fill: ')
INPUT_XWORD = 'nov_5_test'
with open(INPUT_XWORD, 'rb') as partial_xword:
    all_boxes = pickle.load(partial_xword)

# May need to modify based on words file format
with open('test_dict_nov_5.txt', 'rb') as words_file:
    word_list = words_file.readlines()
#word_list = word_list[:-1]
word_list = [unicode(word[:-1].upper()) for word in word_list]
random.shuffle(word_list)



# Putting the words into word-length-specific tries
MIN_WORD_LENGTH = 2
MAX_WORD_LENGTH = 21  # Will need to change to the DIM of input puzzle.



# FUNCTIONS RELATED TO DEVELOPING THE APPROPRIATE ASSOCIATIONS BETWEEN OBJECTS AND CLASSES
def make_tries(word_list):
    """Makes a list of Tries. Each trie contains only words of a specific length, in the
    range of [the min (1? 3?) to the dimension of the puzzle [need to change]]
    returns : a list of Trie instances
    """
    tries = []
    for i in range(MIN_WORD_LENGTH):
        tries.append(None)  # Now, Trie word length == index
    for i in range(MIN_WORD_LENGTH, MAX_WORD_LENGTH + 1):
        same_length_words = [word for word in word_list if len(word) == i]
        tries.append(marisa_trie.Trie(same_length_words))
    return tries

def make_word_objects(all_boxes):
    """Initializes all of the Word instances based on the GenericBox instance inputs.
    all_boxes : a list of GenericBox instances, imported from the crossword_visualizer module
    returns : a list of AcrossWord and a list of DownWord instances
    NOTE: does not currently handle single-letter words. Will take a lot of lines of code.
    """
    a_words = []
    d_words = []
    for box in all_boxes:
        if box.num != '':
            across_word = [box]
            down_word = [box]
            r_neighbor = box.right_neighbor
            d_neighbor = box.down_neighbor
            l_neighbor = box.left_neighbor
            u_neighbor = box.up_neighbor
            if MIN_WORD_LENGTH == 1:  # For single-letter words. TO DO...
                pass
            if r_neighbor is not None:
                if r_neighbor.color == xword.WHITE:
                    if l_neighbor is None:
                        while r_neighbor.color == xword.WHITE:
                            across_word.append(r_neighbor)
                            r_neighbor = r_neighbor.right_neighbor
                            if r_neighbor is None:
                                break
                        a_words.append(AcrossWord(across_word))
                    elif l_neighbor.color == xword.BLACK:
                        while r_neighbor.color == xword.WHITE:
                            across_word.append(r_neighbor)
                            r_neighbor = r_neighbor.right_neighbor
                            if r_neighbor is None:
                                break
                        a_words.append(AcrossWord(across_word))
            if d_neighbor is not None:
                if d_neighbor.color == xword.WHITE:
                    if u_neighbor is None:
                        while d_neighbor.color == xword.WHITE:
                            down_word.append(d_neighbor)
                            d_neighbor = d_neighbor.down_neighbor
                            if d_neighbor is None:
                                break
                        d_words.append(DownWord(down_word))
                    elif u_neighbor.color == xword.BLACK:
                        while d_neighbor.color == xword.WHITE:
                            down_word.append(d_neighbor)
                            d_neighbor = d_neighbor.down_neighbor
                            if d_neighbor is None:
                                break
                        d_words.append(DownWord(down_word))
    return a_words, d_words

"""
def make_one_letter_word(letters_list):
    # Start of code to generate single-letter words, if needed. TO DO...
    if r_neighbor is None:
        if l_neighbor is None:
            a_words.append(AcrossWord(across_word))
        elif l_neighbor.color == xword.BLACK:
            a_words.append(AcrossWord(across_word))
"""

def link_intersecting_wds(all_boxes, a_words, d_words):
    """Gives each word an attribute that lists all intersecting Words,
    listed as the Word's unique index
    all_boxes : a list of all GenericBox instances (goes row by row)
    a_words : a list of all AcrossWord instances
    d_words : a list of all DownWord instances
    """
    for box in all_boxes:
        if box.color == xword.WHITE:
            a_word = a_words[box.across_word_id]
            d_word = d_words[box.down_word_id]
            a_word.mates.append(d_word)
            d_word.mates.append(a_word)

def link_across_wds(across_words):
    """Creates two lists of AcrossWords for each AcrossWord instance.
    across_words : a list of all AcrossWord instances
    above_words : a list of the AcrossWords that are directly above the word in
                  question (e.g. (x, y) has (x, y-1))
    below_words : same as above_words, but for below
    """
    for across_word in across_words:
        above_words = []
        below_words = []
        for box in across_word.boxes:
            if box.up_neighbor is not None:
                if box.up_neighbor.color == xword.WHITE:
                    if across_words[box.up_neighbor.across_word_id] not in above_words:
                        above_words.append(across_words[box.up_neighbor.across_word_id])
            if box.down_neighbor is not None:
                if box.down_neighbor.color == xword.WHITE:
                    if across_words[box.down_neighbor.across_word_id] not in below_words:
                        below_words.append(across_words[box.down_neighbor.across_word_id])
        across_word.above_words = above_words
        across_word.below_words = below_words

def multi_parent_indexes(across_words):
    """Sets-up a list that contains a list of all parents for AcrossWords that have multiple words
    above them, and None otherwise. Used for backtracking
    """
    backtrack_multi_parent = [None]*len(across_words)
    for a_word in across_words:
        if len(a_word.above_words) > 1:
            backtrack_multi_parent[a_word.id] = a_word.above_words
    return backtrack_multi_parent

# END FUNCTIONS RELATED TO SETTING UP RELATIONSHIPS



def word_options(word_inst, tries, assigned_words, choice=None):  # 'tries' and 'assigned_words' are unnecessary...
    """Makes a set of possible words that the Word can draw from,
    given the current filled-in set of boxes. This set is stored in
    the wd_opts attribute of the word_inst.
    word_inst = the Word instance of interest
    tries = list of tries from the input dict
    assigned_words = the set of words already assigned

    NOTE: if I want to make it shuffle, will need to keep wd_opts as a list, not a set.
    """
    start = word_inst.start_of_word()
    unfiltered_options = tries[len(word_inst.boxes)].keys(start) # Include a shuffle if above_words = None?
    word_inst.wd_opts = set(unfiltered_options)
    filt_wd_opts = []
    for i in range(max(len(start), 1), len(word_inst.word)):  # For user-supplied letters/words.
        if word_inst.word[i] != '-':
            for wd in word_inst.wd_opts:
                if word_inst.word[i] == wd[i]:
                    filt_wd_opts.append(wd)
            word_inst.wd_opts = set(filt_wd_opts)
            filt_wd_opts = []
    for wd in assigned_words:
        if wd in word_inst.wd_opts:
            word_inst.wd_opts.remove(wd)
    if choice is not None:  # for DownWords
        if choice in word_inst.wd_opts:
            word_inst.wd_opts.remove(choice)
    word_inst.wd_opts = list(word_inst.wd_opts)
    if word_inst.boxes[1].location[1] == 0:
        random.shuffle(word_inst.wd_opts)

def are_downs_complete(a_word):
    """Small helper fn to improve the readability of main().
    Adds any completed DownWords to the assigned_words set and list of completed DownWords
    """
    for d_word in a_word.mates:
        if '-' not in d_word.word:
            assigned_words.add(d_word.word)
            finished_down_words[d_word.id] = d_word

def clear_all():
    """Clears all words to free up all possible words that weren't preassigned.
    """
    for a_word in across_words:
        reset_word_and_below(a_word)
        a_word.wd_opts = []
    for multi in backtrack_multi_parent[:max_multi.id]:
        if multi is not None:
            multi.above_words = sorted(multi.above_words)

def reset_word_and_below(a_word):
    """Resets the values of an AcrossWord, removing any assigned word.
    Also calls reset_downs(), which addresses potential changes to DownWord completion.
    Also calls reset_below(), which removes any assigned words from below_words
    and also resets the below_words' wd_opts to an empty set.
    """
    if a_word.word in assigned_words:
        assigned_words.remove(a_word.word)
        finished_across_words[a_word.id] = None
        a_word.word = a_word.original_word
        a_word.update_word(a_word.word)
    reset_downs(a_word)
    reset_below(a_word)

def reset_below(a_word):
    """Resets all of a given Word's 'children' below to their initial states.
    Called in the reset_word_and_below() function.
    a_word : the word whose children need to be reset
    """
    for child in a_word.below_words:
        if child.word != child.original_word:  # Need to account for presupplied words?
            assigned_words.remove(child.word)
            finished_across_words[child.id] = None
            child.word = child.original_word
            child.update_word(child.word)
            child.wd_opts = set()
            reset_downs(child)
            reset_below(child)

def reset_downs(a_word):
    """Updates DownWords to reflect backtracking. Removes formerly completed DownWords
    from appropriate lists.
    """
    for d_word in a_word.mates:
        old_d_word = d_word.word
        d_word.update_word()
        if '-' in d_word.word:
            finished_down_words[d_word.id] = None
            if old_d_word in assigned_words:
                assigned_words.remove(old_d_word)


def reset_multi_parent_slice(index):
    """Resets partially-run-through lists of above_words when the index has advanced beyond
    any (if any) AcrossWords with more than one above_word.
    index : the index i of the selected above_word from the list of above_words
    """
    for i in range(index + 1):
        if len(across_words[i].above_words) > 1:
            backtrack_multi_parent[i] = across_words[i].above_words


def backtrack(a_word, i):
    """Called when no viable options exist for an AcrossWord. Tries to find other viable
    options for above_words (predecessors).
    a_word : the word with no options left
    i : bookkeeping index
    returns : i
    """
    #resets_counter = {i : 0 for i in range(len(across_words))}  # would need to make global
    #resets_counter[max_i] += 1
    if len(a_word.above_words) == 0 and i == 0:  # NEED ANOTHER TERMINATION CONDITION TO PREVENT INF LOOPS
        print 'len 0', i
        if max_multi.above_words == sorted(max_multi.above_words) and max_multi.id == max_i:
            raise RuntimeError('No solution found. Gone through every starting word.')
        else:
            #resets_counter[max_i] += 1
            clear_all()  # need to check that this is implemented correctly.
            return 0
    elif len(a_word.above_words) == 0:
        for index in range(i, max_i + 1):  # max_i is global, from main()
            if backtrack_multi_parent[index] is not None:  # could just have if len(across_words.above_words) > 1:
                parent = backtrack_multi_parent[index].pop()
                backtrack_multi_parent[index].insert(0, parent)
                if parent.presupplied is True:
                    return backtrack(parent, parent.id)
                elif parent.word != parent.original_word:
                    reset_word_and_below(parent)
                    return parent.id
                else:
                    raise IndexError('Trying to backtract on a word that is already reset.')
                #new_a_word = backtrack_multi_parent[index].pop()
                #return backtrack(new_a_word, new_a_word.id)
                #except IndexError:
                #    print 'No solution found. Multi-above_words list empty'
                #    sys.exit(1)
        # If you haven't gotten to a multi-parent yet, but still have separate columns of AcrossWords
        return backtrack(across_words[max_i - 1], max_i - 1)
    elif len(a_word.above_words) == 1:
        print 'len 1', i
        parent = a_word.above_words[0]
        if parent.presupplied is True:
            return backtrack(parent, parent.id)
        else:
            reset_word_and_below(parent)
            return parent.id
            # return finished_across_words.index(None)
    elif len(a_word.above_words) > 1:
        parent = a_word.above_words.pop()
        a_word.above_words.insert(0, parent)
        if parent.presupplied is True:
            return backtrack(parent, parent.id)
        else:
            reset_word_and_below(parent)
            return parent.id
        #try:
        #    next_backtrack = backtrack_multi_parent[a_word.id].pop()
        #    i = next_backtrack.id
        #    reset_multi_parent_slice(i)
        #    #reset_word_and_below(next_backtrack)
        #    return finished_across_words.index(None) # or i??
        #except IndexError:  # IS THIS IMPLEMENTED CORRECTLY?
        #    print 'No solution found. No more parents to try to backtrack on.'
    else:
        raise ValueError('Something is wrong with the above_words for %s' % a_word)
"""
what if I had a tracker for the ordering of the above_words for words with multiple above_words,
and if backtrack(i = 0) was called, then there would be a check if the maximum-indexed multi-above_word
Word had its above_words in starting order (i.e. it had permuted through all combinations. If not,
then clear_all would be called, and the finder would start all over again. NOTE: would also have
to reset the ordering of the multi-above_words for all such multis less than the max multi.
"""

def find_word(a_word, i):  # or just i?
    """Finds a valid word to input for a given AcrossWord
    a_word : an AcrossWord
    i : a bookkeeping index
    """
    old_i = i
    global max_multi
    #print max_multi
    #if max_i == 0:
    #    clear_all()
    if len(a_word.above_words) > 1:
        if a_word > max_multi:
            max_multi = a_word
    # If word is user-supplied. Could make this an initialization instead - would be better.
    if a_word.presupplied is True:
        finished_across_words[a_word.id] = a_word
        assigned_words.add(a_word.word)
        try:
            i = finished_across_words.index(None)
        except ValueError:
            i = len(across_words)
        return i
    # If word is not user supplied:
    if len(a_word.wd_opts) == 0:
        word_options(a_word, tries, assigned_words)
        # if not, will continue with a partially run-through list of wd_opts
    while len(a_word.wd_opts) > 0:  # This takes O(len(wd_opts)*len(choice)). Improvable?
        bad_choice = False
        choice = a_word.wd_opts.pop()
        a_word.update_word(choice)
        for d_word in a_word.mates:
            d_word.update_word()
            word_options(d_word, tries, assigned_words, choice)
            if len(d_word.wd_opts) == 0 and finished_down_words[d_word.id] is None:
                bad_choice = True
                a_word.update_word(a_word.original_word)
                for d_word in a_word.mates:  # is this necessary here?
                    d_word.update_word()
                break
        if bad_choice is False:
            are_downs_complete(a_word)
            finished_across_words[a_word.id] = a_word
            assigned_words.add(a_word.word)
            try:
                i = finished_across_words.index(None)  # this will take O(len(f_a_w))
            except ValueError:
                i = len(across_words)  # just to break out of the cycle. could probably neaten up
            break
    if i == old_i:  # add in len(a_word.wd_opts) == 0?
        a_word.update_word(a_word.original_word)  # removes the final 'choice' from being a_word.word
        return backtrack(a_word, i)
    return i


def main():
    global max_i
    global max_multi
    i = 0
    max_i = i
    max_multi = next(word for word in across_words if len(word.above_words) > 1)  # NOTE: type == AcrossWord, not int
    while i < len(across_words):
        if max_i < i:
            max_i = i
            print max_i
        i = find_word(across_words[i], i)
    print 'A solution was found!'
    output_file = INPUT_XWORD + '_output'
    with open(output_file, 'wb') as output:
        pickle.dump(all_boxes, output)


class Word(object):

    def __init__(self, boxes):
        self.boxes = boxes
        self.presupplied = False
        self.original_word = self.make_word()
        self.is_word_presupplied(self.original_word)
        self.word = self.original_word
        self.wd_opts = set()  # implemented as a set (currently)
        self.mates = []  # list of intersecting words
        self.partial_wd_opts = set()  # to continue with until exhausted in backtracking

    def make_word(self):  # change to just a set?
        """Returns the current word in the Word, with dashes for
        unfilled letters.
        """
        word = ''
        for box in self.boxes:
            if box.letter != '':
                word += box.letter
            elif box.letter == '':
                word += '-'
        return unicode(word)

    def is_word_presupplied(self, original_word):
        if '-' not in original_word:
            self.presupplied = True

    def reset_word(self):
        """To be used in backtracking steps. Makes the is_immutable attribute of
        GenericBox pointless, I believe.
        """
        self.word = self.original_word

    def start_of_word(self):
        start_of_word = ''
        for letter in self.word:
            if letter != '-':
                start_of_word += letter
            else:
                break
        return unicode(start_of_word)


class AcrossWord(Word):
    across_counter = 0

    def __init__(self, boxes):
        super(AcrossWord, self).__init__(boxes)
        self.id = AcrossWord.across_counter
        self.link_boxes(boxes)
        self.above_words = []
        self.below_words = []
        AcrossWord.across_counter += 1

    def link_boxes(self, boxes):
        """Adds a new attribute to the boxes in the word, linking the
        word to those boxes.
        """
        for box in boxes:
            box.across_word_id = self.id

    def update_word(self, wd_choice):
        """Updates the letter assignments of the GenericBox objects that make up the Word.
        """
        for i in range(len(self.boxes)):
            self.boxes[i].set_letter(wd_choice[i])
        self.word = self.make_word()

    def __lt__(self, other):
        return self.id < other.id

    def __gt__(self, other):
        return self.id > other.id

    def __repr__(self):
        return "'%s Across: %s'" % (self.id, self.word)


class DownWord(Word):
    down_counter = 0

    def __init__(self, boxes):
        super(DownWord, self).__init__(boxes)
        self.id = DownWord.down_counter
        self.link_boxes(boxes)
        DownWord.down_counter += 1

    def link_boxes(self, boxes):
        """Same method as for AcrossWord, but Down instead.
        """
        for box in boxes:
            box.down_word_id = self.id

    def update_word(self):
        """Updates word to reflect the GenericBox.letter values
        """
        self.word = self.make_word()

    def __repr__(self):
        return "'%s Down: %s'" % (self.id, self.word)


tries = make_tries(word_list)
across_words, down_words = make_word_objects(all_boxes)  # MAKE A DEQUE?
link_intersecting_wds(all_boxes, across_words, down_words)
link_across_wds(across_words)
backtrack_multi_parent = multi_parent_indexes(across_words)


# globals for the next set of functions (also draw from vars in the above few lines)
assigned_words = set()
finished_across_words = [None]*len(across_words)
finished_down_words = [None]*len(down_words)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print '    max_i:', max_i
        print '      across_words:', finished_across_words
        #print '      partial solution placed in input file'
        #with open(INPUT_XWORD, 'wb') as output_file:
        #    pickle.dump(all_boxes, output_file)
