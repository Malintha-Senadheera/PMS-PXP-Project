import google.generativeai as genai
import json
import PIL.Image

class LabelExtractor:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3.1-flash-lite')
        
        # Aluth Prompt eka: Barcode ekayi Item Type ekayi add kala. Okkoma CAPS walin return karanna kiwwa.
        self.prompt = """
        Look at this courier parcel label carefully. Extract the following details and return ONLY a valid JSON object. 
        If a detail is missing, leave the string empty.
        
        CRITICAL RULES:
        1. Convert ALL text values to UPPERCASE before returning.
        2. 'item_type' must be "PSL" (Parcel) if there is any weight mentioned or it looks like a box. If it's just a letter/paper, return "DOC" (Document).
        3. 'tracking_number' is the barcode number. If you can read the barcode numbers or see a tracking ID, extract it.

        Required keys:
        {
          "sender_name": "",
          "sender_phone": "",
          "sender_address": "",
          "sender_city": "",
          "receiver_name": "",
          "receiver_phone": "",
          "receiver_address": "",
          "receiver_city": "",
          "weight": "",
          "item_type": "",
          "tracking_number": ""
        }
        """

    def extract_data(self, image_path):
        try:
            img = PIL.Image.open(image_path)
            response = self.model.generate_content([self.prompt, img])
            clean_text = response.text.replace('```json', '').replace('```', '').strip()
            
            # JSON eka load karala, safety ekata Python walinuth okkoma CAPS karanawa
            data = json.loads(clean_text)
            for key, value in data.items():
                if isinstance(value, str):
                    data[key] = value.upper()
            return data
            
        except Exception as e:
            print(f"[AI Error] Data extract karanna bari una: {e}")
            return None