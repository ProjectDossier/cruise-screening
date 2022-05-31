from typing import Tuple, List
import torch
from transformers import AutoModel, AutoTokenizer


def get_words_similarity(
        cvs: List[Tuple[str, torch.Tensor]],
        dvs: List[Tuple[str, torch.Tensor]],
):
    # cvs: concept vectors (shape: [N, H], N=#tokens in C)
    # dvs: document vectors (shape: [M, H], M=#tokens in D)
    C = torch.stack([v[1] for v in cvs])
    C = C / C.norm(dim=-1)[:, None]

    D = torch.stack([v[1] for v in dvs])
    D = D / D.norm(dim=-1)[:, None]

    M = C @ D.T
    return M


def get_words_score(
        qts: List[str],
        dts: List[str],
        similarities: torch.Tensor,
):
    M = similarities
    assert tuple(M.shape) == (len(qts), len(dts))

    M = torch.max(M, dim=0)[0]
    norm = M.sum().item()

    res = {}
    for i, w in enumerate(dts):
        if w in qts:
            res[w] = res.get(w, 0) + (M[i].item() / norm)

    return res


class ConceptRate:
    def __init__(self, model_name: str, mount_on_gpu: bool = True):
        self.model = AutoModel.from_pretrained(model_name, output_hidden_states=True).eval()
        self.device = 'cuda' if mount_on_gpu and torch.cuda.is_available() else 'cpu'
        self.model.to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def get_vectors(self, string: list[str]):
        tokens = [i.lower().split(' ') for i in string]
        tokenized = self.tokenizer.batch_encode_plus(tokens, is_split_into_words=True, return_tensors='pt', padding=True)
        tokenized = tokenized.to(self.device)

        with torch.no_grad():
            encodings = self.model(**tokenized)

        result = []
        for j, item in enumerate(tokens):
            item_result = []
            for i, token in enumerate(item):
                start, end = tuple(tokenized[j].word_to_tokens(i))
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
                item_result.append((token, vectors))
            result.append(item_result)
        return result

    def concept_score(self,
                      concepts: list[str],
                      documents: list[str],
                      lengths: list[int]
                      ):
        concepts_vectors = self.get_vectors(concepts)
        doc_vectors = self.get_vectors(documents)

        split_concepts_vectors = []
        count = 0
        for length in lengths:
            split_concepts_vectors.append(concepts_vectors[count:count+length])
            count += length

        agg_scores = []
        for concepts_vectors, doc_vector in zip(split_concepts_vectors, doc_vectors):
            scores_ = []
            for keyword_vector in concepts_vectors:
                sim = get_words_similarity(keyword_vector, doc_vector)

                scores = get_words_score(
                    [e[0] for e in keyword_vector],
                    [e[0] for e in doc_vector],
                    sim,
                )
                scores_.append(scores)
            agg_scores.append(scores_)
        return agg_scores


if __name__ == '__main__':
    model_name = "allenai/scibert_scivocab_cased"
    rate = ConceptRate(model_name)
    kw1 = ["xml", "extensible markup languages"]
    kw2 = ["mOLAP", "subsumption", "broadcast"]
    doc1 = "The eXtensible Markup Language XML is not only a language for " \
           "communication between humans and the web, it is also a language for " \
           "communication between programs. Rather than passing parameters, programs " \
           "can pass documents from one to another, containing not only pure data, but " \
           "control information as well. Even legacy programs written in ancient languages " \
           "such as COBOL and PL/I can be adapted by means ofinterface reengineering to process " \
           "and to generate XML documents."
    doc2 = "Mobile online analytical processing (mOLAP) encompasses all necessary technologies f" \
           "or information systems that enable OLAP data access to users carrying a mobile device. " \
           "This paper presents FCLOS, a complete client–server architecture explicitly designed for " \
           "mOLAP. FCLOS founds on intelligent scheduling and compressed transmissions in order to " \
           "become a query efficient, self-adaptive and scalable mOLAP information system. Scheduling " \
           "exploits derivability between data cubes in order to group related queries and eventually reduce " \
           "the necessary transmissions (broadcasts). Compression is achieved by the m-Dwarf, a novel, compressed " \
           "data cube physical structure, which has no loss of semantic information and is explicitly designed for " \
           "mobile applications. The superiority of FCLOS against state of the art systems is shown both experimentally" \
           " and analytically."

    scores = rate.concept_score(kw1 + kw2, [doc1, doc2], lengths=[len(kw1), len(kw2)])
    print()