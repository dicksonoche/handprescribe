from transformers import TrOCRProcessor, VisionEncoderDecoderModel, Seq2SeqTrainer, Seq2SeqTrainingArguments
from peft import LoraConfig, get_peft_model
from datasets import load_from_disk
import torch

dataset = load_from_disk("data/datasets/handprescribe")

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

# PEFT/LoRA
lora_config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"])
model = get_peft_model(model, lora_config)

# Preprocess function
def preprocess(examples):
    images = [processor(Image.open(img), return_tensors="pt").pixel_values[0] for img in examples['image']]
    labels = processor.tokenizer(examples['label'], padding="max_length", max_length=128).input_ids
    return {"pixel_values": images, "labels": labels}

dataset = dataset.map(preprocess, batched=True)

args = Seq2SeqTrainingArguments(
    output_dir="checkpoints",
    num_train_epochs=3,  # Reduce for CPU
    per_device_train_batch_size=4,
    learning_rate=1e-5,
    # CPU fallback: remove if no GPU
)

trainer = Seq2SeqTrainer(model=model, args=args, train_dataset=dataset['train'], eval_dataset=dataset['val'], tokenizer=processor.feature_extractor)
trainer.train()

# Save adapter
model.save_pretrained("fine_tuned_trocr")
# Merge: model.merge_and_unload()