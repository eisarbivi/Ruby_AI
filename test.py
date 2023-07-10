import re

chat = "hey rubi, how are you?"

# Mengecek apakah teks chat mengandung kata-kata yang diinginkan
if re.search(r"(hey|Hi|Hello)\s+(Ruby|rubi)", chat):
    print("Program dapat dilanjutkan!")
    # Lanjutkan dengan bagian program selanjutnya
else:
    print("Teks dalam variabel chat tidak memenuhi syarat.")
    # Tidak melanjutkan program karena teks tidak memenuhi syarat
