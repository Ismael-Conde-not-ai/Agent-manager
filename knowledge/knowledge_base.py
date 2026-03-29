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
        opens the file for read and saves the content.
        '''
        
        for file in os.listdir(self.folder):
            path = os.path.join(self.folder,file)
            with open(path,"r") as f:
                content = f.read()
            
            chunks = self.split_into_chunks(content) #create a list of chunks from content

            for chunk in chunks: #Saves chunks in document, embbed chunk and save it in embeddings

                self.documents.append(chunk)

                embedding = geminiEmbed(chunk)

                self.embeddings.append(embedding)

    def cosine_similarity(self,a,b):

        vec_a = np.array(a)
        vec_b = np.array(b)

        return np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))
        #return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))

    def search (self, query, top_k=3):
        '''
        Gets a embedded query and create a scores list for cosine similarity
        Saves the results in scores and then sort them in descending
        saves the top k chunks and return them in a string separated by newlines
        '''
        query_embedding= geminiEmbed(query)

        scores = []

        for emb in self.embeddings:
            score = self.cosine_similarity(query_embedding,emb)
            scores.append(score)
        
        scores.sort(reverse=True)

        #Get top chunks
        top_chunks = [self.documents[idx] for _, idx in scores[:top_k]]

        #Remove duplicates
        top_chunks = self.remove_duplicates(top_chunks)

        #Limit size
        final_chunks =[]
        total_length = 0
        max_length = 800 #control context size optional

        for chunk in top_chunks:
            if total_length + len(chunk) > max_length:
                break
            final_chunks.append(chunk)
            total_length += len(chunk)

        return "\n\n".join(final_chunks)
    
    def split_into_chunks(self, text,chunk_size=200):
        '''
        Receives a text that is divided in parts by spaces using split method
        a chunks list is created, then the words are counted by 200 and joined using space.
        finally those chunks are stored in chunks list and returned
        '''
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def remove_duplicates(self,chunks):
        '''
        Creates a list of unique chunks, review a list of chunks and seves the not repeated 
        ones, then return the unique list.
        '''
        unique =[]
        for chunk in chunks:
            if chunk not in unique:
                unique.append(chunk)
        return unique

