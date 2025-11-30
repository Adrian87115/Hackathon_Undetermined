import torch
import json
import random
# import utils as u
from Python import utils as u

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

    def nextBatch(self):
        batch_x, batch_y = [], []

        for _ in range(self.batch_size):
            if self.current_idx >= len(self.entries):

                if not batch_x:
                    raise StopIteration
                else:
                    break

            entry = self.entries[self.current_idx]
            tokens = self.enc.encode_pair(entry['original'], entry['transformed'])

            if len(tokens) < self.sequence_length + 1:
                tokens = tokens + [0] * (self.sequence_length + 1 - len(tokens))

            x_tokens, y_tokens = tokens[:-1], tokens[1:]
            batch_x.append(torch.tensor(x_tokens, dtype=torch.long))
            batch_y.append(torch.tensor(y_tokens, dtype=torch.long))
            self.current_idx += 1

        if not batch_x:
            raise StopIteration

        return torch.stack(batch_x), torch.stack(batch_y)

    def reset_eval(self):
        self.current_idx = 0