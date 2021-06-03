# -*- coding: utf-8 -*-

import numpy as np
from numpy import ndarray
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from typing import List


class ClusterFeatures(object):

    def __init__(
        self,
        features: ndarray,
        algorithm: str = 'kmeans',
        pca_k: int = None,
        random_state: int = 12345
    ):
        """
        :param features: input features
        :param algorithm: algorithm to cluster (default: kmeans)
        :param pca_k: reduce number of dimensions by PCA or not
        :param random_state: random state for algorithm
        """
        if pca_k:
            self.features = PCA(n_components=pca_k).fit_transform(features)
        else:
            self.features = features

        self.algorithm = algorithm
        self.pca_k = pca_k
        self.random_state = random_state

    def __get_model(self, k: int):
        """ Function to get clustering model
        :param k: number of clusters
        :returns: KMeans model with parameters
        """
        if self.algorithm == 'gmm':
            return GaussianMixture(n_components=k, random_state=self.random_state)
        return KMeans(n_clusters=k, random_state=self.random_state)

    def __get_centroids(self, model):
        """ Function to get center point of a cluster
        :param model: clustering model
        :returns: center point value of a cluster
        """
        if self.algorithm == 'gmm':
            return model.means_
        return model.cluster_centers_

    def __find_closest_args(self, centroids: np.ndarray):
        """ Function to get center sentence of a cluster
        :param centroids: center point of cluster
        :returns: Center sentence with the most important meaning of paragraph
        """
        centroid_min = 1e10
        cur_arg = -1
        args = {}
        used_idx = []

        for j, centroid in enumerate(centroids):

            for i, feature in enumerate(self.features):
                value = np.linalg.norm(feature - centroid)

                if value < centroid_min and i not in used_idx:
                    cur_arg = i
                    centroid_min = value

            used_idx.append(cur_arg)
            args[j] = cur_arg
            centroid_min = 1e10
            cur_arg = -1

        return args

    def cluster(self, ratio: float = 0.1, no_words: int = 0, max_words: int = 40) -> List[int]:
        """ Function to apply clustring model to document
        :param ratio: ratio for summarization
        :param no_words: number of valid words in document
        :param max_words: maximum number of words in summarized doc.
        :returns: Summarized document
        """
        if max_words != -1:
            if ratio * no_words > max_words:
                ratio = max_words / no_words
        k = 3 if ratio * \
            len(self.features) < 3 else int(len(self.features) * ratio)
        k = min(k, len(self.features))
        k = min(k, 8)
        model = self.__get_model(k).fit(self.features)
        centroids = self.__get_centroids(model)
        cluster_args = self.__find_closest_args(centroids)
        sorted_values = sorted(cluster_args.values())
        return sorted_values

    def __call__(self, ratio: float = 0.1) -> List[int]:
        return self.cluster(ratio)
