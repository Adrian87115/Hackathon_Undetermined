import json
import tiktoken
from math import cos, pi

class ConfigParser:
    def __init__(self, config_path):
        with open(config_path, "r") as f:
            config_dict = json.load(f)
        self.__dict__.update(config_dict)

def loadConfig(path):
    return ConfigParser(path)

from math import cos, pi

def getLr(epoch, config):
    if epoch < config.warmup_epochs:
        return config.max_lr * (epoch + 1) / config.warmup_epochs

    if epoch >= config.max_epochs:
        return config.min_lr

    decay_ratio = (epoch - config.warmup_epochs) / (config.max_epochs - config.warmup_epochs)
    assert 0 <= decay_ratio <= 1, "decay ratio must be between 0 and 1"
    coeff = 0.5 * (1.0 + cos(pi * decay_ratio))
    return config.min_lr + coeff * (config.max_lr - config.min_lr)


class CustomTokenizer:
    def __init__(self):
        base_enc = tiktoken.get_encoding("gpt2")
        self.enc = tiktoken.Encoding(name = "gpt2_custom",
                                     pat_str = base_enc._pat_str,
                                     mergeable_ranks = base_enc._mergeable_ranks,
                                     special_tokens = {**base_enc._special_tokens,
                                                       "<|start|>": 50257,
                                                       "<|sep|>" : 50258,
                                                       "<|end|>": 50259})
        self.allowed_special = {"<|start|>", "<|sep|>", "<|end|>"}

    def encode(self, text, add_special_tokens = True):
        return self.enc.encode(text, allowed_special = self.allowed_special)

    def encode_pair(self, input_text, target_text):
        text = f"<|start|>{input_text}<|sep|>{target_text}<|end|>"
        return self.encode(text, add_special_tokens = False)

    def decode(self, tokens):
        return self.enc.decode(tokens)

def format_article(text):
    text = str(text).strip()
    return (f"<|start|>{text}<|end|>\n")