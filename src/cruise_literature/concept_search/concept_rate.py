from typing import Tuple, List
import torch
from transformers import AutoModel, AutoTokenizer


def get_words_similarity(
    cvs: List[Tuple[str, torch.Tensor]],
    dvs: List[Tuple[str, torch.Tensor]],
):

    C = torch.stack([v[1] for v in cvs])
    C = C / C.norm(dim=-1)[:, None]

    D = torch.stack([v[1] for v in dvs])
    D = D / D.norm(dim=-1)[:, None]

    M = C @ D.T
    return M


def get_words_score(
    cts: List[str],
    dts: List[str],
    similarities: torch.Tensor,
):
    M = similarities
    assert tuple(M.shape) == (len(cts), len(dts))

    M = torch.max(M, dim=0)[0]
    norm = M.sum().item()

    res = {}
    for i, w in enumerate(dts):
        if w in cts:
            res[w] = res.get(w, 0) + (M[i].item() / norm * 100)
    return res


class ConceptRate:
    def __init__(
        self,
        model_name: str = "allenai/scibert_scivocab_cased",
        mount_on_gpu: bool = False,
    ):
        self.model = AutoModel.from_pretrained(
            model_name, output_hidden_states=True
        ).eval()
        self.device = "cuda" if mount_on_gpu and torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def get_vectors(self, strings: List[str]):
        tokens = [i.lower().split(" ") for i in strings]
        tokenized = self.tokenizer.batch_encode_plus(
            tokens,
            is_split_into_words=True,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        )
        tokenized = tokenized.to(self.device)

        with torch.no_grad():
            encodings = self.model(**tokenized)

        result = []
        for j, item in enumerate(tokens):
            item_result = []
            for i, token in enumerate(item):
                pos = tokenized[j].word_to_tokens(i)
                if pos is None:
                    continue
                start, end = tuple(pos)
                """
                the second last layer (11) of BERT was shown to be the most effective single layer on NER [1] 
                and it was shown that later layers (before the last) were the most effective word representations 
                for multiple language tasks [2] that use contextual embeddings 
                as features.
                
                [1] BERT: Pre-training of deep bidirectional transformers for language understanding
                [2] To tune or not to tune? adapting pretrained representations to diverse tasks
                """
                # vectors = encodings.last_hidden_state[0][start:end]
                vectors = encodings.hidden_states[-2][0][start:end]
                vectors = vectors.mean(dim=0)
                item_result.append((token, vectors))
            result.append(item_result)
        return result

    def concept_score(
        self, concepts: List[str], documents: List[str], lengths: List[int]
    ):

        concepts_vectors = self.get_vectors(sum(concepts, []))
        doc_vectors = self.get_vectors(documents)

        split_concepts_vectors = []
        count = 0
        for length in lengths:
            split_concepts_vectors.append(concepts_vectors[count : count + length])
            count += length

        agg_scores = []
        for concepts_vectors, doc_vector, concepts_ in zip(
            split_concepts_vectors, doc_vectors, concepts
        ):
            scores_ = {}
            for keyword_vector, concept in zip(concepts_vectors, concepts_):
                sim = get_words_similarity(keyword_vector, doc_vector)

                scores = get_words_score(
                    [e[0] for e in keyword_vector],
                    [e[0] for e in doc_vector],
                    sim,
                )
                try:
                    rate = sum([rate for _, rate in scores.items()]) / len(
                        scores.keys()
                    )
                except ZeroDivisionError:
                    rate = 0
                scores_.update({concept: rate})
            agg_scores.append(scores_)
        return agg_scores

    def request_score(self, search_result: List[object]):
        concepts = [article.keywords for article in search_result]
        documents = [article.title + ' ' + article.abstract for article in search_result]
        lengths = [len(i) for i in concepts]
        concept_scores = self.concept_score(concepts, documents, lengths)

        for article, scores in zip(search_result, concept_scores):
            article.keywords_score = scores
            article.keywords_snippet = {}
            article.keywords_rest = {}
            index_i = 0
            for k, v in sorted(scores.items(), key=lambda item: item[1], reverse=True):
                index_i += 1
                if index_i < 5:
                    article.keywords_snippet[k] = v
                else:
                    article.keywords_rest[k] = v
        return search_result
