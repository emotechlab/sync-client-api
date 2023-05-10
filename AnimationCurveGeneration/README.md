# Avatar Animation Curve Generation with Sync-AI

This client is intended for people with some familiarity with python. If you are unfamiliar with python try out our [web application](https://app.emotech.ai/login-animation?m=signup).

The `SyncAiAnimationClient` class in `animation_client.py` provides a client for the Emotech Sync AI Platform API to generate csv and fbx animation curve files. To generate content using the API a user needs their token, which can be found in the `Your Token` section in `Account Settings` on [the website](https://app.emotech.ai/account?tab=Profile).

For a detailed overview of the arguments please see the [API Documentation](https://emotech.gitbook.io/sync.ai-api-documentation-animation/).

# Usage

Create a virtual environment and install the required packages from [requirements.txt](../requirements.txt).

```
pip install -r requirements.txt
```

Single requests can be made from the command line using `single_request.py`, while multiple requests can be made using `multiple_requests_from_file.py` providing a json file of the job specifications for these requests.

### SSML Tags

SSML tags can be used within the `text` field to control the prosody of the generated speech, and also the expression on the avatar. See the [API Documentation](https://emotech.gitbook.io/sync.ai-api-documentation-animation/) for more details.

## Examples

### Single Requests

When using `single_request.py` the generated file will be saved to the `output_file`.

Some examples of usage of `single_requests.py` are shown below:
```
python single_request.py --language en-US --token USERS_TOKEN --output_file animation_curve.csv --output_type csv --text "A text for the sync AI platform" --actor female

python single_request.py --language en-US --token USERS_TOKEN --output_file animation_curve.fbx --output_type fbx --target_rig arkit --emotion happy --emotion_level 1 --text "A text for the sync AI platform" --actor male
```

Using an audio file that is on the local machine. The `text` transcript should match the audio in the file:
```
python single_request.py --language en-US --token USERS_TOKEN --output_file animation_curve.csv --output_type csv --audio_file /local/path/to/audio_file.wav --text "A text for the sync AI platform"
```

Using a url to an audio file hosted online. The `text` transcript should match the audio in the file:
```
python single_request.py --language en-US --token USERS_TOKEN --output_file animation_curve.csv --output_type csv --audio_url https://www.awebsite.com/audio_file.wav --text "A text for the sync AI platform"
```

Using ssml tags in the text:
```
python single_request.py --language en-US --token USERS_TOKEN --output_file animation_curve.csv --output_type csv --text "<speak>Here is a pause <break time='1s'/> and now <emo:express-as style='happy' styledegree='1.0'> the expression is happy</emo:express-as><\speak>" --actor female
```

### Multiple Requests from file

[inputs.json](inputs.json) is an example json file specifying multiple jobs, which can be used with the client as shown in the example below. 

```
python multiple_requests_from_file.py --token USERS_TOKEN --input_file inputs.json
```

In the above example, a json file of service responses will be saved to `inputs_results.json`.
