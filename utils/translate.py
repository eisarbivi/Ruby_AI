import sys
import googletrans

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

def translate_google(text, source, target):
    try:
        translator = googletrans.Translator()
        result = translator.translate(text, src=source, dest=target)
        return result.text
    except:
        print("Error translate")
        return
    
def detect_google(text):
    try:
        translator = googletrans.Translator()
        result = translator.detect(text)
        return result.lang.upper()
    except:
        print("Error detect")
        return

if __name__ == "__main__":
    text = "aku tidak menyukaimu"
    source = translate_google(text, "ID", "EN")
    print(source)