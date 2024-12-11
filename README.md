# README for Roman Urdu Processing and Emotion Detection Project

## Project Overview
This project is designed to process Roman Urdu sentences, detect user emotions (happy, sad, neutral, angry), generate appropriate responses, and synthesize speech using StyleTTS2 or Whisper Turbo. The project leverages reinforcement learning techniques to improve response quality and user mood while integrating Retrieval-Augmented Generation (RAG) for sentiment analysis and optimized response generation. All chat records are stored in MongoDB for analysis and tracking.

---

## Features
1. **Emotion Detection**
   - Processes Roman Urdu sentences to identify one of four emotions: happy, sad, neutral, or angry.

2. **Response Generation**
   - Generates appropriate text responses based on detected emotions using LLaMA 3.2:1B, gamma:2b or another lightweight LLM.

3. **Speech Synthesis**
   - Converts generated responses into speech using StyleTTS2 or Whisper Turbo.

4. **Reinforcement Learning**
   - Optimizes the system’s ability to generate responses that improve user mood.

5. **Data Management**
   - Stores chat logs, emotions, responses, and timestamps in MongoDB for further analysis.

6. **RAG Integration**
   - Enhances tagging, response generation, and sentiment improvement using Retrieval-Augmented Generation.

---

## Installation

### Prerequisites
- Python 3.8+
- MongoDB Atlas account
- StyleTTS2 or Whisper Turbo model
- Roman-Urdu-English Code-Switched Emotion Dataset (available on Kaggle)

### Steps
1. Clone the repository:
   ```bash
   git clone  https://github.com/AliArfa852/NLP_Project.git
   cd NLP_Project
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up MongoDB:
   - Create a MongoDB Atlas cluster.
   - Configure your `.env` file with the connection string:
     ```env
     MONGO_URI=<your-mongo-db-connection-string>
     ```

4. Download the dataset:
   - Obtain the Roman-Urdu-English Code-Switched Emotion Dataset from Kaggle.
   - Place the dataset in the `data/` folder.

5. Prepare pretrained models:
   - Download and integrate StyleTTS2/Whisper Turbo and the LLaMA 3.2:1B model.
   - Place the models in the `models/` folder.

---

## Usage

1. Start the application:
   ```bash
   python app.py
   ```

2. Access the application:
   - Open your browser and go to `http://localhost:5000`.

3. Input Roman Urdu text to:
   - Detect emotions.
   - Generate responses.
   - Synthesize speech outputs.

---

## Architecture

### Workflow
1. **Input Processing**: User inputs Roman Urdu sentences.
2. **Emotion Detection**: The system analyzes the input and detects emotions using an LLM.
3. **Response Generation**: A response is generated based on detected emotions.
4. **Speech Synthesis**: Converts the generated response to speech.
5. **Reinforcement Learning**: Refines response generation for user satisfaction.
6. **Data Logging**: Logs the entire conversation in MongoDB for analysis.

---

## Datasets
### Roman-Urdu-English Code-Switched Emotion Dataset
- Includes labeled sentences for happy, sad, neutral, and angry emotions.
- Preprocessed for model fine-tuning and training.

---

## Configuration
### Environment Variables
- **MONGO_URI**: MongoDB connection string
- **MODEL_PATH**: Path to LLaMA 3.2:1B model
- **TTS_MODEL_PATH**: Path to StyleTTS2/Whisper Turbo model

---

## Contribution Guidelines
1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Feature description"
   ```
4. Push changes:
   ```bash
   git push origin feature-name
   ```
5. Submit a pull request.

---

## Known Issues
1. **Accuracy Variations**:
   - Certain emotions in Roman Urdu may overlap, causing minor detection inaccuracies.
2. **Model Latency**:
   - Whisper Turbo may introduce slight delays during speech synthesis.

---

## Future Work
1. Expand emotion categories to include additional sentiments.
2. Optimize reinforcement learning algorithms for faster convergence.
3. Integrate a mobile-friendly interface.

---



Thank you for using our Roman Urdu Processing and Emotion Detection system! Feel free to contribute or reach out for support.


## Features

- **Emotion Detection:** Identifies emotions in user input.
- **Response Generation:** Generates context-aware responses based on detected emotions.
- **Speech Synthesis:** Converts text responses to speech.
- **Reinforcement Learning:** Optimizes responses to improve user mood.
- **Data Logging:** Stores interactions in MongoDB for analysis.


 DATASET : https://www.kaggle.com/datasets/drkhurramshahzad/roman-urdu-english-code-switched-emotion-dataset

```bash
git clone https://github.com/AliArfa852/NLP_Project.git


```run 
python /src/pipeline.py
# just run the pipeline code 
or u can run indivijually to test components 