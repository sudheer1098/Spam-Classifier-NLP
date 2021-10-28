import streamlit as st
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import sqlite3
from PIL import Image
import pickle
import string
from datetime import datetime

# def local_css(file_name):
#     with open(file_name) as f:
#         st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)

# local_css("style.css")

def load_model():
    with open('model.pkl', 'rb') as file:
        data = pickle.load(file)
    return data

data = load_model()

image = Image.open("Media/image.png")

conn = sqlite3.connect("messages.db")
with conn:
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS messages_inbox(ham TEXT, spam TEXT)")


def text_normalize(text):
    """
    
    remove punctuations in text
    remove stopwords
    converts each word in data into its base form (lemma)
    return list of text words
    
    """
    text = text.lower()
    
    nopunc = [char for char in text if char not in string.punctuation] # remove punctuation
    nopunc = "".join(nopunc)
    
    nostop = [word for word in nopunc.split() if word not in stopwords.words("english")] # tokenization and stopwords removal 
    
    ps = PorterStemmer()
    stem_text = [ps.stem(word) for word in nostop]
    
    return [word for word in stem_text] 


pipe1 = data['model1']
pipe2 = data['model2']

hide_menu_style = """
                    <style>
                    #MainMenu {visibility: hidden; }
                    footer {visibility: hidden;}
                    </style>
                  """
st.markdown(hide_menu_style, unsafe_allow_html = True)

def main():

    menu = ["Home", "Inbox"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":

        col1, mid, col2 = st.columns([10,1,20])
        with col1:
            st.image(image, width=None)
        with col2:
            st.title("SMS SPAM CLASSIFIER")
            st.subheader("Enter a message")
            msg = st.text_area('Message here', value='Eg. Congratulations! You have won Rs.10,000 worth gift card, claim now.')
                    
            ok = st.button("Submit")

            if ok:
                X = np.array([msg])
                y = pipe2.predict(X)[0]

                st.header("RESULT")
                print(y)
                if y==0:
                    result = '<p style="font-family:Verdana; color:green; font-size: 30px;"><b>NOT A SPAM MESSAGE</b></p>'
                    st.markdown(result, unsafe_allow_html=True)
                    with conn:
                        cursor.execute("INSERT INTO messages_inbox(ham)VALUES(?)",(msg+"   -"+str(datetime.today().strftime("%I:%M %p")),))
                        
                else:
                    result = '<p style="font-family:Verdana; color:red; font-size: 30px;"><b>SPAM MESSAGE</b></p>'
                    st.markdown(result, unsafe_allow_html=True)
                    with conn:
                        cursor.execute("INSERT INTO messages_inbox(spam)VALUES(?)",(msg+"   -"+str(datetime.today().strftime("%I:%M %p")),))

    else:
        st.subheader("INBOX")
        #st.success("Full layout")
        col1, col2 = st.columns(2)

        col1.success("Primary")
        with col1:
            with conn:
                cursor.execute("SELECT * FROM messages_inbox WHERE ham is not NULL")
            msgs = cursor.fetchall()
            for k in range(len(msgs)-1, -1, -1):
                st.markdown(f'''{msgs[k][0]}''')

        col2.success("Spam")
        with col2:
            with conn:
                cursor.execute("SELECT * FROM messages_inbox WHERE spam is not NULL")
            msgs = cursor.fetchall()
            for k in range(len(msgs)-1, -1, -1):
                st.markdown(f'''{msgs[k][1]}''')

main()
