import torch
import logging

def get_device():
    if torch.cuda.is_available():
        logging.info("CUDA is available.")
        return torch.device("cuda")
    elif torch.backends.mps.is_available() and torch.backends.mps.is_built():
        logging.info("MPS is available.")
        return torch.device("mps")
    logging.info("CUDA and MPS are not available. Using CPU.")
    return torch.device("cpu")
