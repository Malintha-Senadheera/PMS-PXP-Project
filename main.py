import os
import time
import warnings
from datetime import datetime
from dotenv import load_dotenv
from src.ai_extractor import LabelExtractor
from src.browser_bot import CourierBot

warnings.filterwarnings("ignore")
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Real System eke link eka
SYSTEM_URL = "https://pmtxps-prd-web-fdamgqb7enhqcgcj.southeastasia-01.azurewebsites.net/Invoice/ReceiverPay"

def get_unprocessed_images(folder_path="data"):
    images = []
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    for file in os.listdir(folder_path):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')) and not file.startswith('scanned_'):
            images.append(os.path.join(folder_path, file))
    return images

def main():
    if not API_KEY:
        print("❌ API Key eka .env file eke na!")
        return

    print("🚀 PromptXP Real System Auto Bot Starting...")
    ai = LabelExtractor(API_KEY)
    bot = CourierBot(SYSTEM_URL)
    
    bot.open_system()
    
    # +++ LOGIN PAUSE +++
    print("\n" + "="*60)
    print("🔒 LOOK AT THE BROWSER 🔒")
    print("1. Plz login manualy")
    print("2. Open the 'Receiver Pay Inward'")
    input("👉 If your work is done then press ENTER... ")
    # ++++++++++++++++++++++++++++++

    while True:
        unprocessed_images = get_unprocessed_images("data")
        
        if not unprocessed_images:
            print("\n📂 No Date in 'data' folder !!!")
            user_input = input("📸 Uploade Photos into folder & press ENTER (Exit to 'q'): ")
            if user_input.lower() == 'q':
                break
            continue

        for img_path in unprocessed_images:
            print("\n" + "="*60)
            original_filename = os.path.basename(img_path)
            print(f"📄 In Progress: {original_filename}")
            print("⏳ AI is reading ...")
            
            data = ai.extract_data(img_path)
            
            if data:
                # --- NEW FALLBACK LOGIC ---
                # If not found Sender details, auto fill
                if not data.get('sender_name') or data.get('sender_name').strip() == "":
                    data['sender_name'] = "NO NAME"
                if not data.get('sender_address') or data.get('sender_address').strip() == "":
                    data['sender_address'] = "RATNAPURA"
                if not data.get('sender_city') or data.get('sender_city').strip() == "":
                    data['sender_city'] = "RATNAPURA"
                    
                # If no Weight use 1kg as the default
                if not data.get('weight') or data.get('weight').strip() == "":
                    data['weight'] = "1"
                # --------------------------

                print("\n🔍 --- EXTRACTED DATA FROM IMG ---")
                print(f"Tracking No     : {data.get('tracking_number', '-')}")
                print(f"Item Type       : {data.get('item_type', '-')}")
                print(f"Sender Name     : {data.get('sender_name', '-')}")
                print(f"Sender Phone    : {data.get('sender_phone', '-')}")
                print(f"Sender Address  : {data.get('sender_address', '-')}")
                print(f"Sender City     : {data.get('sender_city', '-')}")
                print(f"Receiver Name   : {data.get('receiver_name', '-')}")
                print(f"Receiver Address: {data.get('receiver_address', '-')}")
                print(f"Receiver City   : {data.get('receiver_city', '-')}")
                print(f"Weight          : {data.get('weight', '-')}")
                print("-----------------------------")
                
                confirm = input("❓ Is this data correct? Should I fill out the Form? (y/n): ")
                
                if confirm.lower() == 'y':
                    bot.fill_form(data)
                else:
                    print("⏭️ This parcel is skiped.")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            _, ext = os.path.splitext(img_path)
            
            # Getting Tracking number, if not found tracking number print 'NO_BARCODE'
            tracking_no = data.get("tracking_number", "").upper()
            if not tracking_no:
                tracking_no = "NO_BARCODE"
                
            # New file name : scanned_trackingnumber_datetime.jpg
            new_filename = f"scanned_{tracking_no}_{timestamp}{ext}"
            new_filepath = os.path.join("data", new_filename)
            
            try:
                os.rename(img_path, new_filepath)
                print(f"✅ Photo was renamed -> {new_filename}")
            except Exception as e:
                print(f"❌ Rename error: {e}")

            next_action = input("\n➡️ Barcode scan karala 'Add' kalada? Ilaga ekata yamuda? (ENTER gahanna, Exit wenna 'q'): ")
            if next_action.lower() == 'q':
                bot.close()
                print("🛑 System eken exit wenawa...")
                return

    bot.close()

if __name__ == "__main__":
    main()