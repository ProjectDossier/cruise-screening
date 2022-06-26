from os.path import exists

import faiss
import numpy as np
import torch
from cruise_literature.settings import M1_CHIP
from transformers import AutoTokenizer, AutoModel

if M1_CHIP:
    # solves problems with MKL library on M1 macbook
    # FIXME: this should be replaced by a proper requirements for M1
    import os

    os.environ["KMP_DUPLICATE_LIB_OK"] = "True"


class SemanticSearch:
    def __init__(self, data: list, tax_name: str, mount_gpu: bool = False):
        model_name = "allenai/scibert_scivocab_cased"
        self.model = AutoModel.from_pretrained(
            model_name, output_hidden_states=True
        ).eval()
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, model_max_length=16)
        self.mount_gpu = mount_gpu
        self.device = "cuda:0" if torch.cuda.is_available() and mount_gpu else "cpu"

        self.model = self.model.to(self.device)

        self.n_dimensions = self.model.pooler.dense.out_features
        self.data = data

        index_path = "../../data/processed/Taxonomy{}index.bin".format(tax_name)

        if exists(index_path):
            self.taxonomy_index = faiss.read_index(index_path)
        else:
            self.taxonomy_index = self.create_faiss_index()
            try:
                faiss.write_index(
                    faiss.index_gpu_to_cpu(self.taxonomy_index), index_path
                )
            except AttributeError:
                faiss.write_index(self.taxonomy_index, index_path)

        if mount_gpu:
            try:
                res = faiss.StandardGpuResources()
                self.taxonomy_index = faiss.index_cpu_to_gpu(res, 0, self.taxonomy_index)
            except AttributeError:
                pass

    def embedding(self, word: str):
        """
        embedds the word input as the sum of the last 4 hidden
        states of Bert embeddings
        """
        model = self.model
        tokenizer = self.tokenizer
        word = [word] if word.__class__ != list else word
        marked_text = ["[CLS] " + i + " [SEP]" for i in word]

        padding = "max_length"
        tokenized_text = [
            tokenizer.tokenize(i, padding=padding, truncation=True) for i in marked_text
        ]
        tokenized_text_ = [
            tokenizer.tokenize(i, padding=False, truncation=True) for i in marked_text
        ]
        wordpiece_vectors = [len(i) - 1 for i in tokenized_text_]

        indexed_tokens = [tokenizer.convert_tokens_to_ids(i) for i in tokenized_text]
        tokens_tensor = torch.tensor([indexed_tokens]).squeeze(0)

        with torch.no_grad():
            outputs = model(tokens_tensor.to(self.device))
            hidden_states = outputs["hidden_states"]

        # combine the layers to make a single tensor.
        token_embeddings = torch.stack(hidden_states, dim=0)
        token_embeddings = torch.squeeze(token_embeddings, dim=1)

        try:
            token_embeddings = token_embeddings.permute(1, 2, 0, 3)
        except RuntimeError:
            # RuntimeError: number of dims don't match in permute
            token_embeddings = token_embeddings.unsqueeze(0).permute(0, 2, 1, 3)

        out = []
        for item, wordpiece_vector in zip(token_embeddings, wordpiece_vectors):
            token_vecs_sum = []
            for token in item:
                sum_vec = torch.sum(token[-4:], dim=0)
                token_vecs_sum.append(sum_vec)
            out_i = torch.stack(token_vecs_sum[1:wordpiece_vector], dim=-1)
            out_i = out_i.mean(dim=-1)
            out.append(out_i)
        return torch.stack(out)

    def create_faiss_index(self):
        """
        create a faiss index of type FlatL2 from data vectors of n_dimensions
        """

        fastIndex = faiss.IndexFlatL2(self.n_dimensions)

        if self.mount_gpu:
            try:
                # copy the index to GPU
                res = faiss.StandardGpuResources()
                fastIndex = faiss.index_cpu_to_gpu(res, 0, fastIndex)
            except AttributeError:
                pass

        # index data
        embeddings = self.embedding(self.data).cpu().detach().numpy()
        fastIndex.add(np.stack(embeddings).astype("float32"))
        return fastIndex

    def do_faiss_lookup(self, text):
        """
        the semantic search of word in the indexed collection
        """
        vector = self.embedding(text).cpu().detach().numpy().astype("float32")

        score, index = self.taxonomy_index.search(vector, 1)

        return self.data[index[0][0]], score
