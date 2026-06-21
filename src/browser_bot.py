from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class CourierBot:
    def __init__(self, url):
        self.url = url
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)

    def open_system(self):
        self.driver.get(self.url)
        print("🌐 Browser eka open kala.")
        print("⚠️ Meka real system eka nisa, oya manual login wela 'Receiver Pay Inward' page ekata yanna.")

    def fill_form(self, data):
        try:
            # 1. Item Type AI eken gaththa eka (DOC or PSL) select kirima
            item_type = data.get("item_type", "PSL").upper()
            if item_type not in ["DOC", "PSL"]:
                item_type = "PSL" # Fallback eka Parcel
            
            # Select2 plugin nisa JS eken set karanawa
            self.driver.execute_script(f"document.getElementById('itemtype').value = '{item_type}'; $('#itemtype').trigger('change');")
            time.sleep(0.5)

            # 2. Sender Details (ALL CAPS)
            # self.wait.until(EC.presence_of_element_located((By.ID, "sendermobile"))).send_keys(data.get("sender_phone", ""))
            self.driver.find_element(By.ID, "sendername").send_keys(data.get("sender_name", "").upper())
            self.driver.find_element(By.ID, "senderaddress").send_keys(data.get("sender_address", "").upper())
            
            # Sender City (Title Case / Mul akura witharak capital)
            sender_city = data.get("sender_city", "").title()
            if sender_city:
                s_city_input = self.driver.find_element(By.ID, "sendercity_input")
                s_city_input.send_keys(sender_city)
                time.sleep(1.5)
                s_city_input.send_keys(Keys.ENTER)
                time.sleep(0.2)

            # 3. Receiver Details (ALL CAPS)
            # self.driver.find_element(By.ID, "consigneemobile").send_keys(data.get("receiver_phone", ""))
            self.driver.find_element(By.ID, "consigneename").send_keys(data.get("receiver_name", "").upper())
            self.driver.find_element(By.ID, "consigneeaddress1").send_keys(data.get("receiver_address", "").upper())
            
            # Receiver City (Title Case) mariyu Next Branch extraction
            receiver_city = data.get("receiver_city", "").title()
            next_branch_value = "0001" # Default Head Office
            
            if receiver_city:
                r_city_input = self.driver.find_element(By.ID, "consigneecity_input")
                r_city_input.send_keys(receiver_city)
                
                try:
                    # Autocomplete list eka enakan inna
                    self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#consigneecity_list .ac-item")))
                    time.sleep(0.5)
                    
                    # Palaweni item eken district nama ganna
                    first_item = self.driver.find_element(By.CSS_SELECTOR, "#consigneecity_list .ac-item")
                    district_name = first_item.get_attribute("data-dist")
                    
                    if district_name:
                        print(f"📍 District/Branch hoyagaththa: {district_name}")
                        
                        # NextHub dropdown eke district eka thiyenawada balamu
                        next_hub_select = self.driver.find_element(By.ID, "NextHub")
                        options = next_hub_select.find_elements(By.TAG_NAME, "option")
                        
                        for option in options:
                            if option.text.strip().upper() == district_name.upper():
                                next_branch_value = option.get_attribute("value")
                                print(f"✅ Matching branch dakkai! Code: {next_branch_value}")
                                break
                        else:
                            print("⚠️ Branch list eke na, Head Office (0001) select karanawa.")
                                
                except Exception as e:
                    print(f"⚠️ Autocomplete eken branch eka ganna bari una: {e}")
                    
                # Chivariki Enter press karala city eka select kirima
                r_city_input.send_keys(Keys.ENTER)
                time.sleep(0.2)

            # 4. Weight (Characters ain karala numbers witharak ganna)
            if item_type == "PSL":
                weight_val = data.get("weight", "").upper().replace("KG", "").strip()
                if weight_val:
                    weight_field = self.driver.find_element(By.ID, "weight")
                    weight_field.clear()
                    weight_field.send_keys(weight_val)
                    time.sleep(0.2)
            
            # 5. Next Branch Select kirima (Dynamic hari Head Office hari)
            self.driver.execute_script(f"document.getElementById('NextHub').value = '{next_branch_value}'; $('#NextHub').trigger('change');")
            time.sleep(0.2)

            # 6. Area Default 'OUT STATION' (Value: OS)
            self.driver.execute_script("document.getElementById('area').value = 'OS'; $('#area').trigger('change');")
            time.sleep(0.2)

            # 7. Barcode Type Kirima
            barcode_val = data.get("tracking_number", "").upper()
            barcode_input = self.driver.find_element(By.ID, "trackingnumber")
            
            if barcode_val:
                barcode_input.send_keys(barcode_val)
                print(f"✅ Data saha Barcode ({barcode_val}) form ekata damma. Please check and ADD!")
            else:
                barcode_input.click()
                print("✅ Data form ekata damma. Barcode eka read une na. Scanner eken scan karanna!")
            
        except Exception as e:
            print(f"❌ Form fill error: {e}")

    def close(self):
        self.driver.quit()