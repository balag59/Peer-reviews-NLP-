#flask imports
from flask import Flask,request,render_template, flash,jsonify

#import predict functions:
from predict import predictVolume,predictSentiment,predictSuggestions,predictEmotion

#python and keras imports
import pandas as pd
import numpy as np
from keras.models import load_model
from keras.preprocessing import sequence,text
np.random.seed(7)

#define constants
maxlen = 50
num_of_words=200000

#load the keras tokenizer
df = pd.read_csv('data/suggestions_data_cleaned.csv',encoding='latin1')
keras_tokenizer = text.Tokenizer(num_of_words)
keras_tokenizer.fit_on_texts(list(df['comments']))

#load the pre-trained models before loading the application
#sentiment_model = load_model('model/sentiment/model-17.hdf5')
suggestions_model = load_model('model/suggestions/model-09.hdf5')
"""test_review = np.array(['this is a test review'])
test_review = keras_tokenizer.texts_to_sequences(test_review)
test_review = sequence.pad_sequences(test_review, maxlen=maxlen)
#sentiment_model.predict(test_review)
suggestions_model.predict(test_review)"""

#simple flask app
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '10cr441f27d441f28567d441f2b2018j'

#app routes
#default web application app route
@app.route('/', methods=['GET', 'POST'])
#render the web application page and all it's fields
def renderPage():
    review = "Enter Review Text Here!"
    # Normal page load calls 'GET'. 'POST' gets called when one of the buttons is pressed
    if request.method == 'POST':
        # Check which button was pressed
        if request.form['submit'] == 'Analyze':
            review = request.form.get("text")
            displayMetrics(review)
        elif request.form['submit'] == 'Clear':
            review = ''

    # Render the HTML template. review gets fed into the textarea variable in the template
    return render_template('form.html', textarea=review)

#display all the required metrics on the web application
def displayMetrics(review):
    displayVolume(review)
    displaySentiment(review)
    displaySuggestions(review)
    displayEmotion(review)

#Display all the volume metrics on the screen in the web application
def displayVolume(review):
    total_volume,volume_without_stopwords = predictVolume(review)
    flash('Review text: {}'.format(review))
    flash('\n')
    flash('Volume Metrics')
    flash('Total volume of the review: {}'.format(total_volume))
    flash('Actual useful volume of the review without any stop words: {}'.format(volume_without_stopwords))
    flash('\n')

#Display all the sentiment metrics on the screen in the web application
def displaySentiment(review):
    sentiment_tone,sentiment_score = predictSentiment(review)
    flash('Sentiment metrics')
    flash('Sentiment tone : {}'.format(sentiment_tone))
    flash('Sentiment score : {}'.format(sentiment_score))
    flash('\n')

#Display all the suggestion metrics on the screen in the web application
def displaySuggestions(review):
    suggestions,suggestions_chances = predictSuggestions(review)
    flash('Suggestion metrics')
    flash('In this review, suggestions are {}'.format(suggestions))
    flash('\n')

#Display presence of praise and criticism
def displayEmotion(review):
    praise,criticism = predictEmotion(review)
    flash('Praise and criticism metrics')
    flash('Praise : {}'.format(praise))
    flash('Criticism : {}'.format(criticism))

#route to get all metrics via JSON request
@app.route('/all', methods = ['POST'])
def allJson():
    if not request.is_json:
        return 'Error : Request is not in JSON format'
    review_json = request.get_json()
    review_text = review_json['text']
    total_volume,volume_without_stopwords = predictVolume(review_text)
    sentiment_tone,sentiment_score = predictSentiment(review_text)
    suggestions,suggestions_chances = predictSuggestions(review_text)
    praise,criticism = predictEmotion(review_text)
    return jsonify({'text':review_text,'total_volume':total_volume,'volume_without_stopwords':volume_without_stopwords,'sentiment_tone':sentiment_tone,'sentiment_score':sentiment_score, 'suggestions':suggestions,'suggestions_chances':suggestions_chances, 'Praise':praise,'Criticism':criticism})

#route to get only volume metrics via JSON request
@app.route('/volume', methods = ['POST'])
def volumeJson():
    if not request.is_json:
        return 'Error : Request is not in JSON format'
    review_json = request.get_json()
    review_text = review_json['text']
    total_volume,volume_without_stopwords = predictVolume(review_text)
    return jsonify({'text':review_text,'total_volume':total_volume,'volume_without_stopwords':volume_without_stopwords})

#route to get only sentiment metrics via JSON request
@app.route('/sentiment', methods = ['POST'])
def sentimentJson():
    if not request.is_json:
        return 'Error : Request is not in JSON format'
    review_json = request.get_json()
    review_text = review_json['text']
    sentiment_tone,sentiment_score = predictSentiment(review_text)
    return jsonify({'text':review_text,'sentiment_tone':sentiment_tone,'sentiment_score':sentiment_score})

#route to get only emotion metrics via JSON request
@app.route('/emotions', methods = ['POST'])
def emotionsJson():
    if not request.is_json:
        return 'Error : Request is not in JSON format'
    review_json = request.get_json()
    review_text = review_json['text']
    praise,criticism = predictEmotion(review_text)
    return jsonify({'text':review_text,'Praise':praise,'Criticism':criticism})

#route to get only suggestion metrics via JSON request
@app.route('/suggestions', methods = ['POST'])
def suggestionsJson():
    if not request.is_json:
        return 'Error : Request is not in JSON format'
    review_json = request.get_json()
    review_text = review_json['text']
    suggestions,suggestions_chances = predictSuggestions(review_text)
    return jsonify({'text':review_text,'suggestions':suggestions,'suggestions_chances':suggestions_chances})

if __name__ == '__main__':
    app.run()
