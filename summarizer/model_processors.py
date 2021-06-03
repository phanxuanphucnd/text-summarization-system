# -*- coding: utf-8 -*-

from .BertParent import BertParent
from typing import List
from .ClusterFeatures import ClusterFeatures
from abc import abstractmethod
import neuralcoref
from spacy.lang.vi import Vietnamese
import underthesea
from vncorenlp import VnCoreNLP
import numpy as np
from transformers import PreTrainedModel, PreTrainedTokenizer
from string import punctuation
import re
from nltk.tokenize import sent_tokenize


class ModelProcessor(object):

    def __init__(
            self,
            model='bert-base-multilingual-uncased',
            custom_model: PreTrainedModel = None,
            custom_tokenizer: PreTrainedTokenizer = None,
            hidden: int = -2,
            reduce_option: str = 'mean',
            greedyness: float = 0.45,
            language=Vietnamese,
            random_state: int = 12345,
            max_words: int = -1
    ):

        """
        :param model: bert encoder model
        :param custom_model: Transformers-based Model
        :param custom_tokenizer: Transformers-based Tokenizer
        """
        np.random.seed(random_state)
        self.model = BertParent(model, custom_model, custom_tokenizer)
        self.hidden = hidden
        self.reduce_option = reduce_option
        self.nlp = language()
        self.random_state = random_state
        self.nlp.add_pipe(self.nlp.create_pipe('sentencizer'))
        self.rdrsegmenter = VnCoreNLP(
            f"./summarizer/vncorenlp/VnCoreNLP-1.1.1.jar", annotators="wseg", max_heap_size='-Xmx500m')
        self.map = dict()
        neuralcoref.add_to_pipe(self.nlp, greedyness=greedyness)
        self.max_words = max_words

    def process_content_sentences(self, body: str, min_length=30, max_len=20) -> List[str]:
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
            max_len=20
        paragraphs = body.split('\n')
        paragraphs = [(i, x) for i, x in enumerate(paragraphs)]
        brief = paragraphs[0]
        paragraphs = paragraphs[1:]
        paragraphs.sort(key=lambda s: len(s[1]), reverse=True)
        p = max(0, len(paragraphs) - 8)
        paragraphs = [brief] + paragraphs[p:]
        paragraphs = [x[1] for x in paragraphs]

        raw_sents = []
        for paragraph in paragraphs:
            if paragraph[-1] not in punctuation:
                paragraph += '.'
            raw_sents.extend(sent_tokenize(paragraph))
        train_sents = list()
        number_of_words = 0
        for r_sent in raw_sents:
            words = self.rdrsegmenter.tokenize(r_sent)
            number_of_words += len(words[0])
            sent = [' '.join(word) for word in words][0]
            if len(sent) > min_length and len(words[0]) <= max_len and len(words[0]) > 5:
                train_sents.append(sent)
                self.map[sent] = r_sent
        return train_sents, number_of_words

    @abstractmethod
    def run_clusters(self, content: List[str], ratio=0.2, algorithm='kmeans', use_first: bool = True, no_words=100,
                     max_words=-1) -> List[str]:
        raise NotImplementedError("Must Implement run_clusters")

    def run(
            self,
            body: str,
            ratio: float = 0.2,
            min_length: int = 40,
            max_words: int = -1,
            use_first: bool = True,
            algorithm='kmeans'
    ) -> str:
        """Function to get summarization of document
        :param body: document text
        :param min_length: Minimum length of a sentence
        :param max_len: Maximum words in a sentence
        :param algorithm: Algorithm to cluster document (default: kmeans)
        :returns: summarization in a paragraph
        """
        self.max_words = max_words
        sentences, no_words = self.process_content_sentences(
            body, min_length, max_len=max_words)
        if sentences:
            sentences = self.run_clusters(
                sentences, ratio, algorithm, use_first, no_words, self.max_words)

        return ' '.join([self.map[sent] for sent in sentences])

    def __call__(self, body: str, ratio: float = 0.2, min_length: int = 40,
                 use_first: bool = True, algorithm='kmeans', max_words=-1) -> str:
        return self.run(body, ratio, min_length, max_words=max_words)


class SingleModel(ModelProcessor):
    """
    Deprecated for naming sake.
    """

    def __init__(
            self,
            model='bert-base-multilingual-uncased',
            custom_model: PreTrainedModel = None,
            custom_tokenizer: PreTrainedTokenizer = None,
            hidden: int = -2,
            reduce_option: str = 'mean',
            greedyness: float = 0.45,
            language=Vietnamese,
            random_state: int = 12345,
            max_words: int = -1
    ):
        """
        :param model: bert encoder model
        :param custom_model: Transformers-based Model
        :param custom_tokenizer: Transformers-based Tokenizer
        """
        self.max_words = max_words
        super(SingleModel, self).__init__(model, custom_model, custom_tokenizer, hidden, reduce_option,
                                          greedyness, language=language, random_state=random_state, max_words=max_words)

    def run_clusters(self, content: List[str], ratio=0.2, algorithm='kmeans', use_first: bool = True,
                     no_words: int = 100, max_words=-1) -> List[str]:
        """Function to get summarization of document
        :param content: list of valid sentences in document
        :param ratio: ratio for summarization
        :param no_words: Number of valid words in document
        :param max_words: Maximum words in a sentence
        :param algorithm: Algorithm to cluster document (default: kmeans)
        :returns: list of summarized sentences
        """
        hidden = self.model(content, self.hidden, self.reduce_option)
        hidden_args = ClusterFeatures(
            hidden, algorithm, random_state=self.random_state).cluster(ratio, no_words, max_words=max_words)

        if use_first:
            if hidden_args[0] != 0:
                hidden_args.insert(0, 0)

        return [content[j] for j in hidden_args]


class Summarizer(SingleModel):

    def __init__(
            self,
            model='bert-base-multilingual-uncased',
            custom_model: PreTrainedModel = None,
            custom_tokenizer: PreTrainedTokenizer = None,
            hidden: int = -2,
            reduce_option: str = 'mean',
            greedyness: float = 0.45,
            language=Vietnamese,
            random_state: int = 12345,
            max_words: int = -1
    ):
        """
        :param model: bert encoder model
        :param custom_model: Transformers-based Model
        :param custom_tokenizer: Transformers-based Tokenizer
        """
        super(Summarizer, self).__init__(model, custom_model, custom_tokenizer,
                                         hidden, reduce_option, greedyness, language, random_state, max_words=max_words)
