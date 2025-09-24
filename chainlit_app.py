import chainlit as cl
from src.ocr import ocr_tesseract, ocr_trocr
from src.parsing import parse_rule_based, parse_llm_assisted, PrescriptionSchema
from pydantic import ValidationError
import os

@cl.on_message
async def main(message: cl.Message):
    # Handle image upload
    files = message.elements
    if files and files[0].mime.startswith("image/"):
        image_path = files[0].path
        await cl.Message(content="Processing image...").send()
        
        # Preview image
        await cl.Image(path=image_path, name="Uploaded Prescription", display="inline").send()
        
        # Run OCR (default TrOCR if model loaded, else Tesseract)
        try:
            raw_text = ocr_trocr(image_path)  # Assumes model loaded; fallback to tesseract
        except:
            raw_text = ocr_tesseract(image_path)
        await cl.Message(content=f"Raw OCR Text: {raw_text}").send()
        
        # Parse
        try:
            structured = parse_llm_assisted(raw_text)  # Fallback to rule_based if no LLM
        except:
            structured = parse_rule_based(raw_text)
        
        # Validate
        try:
            validated = PrescriptionSchema(**structured)
            json_out = validated.model_dump_json(indent=2)
        except ValidationError as e:
            json_out = f"Validation error: {e}"
        
        # Stream response
        msg = cl.Message(content="")
        for chunk in json_out.split("\n"):  # Chunked streaming
            await msg.stream_token(chunk + "\n")
        await msg.send()
        
        # Consent & deletion note
        await cl.Message(content="Consent: By uploading, you agree to local processing only. Delete: POST /delete/{job_id}").send()
        
        # Human-in-loop: Allow correction
        cl.user_session.set("last_output", structured)
        await cl.Message(content="Correct fields? Reply with JSON updates.").send()

@cl.on_chat_start
async def start():
    await cl.Message(content="Upload a prescription image for interpretation. Prototype: Human review required.").send()

# Run: chainlit run chainlit_app.py