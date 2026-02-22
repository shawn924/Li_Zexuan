# Qwen2.5-1.5B Python Code Generator — QLoRA Fine-tuning

A Python code generation model fine-tuned from Qwen2.5-1.5B-Instruct using QLoRA, trained entirely on GPU (RTX 4060 8G).

## Highlights

- Fine-tuned a 1.5B model on an 8G consumer GPU using 4-bit quantization
- After fine-tuning, the model shifts from an "educational" style to an "engineering" style — outputting clean, directly usable code without unnecessary explanation
- Training loss decreased steadily with no overfitting

## Environment

- Framework: PyTorch + Transformers + PEFT + bitsandbytes

## Training Configuration

| Parameter | Value |
|-----------|-------|
| Base Model | Qwen/Qwen2.5-1.5B-Instruct |
| Quantization | 4-bit NF4 + double quantization |
| LoRA rank | 8 |
| LoRA alpha | 32 |
| Target modules | q/k/v/o_proj, gate/up/down_proj |
| Epochs | 1 |
| Batch size | 1 (gradient accumulation 8 steps) |
| Learning rate | 2e-4 (cosine decay) |
| Optimizer | paged_adamw_8bit |
| Training time | ~1 hour 46 minutes |

## Dataset

[iamtarun/python_code_instructions_18k_alpaca](https://huggingface.co/datasets/iamtarun/python_code_instructions_18k_alpaca)

18,612 Python code generation instructions in Alpaca format, covering data structures, algorithms, string manipulation, and other common programming tasks.

## Training Loss

| Step | Train Loss | Eval Loss |
|------|-----------|-----------|
| 500  | 0.6231    | 0.5960    |
| 1000 | 0.6074    | 0.5847    |
| 1500 | 0.5972    | 0.5802    |
| 2000 | 0.5799    | 0.5784    |

## Before vs After Fine-tuning

**Instruction**: Write a Python function to reverse a linked list

**Base Model** (educational style, verbose explanation):
```python
class ListNode:
    def __init__(self, value=0, next=None):
        self.value = value
        self.next = next

def reverse_linked_list(head):
    prev = None  # Initialize the previous node as None
    current = head  # Start with the first node

    while current is not None:
        next_node = current.next  # Store the next node temporarily
        current.next = prev       # Reverse the link
        prev = current            # Move prev one step forward
        current = next_node       # Move current one step forward

    return prev
```

**Fine-tuned Model** (engineering style, clean and direct):
```python
def reverse_linked_list(head):
    prev = None
    current = head

    while current:
        next_node = current.next
        current.next = prev
        prev = current
        current = next_node

    return prev
```

## Quick Start

Install dependencies:
```bash
pip install transformers peft bitsandbytes accelerate
```

Interactive mode:
```bash
python inference.py
```

Single instruction:
```bash
python inference.py --instruction "Write a Python function to implement binary search"
```
