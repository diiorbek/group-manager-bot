from better_profanity import profanity

profanity.load_censor_words()  # Standart so'kinish so'zlari bazasini yuklaydi

matn = "."
if profanity.contains_profanity(matn):
    print("Matnda so'kinish bor!")
else:
    print("Matn toza.")