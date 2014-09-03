import re
from bs4 import element
from .segment import Segment
from .functions import cosine_similarity

list_tags = ["ul", "ol", "dl"]
inline_elements = ["b", "big", "i", "small", "tt", "abbr", "acronym", "cite",
                   "code", "dfn", "em", "kbd", "strong", "samp", "var", "a",
                   "bdo", "br", "img", "map", "object", "q", "script", "span",
                   "sub", "sup", "button", "input", "label", "select", "textarea",
                   "cufontext", "cufon"]


def word_set(tag):
    """
    Returns a set of words from tag or NavigableString.
    @param tag: element.Tag or element.NavigableString
    @return: set of words
    """
    reg = "[^\W\d_]+"

    if isinstance(tag, element.Tag):
        found = re.findall(reg, tag.text, re.UNICODE)
    else:
        found = re.findall(reg, unicode(tag), re.UNICODE)
    return {i.lower() for i in found}


def change_tag(x):
    """
    Changes tag to a comparable representation.
    @param x: Tag or NavigableString
    @return: true if a tag, false otherwise
    """
    if isinstance(x, element.Tag):
        return x.name
    else:
        return "text"


def filter_tag(x, i):
    """
    Checks if to go into an element.
    @param x: Tag or NavigableString
    @return: true if a tag, false otherwise
    """
    if x in inline_elements or x == "text":
        return -1
    else:
        return i


def sequence_compare(sq1, sq2):
    """
    Compare tag sequences.
    @param sq1: sequence 1
    @param sq2: sequence 2
    @return: True if similar or False otherwise
    """
    return sq1 == sq2


def set_compare(s1, s2):
    """
   Compare word sets.
    @param s1: set 1
    @param s2: set 2
    @return: True if similar or False otherwise
    """
    return s1 == s2


def unique_sets(sets):
    if len(sets[0]) > 0:
        for i in xrange(len(sets)):
            for j in range(i, len(sets)):
                if set_compare(sets[i], sets[j]):
                    return False
        return True
    return False


def cases(tags, treshold):
    """
    Analyze and check different cases.
    @param tags: all tags
    @param treshold: similarity threshold
    @return: sequence of ids to check
    """
    # @todo conditions about lists
    # if all(x.name in list_tags for x in tags):

    sequences = map(lambda one: map(change_tag, one.children), tags)

    # do tags have the same children sequences
    if all(sequence_compare(sequences[0], seq) for seq in sequences[1:]) and (len(sequences[0]) != 0):


        # get a mapping
        filtered = [filter_tag(sequences[0][i], i) for i in range(len(sequences[0]))]

        if all(f == -1 for f in filtered) and len(filtered) > 0:

            ielements = map(lambda x: x.contents[i], tags)
            sets = map(word_set, ielements)

            if unique_sets(sets):
                return map(lambda sg: [Segment(sg)], tags), True
        return filtered, False

    # otherwise, this is a segment
    else:
        # print sequences
        return map(lambda sg: [Segment(sg)], tags), True


def concurent_search(tags, treshold):
    """
    Main function for concurently searching the tree.
    @param tags: roots of the trees
    @param treshold: maximum similarity difference
    @return: list of segments
    """
    if all([hasattr(tag, "children") for tag in tags]):

        filtered, is_segment = cases(tags, treshold)

        if is_segment:
            return filtered
        else:
            rets = [[] for _ in xrange(len(tags))]
            for i in range(len(filtered)):
                if filtered[i] != -1:
                    cnvs = map(lambda x: x.contents[filtered[i]], tags)
                    cas = concurent_search(cnvs, treshold)
                    for r, c in zip(rets, cas):
                        r.extend(c)

            return rets


def filter_out(x):
    """
    Checks if a segment contains something more than links and numbers.
    POSTPROCESS
    @param x: segment object
    @return: True or False
    """

    # if x.name in ["time", "a"]:
    # return False

    wrong = 0
    all_letters = 0

    for i in x.tags:
        if isinstance(i, element.Tag):
            reject = i.find_all(['a', 'time'])

            digit_reg = re.compile("\d", re.UNICODE)
            links_nums = sum([len(digit_reg.findall(j.text)) for j in reject])
            nums = len(digit_reg.findall(i.text))

            word_reg = re.compile("\w", re.UNICODE)
            links_all = sum([len(word_reg.findall(j.text)) for j in reject])

            all_letters += len(word_reg.findall(i.text))
            wrong += nums - links_nums + links_all

    # arbitrary 0.5
    if all_letters * 0.5 < wrong:
        return False
    else:
        return True


# def simplify(segment):
#
# parent = segment.tags[0].parent
#
# ch = filter(lambda x: x not in inline_elements, parent.contents)
# if len(segment.tags) == len(ch):
#         segment.tags = [parent]
#         simplify(segment)


def tree_segmentation(base, treshold=0.9):
    """
    Top level tree segmentation algorithm.
    @param base: list of root tags to analyze
    @param treshold: similarity threshold
    @return: n lists of segments
    """
    if len(base) < 2:
        return None

    base_tags = map(lambda x: x.tags[0], base)

    converted = concurent_search(base_tags, treshold)

    # for i in converted:
    # for j in i:
    # simplify(j)

    return [filter(filter_out, a) for a in converted]

