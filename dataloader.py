class DataLoader:
    def __init__(self, dataset, batch_size=32, mode=0):
        """
        dataset: a list, numpy array, or any object supporting indexing and len()
        batch_size: number of samples per batch
        shuffle: whether to shuffle data each epoch
        drop_last: if True, drops last incomplete batch
        """
        self.dataset = dataset
        self.batch_size = batch_size
        self.mode = mode

    def __len__(self):
        return len(self.dataset) // self.batch_size


    def __iter__(self):
        import random

        indices = list(range(len(self.dataset)))
        if not self.mode:
            random.shuffle(indices)

        for start in range(0, len(indices), self.batch_size):
            end = start + self.batch_size
            batch_idx = indices[start:end]

            if len(batch_idx) < self.batch_size and self.drop_last:
                break

            batch = [self.dataset[i] for i in batch_idx]
            yield batch
