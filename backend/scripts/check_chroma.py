from storage.vector.vector_store import VectorStore

store = VectorStore.get_instance()

print("Vector count:", store.count())