from google.genai.types import Part

def analyze_attachment(imgs, email, mime_types, client):
    prompt = f"""
        Dựa trên hình ảnh được cung cấp và email được cung cấp hãy đưa ra thông tin của từng bức ảnh một và liên hệ của nó với nội dung email bằng một đoạn văn không quá 20 từ.

        Email:'{email}'
    """
    images = [Part.from_bytes(data=data, mime_type=mime_type) for data,mime_type in zip(imgs,mime_types)]
    # Email: "{email}"
    emails = [Part.from_text(text=prompt)]
    parts = [*images, *emails]
    response = client.models.generate_content(
        model='gemini-2.5-flash',

        contents=parts,

        config={
            "temperature":0.5,
            "max_output_tokens":2548,
        }
    )


    # print("IMAGE")
    # print(response)
    # print(Part.from_bytes(data=img,mime_type='image/jpeg'))
    # print(Part.from_bytes(data=img,mime_type=mime_type))
    return response.text