import nltk
import os
import sys
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files = os.listdir(directory)
    # Maps documents to the file content
    file_to_text = dict()
    for page in files:
        text = open(os.path.join(directory, page), encoding='utf8')
        file_to_text[page] = text.read()
    return file_to_text


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    unfiltered_tokens = nltk.word_tokenize(document)
    # List with only non-stopword, non-punctuation words
    filtered_tokens = list()
    for token in unfiltered_tokens:
        filtered_word = token.lower()
        if filtered_word in nltk.corpus.stopwords.words("english"):
            continue

        if filtered_word in string.punctuation:
            continue

        filtered_tokens.append(filtered_word)

    return filtered_tokens


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    # Maps word to set of documents it's in
    word_doc_freq = dict()
    for document in documents:
        for word in documents[document]:
            if word not in word_doc_freq:
                # First occurance of word
                word_doc_freq[word] = set()
            word_doc_freq[word].add(document)

    total_documents = len(documents)
    word_to_idf = {
        word: math.log(total_documents / len(word_doc_freq[word]))
        for word in word_doc_freq
    }

    return word_to_idf


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    # The total tfidf value of all query words in document
    doc_tfidf = dict()
    for doc in files:
        # Maps query words to their tf-idf
        tf_idfs = dict()
        for word in query:
            # First we get each words term frequency
            tf_idfs[word] = files[doc].count(word)

        # Multiply term frequency by idf of each word
        tf_idfs = {
            word: idfs[word] * tf_idfs[word]
            for word in tf_idfs
            # Avoid error of using new word as key
            if word in idfs
        }
        doc_tfidf[doc] = sum(tf_idfs.values())

    # We get a list of the keys sorted by their values
    docs = sorted(doc_tfidf, key=lambda x: doc_tfidf[x], reverse=True)
    return docs[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    # Maps a sentence to its sum idf value
    sentence_idf = dict()
    # Maps a sentence to its qtd
    sentence_qtd = dict()
    for sentence in sentences:
        sentence_idf[sentence] = 0
        sentence_qtd[sentence] = 0

        for word in query:
            if word in sentences[sentence]:
                sentence_idf[sentence] += idfs[word]
            sentence_qtd[sentence] += sentences[sentence].count(word)

        sentence_qtd[sentence] /= len(sentences[sentence])

    # Maps sentence to a tuple containing its sum idf and qtd
    sent_data = {
        sent: (sentence_idf[sent], sentence_qtd[sent])
        for sent in sentences
    }

    # I used a tuple since the second element acts as tiebreaker
    # for documents with the same first value
    sents = sorted(sent_data, key=lambda x: sent_data[x], reverse=True)
    return sents[:n]


if __name__ == "__main__":
    main()
