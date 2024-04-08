
# # Installing Dependencies 
def web_scraping(your_directory):
    import nltk

    nltk.download('cmudict')
    nltk.download('wordnet')

    import warnings
    warnings.filterwarnings("ignore")
    from bs4 import BeautifulSoup
    import requests
    import pandas as pd
    import os
    import re
    import itertools
    from itertools import chain

    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.tokenize import word_tokenize
    from nltk.corpus import wordnet
    import cmudict

    df1 = pd.read_excel('Input.xlsx')


    # Extracting Data 

    directory_name = 'extracted'
    directory_path = os.path.join(your_directory, directory_name)
    os.makedirs(directory_path)
    print(f"Directory '{directory_name}' created successfully!")

    def extract_info(URL_ID,URL):
        website=requests.get(URL).text
        soup=BeautifulSoup(website,'lxml')
        title=soup.find('h1',class_=["entry-title","tdb-title-text"]).text
        first_class = soup.find_all("div", class_="td-post-content tagdiv-type")
        second_class = soup.find_all("div", class_="tdb-block-inner td-fix-index")
        with open(f'extracted/{URL_ID}.txt','w',encoding='UTF-8') as f:
            f.write(title)
            if first_class:
                for div in first_class:
                    f.write(div.text.strip())
            else:
                for div in second_class:
                    f.write(div.text.strip())

    for website in df1.itertuples():
        try:
            extract_info(website.URL_ID,website.URL)
        except AttributeError:
            pass
            

    # # Cleaning Using StopWords 
    sub_dir='StopWords'
    sw_directory=os.path.join(your_directory, sub_dir)
    stop_words=[]
    for file in os.listdir(sw_directory):
        if file.endswith(".txt"):
            file_path = os.path.join(sw_directory, file)
            with open(file_path, "r") as file:
                text = file.readlines()
                for i in range(len(text)):
                    stop_words.append(text[i].lower().strip('\n').replace('|','').split(','))

    flattened_sw = list(chain.from_iterable(stop_words))


    def filter_text(path):
        with open(path,'r',encoding='UTF-8') as f:
            text=f.read()
            words = word_tokenize(text)
            filtered_words = [word for word in words if word.lower() not in flattened_sw]
            updated_text = " ".join(filtered_words)
            with open(path,'w',encoding='UTF-8') as f:
                f.write(updated_text)
    ext_dir='extracted'    
    filter_dir=os.path.join(your_directory,ext_dir)
    for file in os.listdir(filter_dir):
        if file.endswith(".txt"):
            file_path = os.path.join(filter_dir, file)
            filter_text(file_path)


    # # Master Dictionary 

    master_dir=os.path.join(your_directory,'MasterDictionary')
    pw_dir= os.path.join(master_dir,'positive-words.txt')
    nw_dir=os.path.join(master_dir,'negative-words.txt')
    pos_words=[]
    neg_words=[]
    with open(pw_dir,'r') as f:
        text=f.readlines()
        for i in range(len(text)):
            pos_words.append(text[i].lower().strip('\n').split(','))
    positive_words = list(chain.from_iterable(pos_words))

    neg_words=[]
    with open(nw_dir,'r') as f:
        text=f.readlines()
        for i in range(len(text)):
            neg_words.append(text[i].lower().strip('\n').split(','))
    negative_words = list(chain.from_iterable(neg_words))

    unique_pos=[]
    for word in positive_words:
        if word not in flattened_sw:
            unique_pos.append(word)

    unique_negative=[]
    for word in negative_words:
        if word not in flattened_sw:
            unique_negative.append(word)

    pos_dict = {key: 'positive' for key in unique_pos}
    neg_dict = {key: 'negative' for key in unique_negative}



    # # Extracting Derived Variables 

    df=pd.read_excel('input.xlsx')
    df=df.drop(35)
    df=df.drop(47)
    positive_s=[]
    negative_s=[]
    polarity_s=[]
    subjectivity_s=[]
    def extract_variables(path):
        with open(path,'r',encoding='UTF-8') as f:
            positive_score=0
            negative_score=0
            text=f.read()
            words = nltk.word_tokenize(text)
            for word in words:
                if pos_dict.get(word.lower(), '') == 'positive':
                    positive_score += 1
                elif neg_dict.get(word.lower(),'') == 'negative':
                    negative_score+=1
            polarity_score = (positive_score - negative_score)/((positive_score + negative_score)+0.000001)
            subjectivity_score = (positive_score + negative_score) / ((len(words))+0.000001)
            positive_s.append(positive_score)
            negative_s.append(negative_score)
            polarity_s.append(polarity_score)
            subjectivity_s.append(subjectivity_score)       

    extracted_dir=os.path.join(your_directory,ext_dir)

    for file in os.listdir(extracted_dir):
        if file.endswith(".txt"):
            file_path = os.path.join(extracted_dir, file)
            extract_variables(file_path)

    df['Positive Score'] = positive_s
    df['Negative Score'] = negative_s
    df['Polarity Score'] = polarity_s
    df['Subjectivity_s'] = subjectivity_s


    # ## Analysis of Readability 

    avg_sent_len=[]
    def analysis_readability(path):
        with open(path,'r',encoding='UTF-8') as f:
                text=f.read()
                sentences = sent_tokenize(text)
                sent_len=[len(nltk.word_tokenize(sentence)) for sentence in sentences]
                avg_length = sum(sent_len) / len(sent_len)
                avg_sent_len.append(avg_length)
            


    # ### Complex Word Count , Percentage of Complex Words  and Fog Index

    def is_complex(word):
        return len(wordnet.synsets(word)) > 1 

    def count_complex_words(text):
        words = word_tokenize(text)
        return sum(1 for word in words if is_complex(word))

    complex_count=[]
    percentage_complex=[]
    fog_index=[]
    def complex_percentage(path):
        with open(path, 'r',encoding='UTF-8') as file:
            text = file.read()
            sentences=sent_tokenize(text)
            words1=word_tokenize(text)
            complex_word_count = count_complex_words(text)
            percentage_complex_words= (complex_word_count / len(words1) )* 100
            complex_count.append(complex_word_count)
            percentage_complex.append(percentage_complex_words)
            
            sent_len=[len(nltk.word_tokenize(sentence)) for sentence in sentences]
            avg_sent_length = sum(sent_len) / len(sent_len)
            
            fog_ind= 0.4 * (avg_sent_length + percentage_complex_words)
            fog_index.append(fog_ind)

            


    # ###  Syllables Count Per Word
    def syllable_count(word):
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        if word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        if word.endswith("e"):
            count -= 1
        if count == 0:
            count += 1
        return count


    syl_count=[]
    def syllable_c(path):
        with open(path, 'r',encoding='UTF-8') as file:
            text = file.read()
            word_syl=[]
            avg_syll=0
            words=word_tokenize(text)
            for word in words:
                word_syl.append(syllable_count(word))
            avg_syll=sum(word_syl) / len(word_syl)
            syl_count.append(avg_syll)
                


    # ### Avg Number of Words per Sentence 

    avg_word_count=[]
    def avg_words(path):
        with open(path,'r',encoding='UTF-8') as f:
            c=0
            text=f.read()
            sentences = sent_tokenize(text)
            word=word_tokenize(text)
            c= len(word) / len(sentences)
            avg_word_count.append(c)   


    # ### Word Count 

    wc=[]
    def word_count(path):
        with open(path,'r',encoding='UTF-8') as f:
            c=0
            text=f.read()
            punct=r'[^\w\s]' 
            text=re.sub(punct, '', text)
            words=word_tokenize(text)
            c=len(words)
            wc.append(c)


    # ### Personal Pronouns

    pronoun_count=[]
    personal_pronouns = ['i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'themselves']
    def pronoun_c(path):
        with open(path,'r',encoding='UTF-8') as f:
            c=0
            text=f.read()
            text=text.lower()
            words = re.findall(r'\b\w+\b', text)
            c=sum(1 for word in words if word in personal_pronouns)
            pronoun_count.append(c)


    # ### Avg word length 

    avg_word_len=[]
    def word_len(path):
        with open(path,'r',encoding='UTF-8') as f:
            avg_len=0
            total_char=0
            text=f.read()
            words=word_tokenize(text)
            for word in words:
                total_char+=len(word)
            total_words=len(words)
            avg_len=total_char / total_words
            avg_word_len.append(avg_len)
            


    # ### Iterating through text files

    for file in os.listdir(extracted_dir):
        if file.endswith(".txt"):
            file_path = os.path.join(extracted_dir, file)
            avg_words(file_path)
            pronoun_c(file_path)
            word_len(file_path)
            analysis_readability(file_path)
            word_count(file_path)
            complex_percentage(file_path)
            syllable_c(file_path)


    # ### Writing to DataFrame 

    df['Average Sentence Length']= avg_sent_len
    df['Percentage of Complex Words'] = percentage_complex
    df['Fog Index'] = fog_index
    df['Average Number of Words Per Sentence'] = avg_word_count
    df['Complex Word Count'] = complex_count
    df['Word Count'] = wc
    df['Syllable Per Word'] = syl_count
    df['Personal Pronouns'] = pronoun_count
    df['Average Word Length'] = avg_word_len

    df
    df.to_excel('output.xlsx',index=False)


web_scraping('C:/Users/Deepak/Desktop/BlackCoffer_Assignment')