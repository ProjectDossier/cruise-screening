from dataclasses import dataclass
from typing import Any, Self

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig, PreTrainedTokenizerFast


@dataclass(slots=True)
class ModelConfig:
    device: torch.device
    tokenizer: PreTrainedTokenizerFast
    model: AutoModelForCausalLM
    gen_config: GenerationConfig

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> Self:
        if not torch.cuda.is_available():
            raise ValueError('Cuda platform is not available!')

        model_path = config["MODEL_PATH"]

        return cls(device=torch.device("cuda"),
                   tokenizer=AutoTokenizer.from_pretrained(model_path),
                   model=AutoModelForCausalLM.from_pretrained(model_path),
                   gen_config=GenerationConfig.from_pretrained(model_path))