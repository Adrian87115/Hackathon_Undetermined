import torch
import json
import random
import utils as u

class DataLoaderPT:
    def __init__(self, batch_size, sequence_length, database_path, train = True):
        self.batch_size = batch_size
        self.sequence_length = sequence_length
        self.database_path = database_path
        self.train = train
        self.enc = u.CustomTokenizer()

        with open(self.database_path, 'r', encoding = 'utf-8') as f:
            self.all_entries = json.load(f)
            rnd = random.Random(42) # do not change the seed, unless you train from scratch
            rnd.shuffle(self.all_entries)

        print(f"Found {len(self.all_entries)} total entries.")
        split_idx = int(0.90 * len(self.all_entries))

        if self.train:
            self.entries = self.all_entries[:split_idx]
            random.shuffle(self.entries)
        else:
            self.entries = self.all_entries[split_idx:]
            rnd = random.Random(42)
            rnd.shuffle(self.entries)

        print(f"Using {len(self.entries)} entries for {'train' if self.train else 'eval'}.")
        self.current_idx = 0
        self.epoch = 0

    def _get_token_pairs(self, entry):
        x_tokens = self.enc.encode(entry['original'])
        y_tokens = self.enc.encode(entry['transformed'])
        return torch.tensor(x_tokens, dtype = torch.long), torch.tensor(y_tokens, dtype = torch.long)

    def nextBatch(self):
        batch_x, batch_y = [], []

        for _ in range(self.batch_size):
            if self.current_idx >= len(self.entries):
                raise StopIteration

            entry = self.entries[self.current_idx]
            x_tokens = self.enc.encode(entry['original'])
            y_tokens = self.enc.encode(entry['transformed'])

            max_len = max(len(x_tokens), len(y_tokens), self.sequence_length)
            x_tokens = x_tokens[:max_len]
            y_tokens = y_tokens[:max_len]

            pad_len_x = max_len - len(x_tokens)
            pad_len_y = max_len - len(y_tokens)

            x_tokens = x_tokens + [0] * pad_len_x
            y_tokens = y_tokens + [0] * pad_len_y

            batch_x.append(torch.tensor(x_tokens, dtype = torch.long))
            batch_y.append(torch.tensor(y_tokens, dtype = torch.long))

            self.current_idx += 1

        return torch.stack(batch_x), torch.stack(batch_y)


    def reset_eval(self):
        self.current_idx = 0