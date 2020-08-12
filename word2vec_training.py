# import modules & set up logging
import os
import gensim, logging
from gensim.models import Word2Vec

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
 
# train word2vec on the two sentences

class MySentences(object):
    def __init__(self, dirname):
        self.dirname = dirname
 
    def __iter__(self):
        for fname in os.listdir(self.dirname):
            for line in open(os.path.join(self.dirname, fname)): 
                yield line.split()
  
def train():
    global model
    sentences = MySentences('.\Articles') # a memory-friendly iterator
    model = gensim.models.Word2Vec(sentences)

def loadv():
    global model
    model = Word2Vec.load("word2vec.650K.model")

def savev():
    global model
    model.save("word2vec.650K.model")
    
def simv(w, topn=20):
    return model.wv.similar_by_word(w, topn)

print("word2vec loaded")
loadv()

