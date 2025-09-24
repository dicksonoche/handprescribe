#!/bin/bash
# Assumes GPU; for CPU: add --cpu_only
accelerate launch --mixed_precision fp16 train/finetune_ocr.py