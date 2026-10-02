class DocumentSync:
    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base

    def sync(self):

        documents = (
            self.knowledge_base.document_loader.load_documents()
        )
        current_sources = {
            document["file_name"] for document in documents
        }

        indexed_sources = (
            self.knowledge_base.vector_store.get_sources()
        )

        added = []
        updated = []
        deleted = []

        #NEW AND MODIFIED DOCUMENTS
        for document in documents:
            source = document["file_name"]

            new_hash = document["metadata"]["file_hash"]
            old_hash = self.knowledge_base.vector_store.get_document_hash(source)

            if source not in indexed_sources:
                self.knowledge_base.index_document(document)
                added.append(source)
            elif new_hash != old_hash:
                self.knowledge_base.delete_document(source)
                self.knowledge_base.index_document(document)
                updated.append(source)

        #DELETED DOCUMENTS
        deleted_sources = indexed_sources - current_sources
        for source in deleted_sources:
            self.knowledge_base.delete_document(source)
            deleted.append(source)

        return {
            "added": added,
            "updated": updated,
            "deleted": deleted
        }