from string import letters

'''
Just some methods to normalise text.
'''

def normalise(filename):
    content = []
    with open(filename) as tf:
        content = tf.readlines()

    for line_number in range(len(content)):
        original_content = content[line_number][:-1] # All but the last char to avoid newlines
        replacement_content = []
        for word in original_content.split(" "):
            word = word.lower()
            if word=='\n':
                break

            # Strip out punctuation...
            current_word = ""
            for char in word:
                if char in letters:  # imported above
                    current_word += char
                else:
                    if len(current_word) != 0:
                        replacement_content.append(current_word)
                    replacement_content.append(char)
                    current_word = ""

            if len(current_word) != 0:
                replacement_content.append(current_word)

        if len(replacement_content) > 0:
            content[line_number] = replacement_content

    return content


if __name__ == "__main__":
    print normalise("cyberspace_manifesto.txt")
