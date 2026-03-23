import os

class KnowledgeBase:
    ''' 
    The object folder is the path of the documents for the agent 
    documents is a list where we save the content as a text
    '''
    
    def __init__(self, folder = "knowledge/documents"):
        self.folder = folder
        self.documents = []
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

    def search (self,query):
        '''
        Creates an empty list of results then searchs the query in the list of documents
        if the query is in it, saves the content in results, then return results list
        '''
        results = []
        for doc in self.documents:
            if query.lower() in doc.lower():
                results.append(doc)
        return results