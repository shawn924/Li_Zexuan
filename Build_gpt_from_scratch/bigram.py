import requests
import torch
import torch.nn as nn
from torch.nn import functional as F

#Hyperparameters
torch.manual_seed(1337)
batch_size = 32 # how many independent sequences will we process in parallel?
block_size = 8 # what is the max context length for prediction?
max_iters = 3000
eval_interval = 300 #how long u check the loss
learning_rate = 1e-3
device = 'cuda' if torch.cuda.is_available() else 'cpu'
eval_iters = 200 #how much you check each time
url = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"

#-------

torch.manual_seed(1337)

r = requests.get(url)
text = r.text

# 1.write in file
with open("input.txt", "w", encoding="utf-8") as f:
    f.write(r.text)

# 2.tokenization
# here are all the unique characters that occur in this text
chars = sorted(list(set(text)))
vocab_size = len(chars)
#create mapping
stoi = { ch:i for i,ch in enumerate(chars)} #为每个字符创建一个映射 a:0 , b:1
itos = { i:ch for i,ch in enumerate(chars)} #与stoi相反
encode = lambda s: [ stoi[c] for c in s] # 例子：s = "hi!" 遍历字符：'h' → 'i' → '!' 查找索引：stoi['h'] → 7, stoi['i'] → 8, stoi['!'] → 27 结果：[7, 8, 27]
decode = lambda l: ''.join([itos[i] for i in l])

# 3.split data
data = torch.tensor(encode(text), dtype=torch.long)

n = int(0.9*len(data))
train_data = data[:n]
val_data = data[n:]

# 4.data loading
def get_batch(split):
    # generate a small batch of data of inputs x and targets y
    data = train_data if split == "train" else val_data
    ix = torch.randint(len(data) - block_size, (batch_size,)) #找4个点起始，len(data)-blocksize保证取到完整的片段
    x = torch.stack([data[i:i+block_size] for i in ix])
    y = torch.stack([data[i+1:i+block_size+1] for i in ix]) #model应该预测的东西，预测与y比较
    x,y = x.to(device), y.to(device)
    return x,y

@torch.no_grad() #告诉pytorch不需要训练，不用记grad, 接下来的estimate loss在做tensor运算
def estimate_loss():
    out = {}
    model.eval() #bigram中不重要，但是在dropout训练中，会看不到真实performance
    for split in ["train","val"]:
        losses = torch.zeros(eval_iters) #创建一个全是0的tensor
        for k in range(eval_iters):
            X,Y = get_batch(split)
            logits,loss = model(X,Y)
            losses[k] = loss.item()
        out[split] = losses.mean()
    model.train()
    return out


# 5. create bigram model
class BigramLanguageModel(nn.Module):

    def __init__(self, vocab_size):
        super().__init__()
        # each token directly reads off the logits for the next token from a lookup table
        self.token_embedding_table = nn.Embedding(vocab_size, vocab_size) #(多少个不同的词/每个词用多少维的向量表示)


    def forward(self, idx, targets = None):
        # idx and targets are both (B,T) tensor of integers
        logits = self.token_embedding_table(idx) #BTC

        if targets is None:
            loss = None
        else:
            B,T,C = logits.shape
            logits = logits.view(B*T,C)
            targets = targets.view(B*T)
            loss = F.cross_entropy(logits,targets)
        
        return logits, loss
    
    def generate(self, idx, max_new_tokens):
        for _ in range(max_new_tokens):
            #get predictions
            logits, loss = self(idx)
            # focus only on the last time step
            logits = logits[:,-1,:] #becomes(B,C)
            # apply softmax to get probabilities
            probs = F.softmax(logits,dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            #append sampled index to the running sequence
            idx = torch.cat((idx,idx_next),dim=1)
        return idx
    
model = BigramLanguageModel(vocab_size)
m = model.to(device)

#create a optimizer
optimizer = torch.optim.AdamW(model.parameters(), lr = learning_rate)

for iter in range(max_iters):
    # every once in a while evaluate the loss on train and val sets
    if iter % eval_interval == 0 :
        losses = estimate_loss()
        print(f"step {iter}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f}")
    
    #sample a batch of data
    xb,yb = get_batch("train")

    #evaluate loss
    logits,loss = model(xb,yb)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()

#generate from the model
context = torch.zeros((1,1),dtype = torch.long, device = device)
print(decode(m.generate(context, max_new_tokens=500)[0].tolist()))

