import argparse
from datasets import Dataset, DatasetDict
from PIL import Image
import albumentations as A
import os
import random
import json

# Augmentation transform
transform = A.Compose([
    A.GaussNoise(p=0.2),
    A.ElasticTransform(p=0.2),
    # Add stroke jitter, fonts if text overlay
])

def augment_image(image_path, output_dir, factor=20):
    img = Image.open(image_path)
    for i in range(factor):
        augmented = transform(image=np.array(img))['image']
        Image.fromarray(augmented).save(f"{output_dir}/{os.path.basename(image_path)}_aug{i}.jpg")

# Assume labeled.json from Label Studio
def load_labels(label_file):
    with open(label_file, 'r') as f:
        return json.load(f)  # Map to HF format

def main(args):
    # Normalize: grayscale, resize, denoise
    for img in os.listdir(args.input_dir):
        path = os.path.join(args.input_dir, img)
        img_cv = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        img_cv = cv2.resize(img_cv, (512, 512))
        img_cv = cv2.medianBlur(img_cv, 3)
        cv2.imwrite(path, img_cv)  # Overwrite or save new
        
        # Augment
        augment_image(path, args.output_dir, args.augment_factor)
    
    # Load labels, assume duplicated for augments
    labels = load_labels("data/labeled.json")
    # Chunk/convert to HF Dataset
    data = {"image": [], "label": []}  # For each
    # Populate...
    dataset = Dataset.from_dict(data)
    splits = dataset.train_test_split(test_size=0.2, seed=42)
    val_test = splits['test'].train_test_split(test_size=0.5, seed=42)
    ds_dict = DatasetDict({"train": splits['train'], "val": val_test['train'], "test": val_test['test']})
    ds_dict.save_to_disk(args.output_dir + "/handprescribe")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", default="data/raw")
    parser.add_argument("--output_dir", default="data/datasets")
    parser.add_argument("--augment_factor", type=int, default=20)
    args = parser.parse_args()
    main(args)