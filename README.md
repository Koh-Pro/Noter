# NOTER #

Noter is a software for **recording audio contents** and **make a 3d graph of the cooccurrence matrix**.
***
### ENVIRONMENT
* MacOS Big Sur 11.4
* Python 3.8.7
* google-cloud-speech 2.4.0
* Plotly 5.1.0
***
### QUICK START
1. run `noter1.py` as follows.
```
python noter1.py <FILE NAME FOR RECORDING AUDIO>.txt
```
This command starts recording. You can talk before the microphone. When you would like to finish recording, just say "Quit".

2. run `noter2.py` as follows. `<FILE NAME FOR RECORDING AUDIO>.txt` must be the same as #1.
```
python noter2.py <FILE NAME FOR RECORDING AUDIO>.txt
```
The python script starting, it automatically transforms the recorded text into a JSON file.
3. run `noter3.py` as follows.
```
python noter3.py <TITLE OF THE GRAPH>
```
You will see a 3d graph.
