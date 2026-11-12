from knowledge.document_loader import DocumentLoader


def main():
    documents = DocumentLoader().load_documents()
    print("Documents found:", len(documents))
    for document in documents:
        print("\n" + "=" * 60)
        print("File:", document["file_name"])
        print("Characters:", len(document["content"]))
        print("Content:", document["content"][:200])


if __name__ == "__main__":
    main()
