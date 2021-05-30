# -*- coding: utf-8 -*-

from typing import List
from underthesea import sent_tokenize, word_tokenize
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.stemmers import Stemmer
from sumy.summarizers.text_rank import TextRankSummarizer
from vncorenlp import VnCoreNLP
from string import punctuation
import re

# rdrsegmenter = VnCoreNLP(
#             f"./summarizer/vncorenlp/VnCoreNLP-1.1.1.jar", annotators="wseg", max_heap_size='-Xmx500m')

class Tokenizer:
    @staticmethod
    def to_sentences(text: str) -> List[str]:
        return sent_tokenize(text)

    @staticmethod
    def to_words(sentence: str) -> List[str]:
        return word_tokenize(sentence)


class ViTextRank:
    def __init__(self):
        stemmer = Stemmer("ja")
        self.summarizer = TextRankSummarizer(stemmer)
        self.summarizer.stop_words = self.get_stop_words()
        self.bonus_words = frozenset()
        self.map = dict()

    def process_content_sentences(self, body: str, min_length=30, max_len=25) -> List[str]:
        """Function to preprocess document
        :param body: document text
        :param min_length: Minimum length of a sentence
        :param max_len: Maximum words in a sentence
        :returns: List of valid sentence to summary
        """
        body = re.sub('(?<=\d). (?=\d)', '.', body)
        if max_len < 0:
            max_len = 30
        else:
            max_len = 20
        paragraphs = body.split('\n')
        raw_sents = []
        for paragraph in paragraphs:
            if paragraph[-1] not in punctuation:
                paragraph += '.'
            raw_sents.extend(sent_tokenize(paragraph))
        train_sents = list()
        number_of_words = 0
        for r_sent in raw_sents:
            sent = word_tokenize(r_sent, format="text")
            words = sent.split()
            number_of_words += len(words)
            if len(sent) > min_length and len(words) <= max_len and len(words) > 5:
                train_sents.append(sent)
                self.map[sent] = r_sent
        return train_sents, number_of_words

    def get_stop_words(self):
        """Function to get vietnamese common stopwords
        :returns: List of stopwords
        """
        with open("summarizer/vi_stopwords.txt", 'r', encoding='utf8') as f:
            lines = f.readlines()
        return frozenset(lines)

    def run(self, doc, ratio=0.2, min_length=30, max_words=-1):
        """ Function to apply clustring model to document
        :param ratio: ratio for summarization
        :param min_length: Minimum length of a sentence
        :param max_words: maximum number of words in summarized doc.
        :returns: Summarized document
        """
        sentences, no_words = self.process_content_sentences(
            doc, min_length, max_len=max_words)

        doc = "\n".join(sentences)

        origin = PlaintextParser.from_string(doc, Tokenizer())

        n_sent = round(len(origin.document.sentences) * ratio)
        if n_sent < 3:
            n_sent = 3
        n_sent = min(n_sent, 8)

        eval_sent = self.summarizer(origin.document, n_sent)
        result = ' '.join([self.map[str(sent)] for sent in eval_sent])
        # print("===>", result)
        return result.strip()
