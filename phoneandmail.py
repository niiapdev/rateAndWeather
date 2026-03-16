import pyperclip, re, math

def phonenumbandmail():
    russianPhoneRegex = re.compile(r'''(
    \b              # граница слова
    (\+?7|7|8)      # +7 или 7 или 8
    [\s\-\(\)\.]?   # разделитель ._-()
    (\d{3})         # код оператора
    [\s\-\(\)\.]?
    (\d{3})         # следующие цифры номера
    [\s\-\(\)\.]?
    (\d{2})         
    [\s\-\(\)\.]?
    (\d{2})         
    \b              # граница слова
    )''', re.VERBOSE)



    phoneRegex = re.compile(r'''(
    (\d{3})         # first number 
    [\s\-\(\)\.]?    # separator
    (\d{2})         # second number
    [\s\-\(\)\.]?     # separator
    (\d{2}))''', re.VERBOSE)


    # Создание регулярного выражения для адресов электронной почты
    emailRegex = re.compile(r'''(
    [a-zA-Z0-9._%+-]+ # username
    @                 # symbol @  
    [a-zA-Z0-9.-]+    # domain name  
    (\.[a-zA-Z]{2,}) # other domain name  
    )''', re.VERBOSE)

    # Find match in text, save into clip board
    text = str(pyperclip.paste())

    matches = []

    # find russian number phone
    temp_text = text
    for match in russianPhoneRegex.finditer(text):
        groups = match.groups()
        phoneNum = f"+7 {groups[2]} {groups[3]}-{groups[4]}-{groups[5]}"
        matches.append(phoneNum)
        start, end = match.span()
        temp_text = temp_text[:start] + "###PHONE###" + temp_text[end:]

    # find short city number: 200-92-73
    for groups in phoneRegex.findall(temp_text):
        phoneNum = '-'.join([groups[1], groups[2], groups[3]])
        matches.append(phoneNum)

    # find email address
    for groups in emailRegex.findall(text):
        matches.append(groups[0])

    matches = list(dict.fromkeys(matches))
    return {matches}
# output of the result
#if len(matches) > 0:
    #pyperclip.copy('\n'.join(matches))
    #print('Copied to clipboard')
    #print('\n'.join(matches))
#else:
    #print('Telephone and number not found')