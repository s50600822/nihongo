import os
from collections import Counter
import string

ignored = {'\u0060','`','\u007e','～','!','@','\u0023','#','$','%','^','&','*','^','^','(',')','<','>','＜','＞','[',']','{','}',':','：','.','。',',','，','!','?','？','+','-','/'}

ignored = ignored.union(string.ascii_uppercase)
ignored = ignored.union(string.ascii_lowercase)

bs = {'！','','|',"'"}
ignored = ignored.union(bs)

#case like 啊啊啊啊啊啊... ~ aaaaaaaa...
noise = {'啊'}
ignored = ignored.union(noise)

vietnamese_characters = {
    'à', 'á', 'ả', 'ã', 'ạ',
    'ă', 'ằ', 'ắ', 'ẳ', 'ẵ', 'ặ',
    'â', 'ầ', 'ấ', 'ẩ', 'ẫ', 'ậ','đ','đ'
    'è', 'é', 'ẻ', 'ẽ', 'ẹ',
    'ê', 'ề', 'ế', 'ể', 'ễ', 'ệ',
    'ì', 'í', 'ỉ', 'ĩ', 'ị',
    'ò', 'ó', 'ỏ', 'õ', 'ọ',
    'ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ',
    'ơ', 'ờ', 'ớ', 'ở', 'ỡ', 'ợ',
    'ù', 'ú', 'ủ', 'ũ', 'ụ',
    'ư', 'ừ', 'ứ', 'ử', 'ữ', 'ự',
    'ỳ', 'ý', 'ỷ', 'ỹ', 'ỵ',
}
ignored = ignored.union(vietnamese_characters)

pinyin_characters = {
    'ā', 'á', 'ǎ', 'à', 'a',
    'ē', 'é', 'ě', 'è', 'e',
    'ī', 'í', 'ǐ', 'ì', 'i',
    'ō', 'ó', 'ǒ', 'ò', 'o',
    'ū', 'ú', 'ǔ', 'ù', 'u',
    'ǖ', 'ǘ', 'ǚ', 'ǜ', 'ü',
}
ignored = ignored.union(pinyin_characters)
ignored = ignored.union({'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'})

in_file_ext = ".md" # better browsing on github

def process_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read().replace('\n', '')
    return text



def process_directory(directory_path):
    all_text = ""
    for file_name in os.listdir(directory_path):
        if file_name.endswith(in_file_ext):
            file_path = os.path.join(directory_path, file_name)
            all_text += process_text_file(file_path)
    return all_text

def process_directories(directory_paths):
    all_text = ""
    for dir_path in directory_paths:
        all_text += process_directory(dir_path)
    return all_text

def print_character_frequencies(text):
    # Remove spaces
    cleaned_text = ''.join(text.split())
    # Count character frequencies
    character_frequencies = Counter(cleaned_text)
    generate_md(character_frequencies.most_common())
    # Print characters ordered by frequencies in descending order
    for char, freq in character_frequencies.most_common():
        if char not in ignored:
            print(f"{char}: {freq}")

def generate_md(character_frequencies):
    table = "| Rank | Character | Frequency |\n|-----------|-----------|-----------|\n"
    total_count = 0

    for char, freq in character_frequencies:
        if char not in ignored:
            total_count += 1
            table += f"| {total_count} | {char} | {freq} |\n"

    # Add total row at the top
    table = f" {total_count}: characters \n" + table

    with open("Readme.md", 'w', encoding='utf-8') as readme_file:
        readme_file.write(table)



all_text = process_directories({'./lyrics','./poems'})

print_character_frequencies(all_text)