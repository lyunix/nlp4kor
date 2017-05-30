import gzip
import pickle

import numpy as np

from bage_utils.one_hot_vector import OneHotVector
from nlp4kor.config import log


class DataSet(object):
    def __init__(self, features: np.ndarray, labels: np.ndarray, features_vector: OneHotVector, labels_vector: OneHotVector, name: str = ''):
        """
        
        :param features: list of data
        :param labels: list of one hot vector 
        """
        self.is_one_hot_vector = False
        self.name = name
        self.features = features if type(features) is np.ndarray else np.array(features)
        self.labels = labels if type(labels) is np.ndarray else np.array(labels)
        self.size = min(len(self.features), len(self.labels))
        self.features_vector = features_vector
        self.labels_vector = labels_vector

        if len(self.labels) > self.size:
            self.labels = self.labels[:self.size]
        if len(self.features) > self.size:
            self.features = self.features[:self.size]

    def next_batch(self, batch_size=50):
        splits = len(self.features) // batch_size
        if len(self.features) % batch_size > 0:
            splits += 1
        # for features_batch, labels_batch in zip(np.array_split(self.features, splits),
        #                                         ListUtil.chunks_with_size(self.labels, chunk_size=batch_size)):
        for features_batch, labels_batch in zip(np.array_split(self.features, splits), np.array_split(self.labels, splits)):
            yield features_batch, labels_batch

    def __repr__(self):
        return '%s "%s" (feature: %s, label:%s, size: %s)' % (self.__class__.__name__, self.name, type(self.features[0]), type(self.labels[0]), self.size)

    def __len__(self):
        return self.size

    def to_one_hot_vector(self):
        _features, _labels = [], []
        for i, (chars, has_space) in enumerate(zip(self.features, self.labels)):
            # chars = list([c for c in chars])  # characters.
            chars_v = self.features_vector.to_vectors(chars)
            # chars_v = list([v for v in chars_v])
            feature = np.concatenate(chars_v)  # concated feature
            label = self.labels_vector.to_vector(has_space)

            _features.append(feature)
            _labels.append(label)

            if i % 1000 == 0:
                log.info('[%s] %s -> %s, %s (len=%s) %s (len=%s)' % (i, chars, label, feature, len(feature), label, len(label)))
        d = DataSet(_features, _labels, self.features_vector, self.labels_vector)
        d.is_one_hot_vector = True
        return d

    @classmethod
    def load(cls, filepath: str, gzip_format=False, to_one_hot_vector=False):
        if gzip_format:
            with gzip.open(filepath, 'rb') as f:
                d = pickle.load(f)
        else:
            with open(filepath, 'rb') as f:
                d = pickle.load(f)

        if to_one_hot_vector:
            d.is_one_hot_vector = True
            return d.to_one_hot_vector()
        else:
            return d

    def save(self, filepath: str, gzip_format=False):
        if gzip_format:
            with gzip.open(filepath, 'wb') as f_out:
                pickle.dump(self, f_out)
        else:
            with open(filepath, 'wb') as f_out:
                pickle.dump(self, f_out)


if __name__ == '__main__':
    pass