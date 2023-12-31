# Project Goals:

* Use fastest STT (Speech to text) API **[Currently using OpenAI Deepgram]** [Speech2Text](https://huggingface.co/docs/transformers/model_doc/speech_to_text)
* Use trainable open-source TTS *[[TorToise TTS Fast]](https://github.com/152334H/tortoise-tts-fast)*
* Use fastest audio recording library. 
* Use a wake word, "Hey, Jarvis."
* Response generated by OpenAI ChatGPT (tokenized to behave like Jarvis)

## Virual Environment Setup For Testing

```pip install virtualenv```

```
# TO CREATE VENV
virtualenv <name>
```

```
# TO ACTVATE VENV
. .\<name>\Scripts\activate
```

```
# TO DEACTIVATE VENV
deactivate
```

## Temporary TTS Solution

```
pip install pyttsx3
```

## ChatGPT

* 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

## Deepgram

* [Deepgram Github](https://github.com/deepgram/deepgram-python-sdk)

* API key secret: `aa31cc8f3e1c6945664592285e2de5ccfbd17dd4`

```
pip install deepgram-sdk
```

[Went down this rabbit hole to ensure things built properly.](https://stackoverflow.com/questions/64261546/how-to-solve-error-microsoft-visual-c-14-0-or-greater-is-required-when-inst)
