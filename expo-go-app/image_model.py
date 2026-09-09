import json
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification

# 1. Model Configuration
MODEL_NAME = "A2H0H0R1/mobilenet_v2_1.0_224-plant-disease-new"

print("Loading Hugging Face model and feature extractor...")
feature_extractor = AutoImageProcessor.from_pretrained(MODEL_NAME)
model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)
model.eval()  # Set model to evaluation mode


def analyze_crop_image(image_input, crop: str | None = None) -> str:
    """Accepts an image file path or PIL Image object from a server request,

    runs inference via MobileNetV2, and returns a JSON string response.
    """
    try:
        # Open image if passed as a file path or file-like object
        if isinstance(image_input, str):
            image = Image.open(image_input).convert("RGB")
        elif hasattr(image_input, "read"):
            image = Image.open(image_input).convert("RGB")
        elif isinstance(image_input, Image.Image):
            image = image_input.convert("RGB")
        else:
            raise ValueError("Unsupported image input format.")

        # Preprocess the image
        inputs = feature_extractor(images=image, return_tensors="pt")

        # Perform inference
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits

        # Restrict the decision to the selected crop when this model supports it.
        probabilities = torch.nn.functional.softmax(logits, dim=-1)[0]
        eligible_indices = list(range(len(probabilities)))
        if crop:
            crop_prefix = {
                "apple": "apple",
                "blueberry": "blueberry",
                "cherry": "cherry",
                "corn (maize)": "corn (maize)",
                "grape": "grape",
                "orange": "orange",
                "peach": "peach",
                "pepper, bell": "pepper, bell",
                "potato": "potato",
                "raspberry": "raspberry",
                "soybean": "soybean",
                "squash": "squash",
                "strawberry": "strawberry",
                "tomato": "tomato",
            }.get(crop.lower())
            eligible_indices = [
                idx for idx in eligible_indices
                if crop_prefix and model.config.id2label[idx].lower().startswith(crop_prefix)
            ]
        if not eligible_indices:
            return json.dumps({"status": "unsupported_crop", "crop": crop})

        eligible_probabilities = probabilities[eligible_indices]
        crop_probability_mass = eligible_probabilities.sum()
        if crop_probability_mass <= 0:
            return json.dumps({"status": "error", "message": "The model produced no usable crop probabilities."})
        crop_probabilities = eligible_probabilities / crop_probability_mass
        confidence, relative_idx = torch.max(crop_probabilities, dim=0)
        predicted_class_idx = eligible_indices[relative_idx.item()]

        # Retrieve label from model config
        predicted_label = model.config.id2label[predicted_class_idx]
        confidence_score = round(confidence.item() * 100, 2)

        # Construct structured response
        response_data = {
            "status": "success",
            "prediction": {
                "class_index": predicted_class_idx,
                "label": predicted_label,
                "confidence_percentage": confidence_score,
                "confidence_scope": f"{crop} classes" if crop else "all model classes",
            },
            "all_classes_probabilities": {
                model.config.id2label[idx]: round(crop_probabilities[position].item() * 100, 2)
                for position, idx in enumerate(eligible_indices)
            },
        }

        return json.dumps(response_data, indent=2)

    except Exception as e:
        error_response = {"status": "error", "message": str(e)}
        return json.dumps(error_response, indent=2)


# Example usage / local testing block
if __name__ == "__main__":
    # Replace with an actual test image path
    test_image = "C:/Users/piyus/Desktop/image.jpg"
    result_json = analyze_crop_image(test_image)
    print("\n--- Model Output JSON ---")
    print(result_json)
