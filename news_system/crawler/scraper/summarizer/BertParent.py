# -*- coding: utf-8 -*-

from transformers import *
import logging
import torch
import numpy as np
from numpy import ndarray
from typing import List

logging.basicConfig(level=logging.WARNING)


class BertParent(object):

    MODELS = {
        'bert-base-multilingual-uncased': (BertModel, BertTokenizer),
        'bert-base-uncased': (BertModel, BertTokenizer),
        'bert-large-uncased': (BertModel, BertTokenizer),
        'xlnet-base-cased': (XLNetModel, XLNetTokenizer),
        'xlm-mlm-enfr-1024': (XLMModel, XLMTokenizer),
        'distilbert-base-uncased': (DistilBertModel, DistilBertTokenizer),
        'vinai/phobert-base': (AutoModel, AutoTokenizer),
        'vinai/phobert-large': (AutoModel, AutoTokenizer),
    }

    def __init__(
        self,
        model: str,
        custom_model: PreTrainedModel = None,
        custom_tokenizer: PreTrainedTokenizer = None
    ):
        """
        :param model: Model is the string path for the bert weights. If given a keyword, the s3 path will be used
        :param custom_model: This is optional if a custom bert model is used
        :param custom_tokenizer: Place to use custom tokenizer
        """

        base_model, base_tokenizer = self.MODELS.get(model, (None, None))

        if custom_model:
            self.model = custom_model
        else:
            self.model = base_model.from_pretrained(
                model, output_hidden_states=True)

        if custom_tokenizer:
            self.tokenizer = custom_tokenizer
        else:
            self.tokenizer = base_tokenizer.from_pretrained(model)

        self.model.eval()

    def tokenize_input(self, text: str) -> torch.tensor:
        """Function to tokenize the text input.

        :param text: Text to tokenize

        :returns: Returns a torch tensor: [1, 2, 5, ...]
        """
        tokenized_text = self.tokenizer.tokenize(text)
        indexed_tokens = self.tokenizer.convert_tokens_to_ids(tokenized_text)
        return torch.tensor([indexed_tokens])

    def extract_embeddings(
        self,
        text: str,
        hidden: int = -2,
        squeeze: bool = False,
        reduce_option: str = 'mean'
    ) -> ndarray:
        """Function to generate vector embedding of text

        :param text: input text
        :param hidden: number of hidden layer
        :param squeeze: squeeze output or not
        :param reduce_option: type to calculate sentence embedding

        :returns: Embedding vector for input text
        """
        tokens_tensor = self.tokenize_input(text)
        pooled, hidden_states = self.model(tokens_tensor)[-2:]

        if -1 > hidden > -12:

            if reduce_option == 'max':
                pooled = hidden_states[hidden].max(dim=1)[0]

            elif reduce_option == 'median':
                pooled = hidden_states[hidden].median(dim=1)[0]

            else:
                pooled = hidden_states[hidden].mean(dim=1)

        if squeeze:
            return pooled.detach().numpy().squeeze()

        return pooled

    def create_matrix(
        self,
        content: List[str],
        hidden: int = -2,
        reduce_option: str = 'mean'
    ) -> ndarray:
        """Function to generate matrix of vector embedding for list of text

        :param content: input list of text
        :param hidden: number of hidden layer
        :param reduce_option: type to calculate sentence embedding

        :returns: Embedding matrix for input.
        """

        return np.asarray([
            np.squeeze(self.extract_embeddings(t, hidden=hidden,
                                               reduce_option=reduce_option).data.numpy())
            for t in content
        ])

    def __call__(
        self,
        content: List[str],
        hidden: int = -2,
        reduce_option: str = 'mean'
    ) -> ndarray:
        return self.create_matrix(content, hidden, reduce_option)
