from os.path import basename
from sys import argv
from os import walk
from pathlib import Path

from pprint import pprint
from pyquery import PyQuery as pq
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfVectorizer


# cluster tabs things by cos distance of
# innertext >| term vectors >| tfidf

def samples_from_dir(in_dir):
    """Return an iterable of Paths to samples found in ``in_dir``,
    recursively."""
    for dir_path, dirs, files in walk(in_dir):
        try:
            # Skip resources/ folders. Sometimes they contain .html files, and
            # those aren't samples.
            dirs.remove('resources')
        except ValueError:
            pass
        yield from (Path(dir_path) / file for file in files
                    if file.endswith('.html'))

def tab_clusters(folder):
    paths_and_docs = [(basename(path), text_from_sample(path)) for path in samples_from_dir(folder)]
    paths, docs = zip(*paths_and_docs)
    vectorizer = TfidfVectorizer(max_df=.6)  # Decrease max_df to be more aggressive about declaring things stopwords.
    tfidfs = vectorizer.fit_transform(docs)
    print(f'Stopwords: {vectorizer.stop_words_}')
    clustering = AgglomerativeClustering(n_clusters=None, linkage='ward', compute_full_tree=True, distance_threshold=1.45)
    clustering.fit(tfidfs.toarray())
    print(f'Found {clustering.n_clusters_} clusters:')
    clusters = [[] for _ in range(clustering.n_clusters_)]
    for path_index, label in enumerate(clustering.labels_):
        clusters[label].append(paths[path_index])
    pprint(clusters)


def text_from_sample(filename):
    """Return the innerText (or thereabouts) from an HTML file."""
    with open(filename, encoding='utf-8') as file:
        return pq(file.read()).remove('script').remove('style').text()


if __name__ == '__main__':
    tab_clusters(argv[1])


# NEXT: HTML signal, throw the URL or domain in as signal. Measure that first cluster, which seems to be pretty misc, so wee if it has high spread/variance or something that I can ignore it based on.