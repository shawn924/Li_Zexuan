import argparse
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
LORA_PATH = "./qwen-code-lora-final"

def load_model():
    print("加载模型...")
    tokenizer = AutoTokenizer.from_pretrained(LORA_PATH)
    base = AutoModelForCausalLM.from_pretrained(BASE_MODEL, dtype=torch.float16, device_map="auto")
    model = PeftModel.from_pretrained(base, LORA_PATH, device_map={"": 0})
    model.eval()
    print("✅ 加载完成\n")
    return model, tokenizer

@torch.inference_mode()
def generate(model, tokenizer, instruction, max_new_tokens=512):
    messages = [{"role": "user", "content": instruction}]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        pad_token_id=tokenizer.eos_token_id,
    )
    return tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instruction", type=str, default=None)
    args = parser.parse_args()

    model, tokenizer = load_model()

    if args.instruction:
        print(generate(model, tokenizer, args.instruction))
    else:
        print("交互模式（输入 quit 退出）\n")
        while True:
            instruction = input(">>> ").strip()
            if instruction.lower() in ("quit", "exit", "q"):
                break
            print(generate(model, tokenizer, instruction))
            print()

if __name__ == "__main__":
    main()