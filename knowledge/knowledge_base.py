#from http import client
import os
import numpy as np
from api.apiClient import geminiEmbed


class KnowledgeBase:
    ''' 
    The object folder is the path of the documents for the agent 
    documents is a list where we save the content as a text
    '''
    
    def __init__(self, folder = "knowledge/documents"):
        self.folder = folder
        self.documents = []
        self.embeddings = []
        self.load_documents()

    def load_documents(self):
        '''
        Opens the file using for for the list of directories in folder
        saves the path using the folder and file name
        opens the file for read and saves the content in documents list
        '''
        
        for file in os.listdir(self.folder):
            path = os.path.join(self.folder,file)
            with open(path,"r") as f:
                content = f.read()
            self.documents.append(content)

            embedding = geminiEmbed(content)

            self.embeddings.append(embedding)

    def cosine_similarity(self,a,b):

        vec_a = np.array(a)
        vec_b = np.array(b)

        return np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))
        #return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))

    def search (self,query):
        '''
        Creates an empty list of results then searchs the query in the list of documents
        if the query is in it, saves the content in results, then return results list
        '''
        query_embedding= geminiEmbed(query)

        similarities = []

        for emb in self.embeddings:
            score = self.cosine_similarity(query_embedding,emb)
            similarities.append(score)

        best_index = similarities.index(max(similarities))

        return self.documents[best_index]


    '''
        results = []
        for doc in self.documents:
            if query.lower() in doc.lower():
                results.append(doc)
        return
    '''