import weaviate


def load_weaviate_client():
    return weaviate.connect_to_local(port=8081)