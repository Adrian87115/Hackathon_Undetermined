import torch
import time
from torch.nn import functional as F
# import model as m
from Python import model as m

# import utils as u
from Python import utils as u
# import dataloader as dl
from Python import dataloader as dl

class ECOGPT():
    def __init__(self, batch_size, sequence_length,train_mode = True, dataset_path = None, checkpoint = None): # train_mode = False : not in training mode
                                                                                                               # train_mode = True : training mode
        super(ECOGPT, self).__init__()
        # assert torch.cuda.is_available(), "CUDA is not available"
        self.device = torch.device("cpu")
        self.checkpoint = checkpoint
        self.train_mode = train_mode
        self.batch_size = batch_size
        self.sequence_length = sequence_length
        self.current_epoch = 0
        self.config = u.loadConfig("/home/norbert/Hackathon_Undetermined/Python/config.json")
        self.max_epochs = self.config.max_epochs
        self.model = m.ScaledGPT(self.config).to(self.device)
        torch.backends.cuda.matmul.fp32_precision = 'tf32'
        torch.backends.cudnn.conv.fp32_precision = 'tf32'
        torch.manual_seed(0)
        torch.cuda.manual_seed(0)
        self.optimizer = self.configureOptimizers(weight_decay = 0.1, learning_rate = self.config.max_lr)

        if dataset_path is not None:

            if train_mode:
                self.train_loader = dl.DataLoaderPT(batch_size, sequence_length, dataset_path)
                self.eval_loader = dl.DataLoaderPT(batch_size, sequence_length, dataset_path, train = False)
            else:
                self.eval_loader = dl.DataLoaderPT(batch_size, sequence_length, dataset_path, train = False)

        if self.checkpoint:
            self.loadModel()

        

    def saveModel(self):
        model_state = {k: v for k, v in self.model.state_dict().items()}
        checkpoint = {'model_state_dict': model_state,
                      'optimizer_state_dict': self.optimizer.state_dict(),
                      'current_epoch': self.current_epoch}
        torch.save(checkpoint, f'models/eco_gpt_{self.current_epoch}.pth')
        print("Checkpoint saved.")

    def loadModel(self):
        assert self.checkpoint is not None, "No checkpoint."
        checkpoint = torch.load(self.checkpoint, map_location = self.device)
        state = {k: v for k, v in checkpoint['model_state_dict'].items()}
        self.model.load_state_dict(state)
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.current_epoch = checkpoint['current_epoch']
        print("Checkpoint loaded.")

    def configureOptimizers(self, weight_decay, learning_rate):
        param_dict = {pn: p for pn, p in self.model.named_parameters()}
        param_dict = {pn: p for pn, p in param_dict.items() if p.requires_grad}
        decay_params = [p for n, p in param_dict.items() if p.dim() >= 2]
        nodecay_params = [p for n, p in param_dict.items() if p.dim() < 2]
        optim_groups = [{'params': decay_params, 'weight_decay': weight_decay},
                        {'params': nodecay_params, 'weight_decay': 0.0}]
        optimizer = torch.optim.AdamW(optim_groups, lr = learning_rate, betas = (0.9, 0.95), eps = 1e-8, fused = True)
        return optimizer

    def train(self):
        with open("logs/evaluation_log.txt", "w") as f:
            pass

        print("Training started...")

        for epoch in range(self.current_epoch + 1, self.max_epochs + 1):
            self.current_epoch = epoch
            print(f"\n=== Epoch {epoch}/{self.max_epochs} ===\n")

            self.train_loader.current_idx = 0
            self.train_loader.epoch = epoch - 1
            self.model.train()

            total_loss = 0.0
            total_batches = 0

            while True:
                t0 = time.time()
                self.optimizer.zero_grad()

                try:
                    x, y = self.train_loader.nextBatch()
                    x, y = x.to(self.device), y.to(self.device)

                    _, loss = self.model(x, y)
                    loss.backward()

                except StopIteration:
                    break

                norm = torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.optimizer.step()
                torch.cuda.synchronize()
                total_loss += loss.item()
                total_batches += 1
                dt = (time.time() - t0) * 1000
                print(f"Batch {total_batches:4d} | Loss: {loss.item():.6f} | Norm: {norm:.4f} | Time: {dt:.2f} ms")

            avg_train_loss = total_loss / max(1, total_batches)
            print(f"\nEpoch {epoch} completed. Avg Train Loss: {avg_train_loss:.6f}")

            self.evaluate()
            self.saveModel()
            try:
                self.train_loader.current_idx = 0
                sample_x, _ = self.train_loader.nextBatch()
                sample_input = self.train_loader.enc.decode(sample_x[0].tolist()).split("<|sep|>")[0].replace("<|start|>", "").strip()
                sample_output = self.generateResponse(sample_input, max_seq_length=64)
                print(f"\n--- Sample generated output ---\nInput : {sample_input}\nOutput: {sample_output}\n-------------------------------\n")
            except Exception as e:
                print(f"Could not generate sample output: {e}")

    def evaluate(self):
        print(f"Evaluating (Epoch {self.current_epoch})...")
        self.model.eval()
        self.eval_loader.reset_eval()
        losses = []
        t0 = time.time()

        with torch.no_grad():
            try:
                while True:
                    x, y = self.eval_loader.nextBatch()
                    x, y = x.to(self.device), y.to(self.device)
                    _, loss = self.model(x, y)
                    losses.append(loss.item())

            except StopIteration:
                pass

        avg_loss = sum(losses) / len(losses)
        t1 = time.time()
        print(f"Eval Loss (Epoch {self.current_epoch}): {avg_loss:.4f} | Time: {t1 - t0:.2f}s")

        with open("logs/evaluation_log.txt", "a") as f:
            f.write(f"Epoch {self.current_epoch}: {avg_loss:.4f}\n")

    def generateResponse(self, input, max_seq_length = 64):
        self.model.eval()
        enc = u.CustomTokenizer()
        prompt = f"<|start|>{input}<|sep|>"
        print(prompt)
        input_tokens = enc.encode(prompt)
        print(input_tokens)
        tokens_tensor = torch.tensor(input_tokens, dtype=torch.long).unsqueeze(0).to(self.device)

        with torch.no_grad():
            for _ in range(max_seq_length):
                logits = self.model(tokens_tensor)

                if logits.dim() == 2:
                    logits = logits.unsqueeze(0)

                logits_last = logits[:, -1, :]
                probs = F.softmax(logits_last, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                next_token = torch.clamp(next_token, 0, self.config.vocab_size - 1)
                tokens_tensor = torch.cat((tokens_tensor, next_token), dim=1)

                decoded = enc.decode(tokens_tensor[0].tolist())
                if "<|end|>" in decoded:
                    break
        print(tokens_tensor)
        full_decoded = enc.decode(tokens_tensor[0].tolist())
        print(full_decoded)
        response = full_decoded.split("<|sep|>")[-1].split("<|end|>")[0].strip()
        return response

def convert(model):
    assert model.checkpoint is not None, "No checkpoint."
    print("===== ECO GPT =====")
    print("Provide an input text, and I will transform it for you.")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("Input: ").strip()

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        output = model.generateResponse(user_input)

        print("\n=== Generated Output ===\n")
        print(output)
        print("\n=======================\n")
