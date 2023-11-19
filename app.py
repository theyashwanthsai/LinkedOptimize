# Import necessary libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os.path, time
import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
import pinecone
import os
import dotenv
import tempfile


dotenv.load_dotenv()

# Page selection
page_options = ['LinkedIn Profile Optimizer', 'Linkedin Optimizer']
selected_page = st.sidebar.radio('Select Page', page_options)

if selected_page == 'LinkedIn Profile Optimizer':
    st.title("LinkedIn Profile Optimizer")
    
    def search_and_send_request(keywords, till_page):
        connection_results = []
        for page in range(1, till_page + 1):
            st.write('\nINFO: Checking on page %s' % (page))
            query_url = 'https://www.linkedin.com/search/results/people/?keywords=' + keywords + '&origin=GLOBAL_SEARCH_HEADER&page=' + str(page)
            driver.get(query_url)
            time.sleep(5)
            html = driver.find_element(By.TAG_NAME, 'html')
            html.send_keys(Keys.END)
            time.sleep(5)
            linkedin_urls = driver.find_elements(By.CLASS_NAME, 'reusable-search__result-container')
            st.write('INFO: %s connections found on page %s' % (len(linkedin_urls), page))
            for index, result in enumerate(linkedin_urls, start=1):
                text = result.text.split('\n')[0]
                connection_action = result.find_elements(By.CLASS_NAME, 'artdeco-button__text')
                if connection_action:
                    connection = connection_action[0]
                else:
                    st.write("%s ) CANT: %s" % (index, text))
                    continue
                if connection.text == 'Connect':
                    try:
                        coordinates = connection.location_once_scrolled_into_view  # returns dict of X, Y coordinates
                        driver.execute_script("window.scrollTo(%s, %s);" % (coordinates['x'], coordinates['y']))
                        time.sleep(5)
                        connection.click()
                        time.sleep(5)
                        if driver.find_elements(By.CLASS_NAME, 'artdeco-button--primary')[0].is_enabled():
                            driver.find_elements(By.CLASS_NAME, 'artdeco-button--primary')[0].click()
                            connection_results.append(text)
                            st.write("%s ) SENT: %s" % (index, text))
                        else:
                            driver.find_elements(By.CLASS_NAME, 'artdeco-modal__dismiss')[0].click()
                            st.write("%s ) CANT: %s" % (index, text))
                    except Exception as e:
                        st.write('%s ) ERROR: %s' % (index, text))
                    time.sleep(5)
                elif connection.text == 'Pending':
                    st.write("%s ) PENDING: %s" % (index, text))
                else:
                    if text:
                        st.write("%s ) CANT: %s" % (index, text))
                    else:
                        st.write("%s ) ERROR: You might have reached the limit" % (index))

        return connection_results
    linkedin_username = st.text_input('LinkedIn Username')
    linkedin_password = st.text_input('LinkedIn Password', type='password')
    keywords = st.text_input('Search Keywords')
    till_page = st.number_input('Number of Pages to Check', min_value=1, value=5)
    submit_button = st.button(label="Submit")
    if submit_button:
        try:
            # LinkedIn Profile Optimizer code here...
            # ...
                driver = webdriver.Chrome((ChromeDriverManager().install()))
                driver.get('https://www.linkedin.com/login')
                driver.find_element('id', 'username').send_keys(linkedin_username)
                driver.find_element('id', 'password').send_keys(linkedin_password)
                driver.find_element('xpath', '//*[@type="submit"]').click()
                time.sleep(10)

                st.write("Connection Summary")
                connection_results = search_and_send_request(keywords=keywords, till_page=till_page)
        

                for result in connection_results:
                    st.write(result)
                

                

        except KeyboardInterrupt:
            st.write("\n\nINFO: User Canceled\n")
        except Exception as e:
            st.write('ERROR: Unable to run LinkedIn Profile Optimizer, error - %s' % (e))

elif selected_page == 'Linkedin Optimizer':
    st.title("Profile Optimizer")
    resume_uploader = st.file_uploader(label="Resume here")
    about = st.text_input("About here")
    submit_button = st.button(label="Submit")

    if submit_button:
        if resume_uploader:
            try:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(resume_uploader.read())
                    temp_filename = temp_file.name

                pdf_loader = PyPDFLoader(temp_filename)
                data = pdf_loader.load()

                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                texts = text_splitter.split_documents(data)

                embeddings = OpenAIEmbeddings(openai_api_key='')

                pinecone.init(api_key='', environment='')
                index_name = "demo"
                index = Pinecone.from_documents(texts, embeddings, index_name=index_name)
                retriever = index.as_retriever()

                llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0, openai_api_key='')
                memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
                chain = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory)

                query = f'Generate an about section for my LinkedIn profile. Use my Resume section for reference. Heres my about section {about}'
                result = chain.run({'question': query})
                print(result)
                st.write("Optimized About Section:", result)

                os.remove(temp_filename)

            except Exception as e:
                st.write(f'ERROR: Unable to run Profile Optimizer, error - {e}')
