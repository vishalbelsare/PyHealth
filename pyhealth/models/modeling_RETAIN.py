import torch
import torch.nn as nn
import torch.nn.functional as F


class RetainLayer(nn.Module):
    """flexible layers for Retain model across different tasks"""

    def __init__(self, voc_size, emb_dim=64, device=torch.device("cpu:0")):
        super(RetainLayer, self).__init__()
        self.device = device

        self.embedding = nn.ModuleList([nn.Embedding(s + 1, emb_dim) for s in voc_size])

        self.dropout = nn.Dropout(p=0.5)
        self.alpha_gru = nn.GRU(emb_dim, emb_dim, batch_first=True)
        self.beta_gru = nn.GRU(emb_dim, emb_dim, batch_first=True)

        self.alpha_li = nn.Linear(emb_dim, 1)
        self.beta_li = nn.Linear(emb_dim, emb_dim)

    def forward(self, x, padding_mask=None):

        visit_emb_ls = []
        for idx, input in enumerate(x):
            cur_emb = self.embedding[idx](input)  # (batch, visit, code_len, dim)
            visit_emb_ls.append(torch.sum(cur_emb, dim=2))  # (batch, visit, dim)
        visit_emb = torch.stack(visit_emb_ls, dim=2).mean(2)  # (batch, visit, dim)

        g, _ = self.alpha_gru(visit_emb)  # (batch, visit, dim)
        h, _ = self.beta_gru(visit_emb)  # (batch, visit, dim)

        # to mask out the visit
        attn_g = torch.softmax(self.alpha_li(g), dim=1)  # (batch, visit, 1)
        attn_h = torch.tanh(self.beta_li(h))  # (batch, visit, emb)

        c = attn_g * attn_h * visit_emb  # (batch, visit, emb)
        c = torch.sum(c, dim=1)  # (batch, emb)

        return c


class RetainDrugRec(nn.Module):
    """Retain model for drug recommendation task"""

    def __init__(self, voc_size, tokenizers, emb_dim=64, device=torch.device("cpu:0")):
        super(RetainDrugRec, self).__init__()
        self.device = device
        self.retain = RetainLayer(voc_size, emb_dim, device)

        self.condition_tokenizer = tokenizers[0]
        self.procedure_tokenizer = tokenizers[1]
        self.drug_tokenizer = tokenizers[2]
        self.drug_fc = nn.Linear(emb_dim, self.drug_tokenizer.get_vocabulary_size())

    def forward(
        self, conditions, procedures, drugs, padding_mask=None, device=None, **kwargs
    ):
        diagT = self.condition_tokenizer.batch_tokenize(conditions).to(device)
        procT = self.procedure_tokenizer.batch_tokenize(procedures).to(device)
        x = [diagT, procT]
        embedding = self.retain(x, padding_mask)
        logits = self.drug_fc(embedding)
        y_prob = torch.sigmoid(logits)

        # target
        y = torch.zeros(diagT.shape[0], self.drug_tokenizer.get_vocabulary_size())
        for idx, sample in enumerate(drugs):
            y[idx, self.drug_tokenizer(sample[-1:])[0]] = 1

        # loss
        loss = F.binary_cross_entropy_with_logits(logits, y.to(device))
        return {"loss": loss, "y_prob": y_prob, "y_true": y}


class RETAIN(nn.Module):
    """RETAIN Class, use "task" as key to identify specific RETAIN model and route there"""

    def __init__(self, **kwargs):
        super(RETAIN, self).__init__()
        task = kwargs["task"]
        kwargs.pop("task")
        if task == "drug_recommendation":
            self.model = RetainDrugRec(**kwargs)
        else:
            raise NotImplementedError

    def forward(self, *args, **kwargs):
        return self.model(*args, **kwargs)
