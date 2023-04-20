# Avatar Video Generation with Sync-AI

The `SyncAiVideoClient` class in `video_client.py` provides a client for the Emotech Sync AI Platform API to generate avatar videos. To generate content using the API a user needs their token, which can be found in the `Account Settings` section on [the website](https://lipsync-ai.bubbleapps.io/). 

For a detailed overview of the arguments please see the [API Documentation]().

# Usage

Single requests can be made from the command line using `single_request.py`, while multiple requests can be made using `multiple_requests_from_file.py` providing a json file of the job specifications for these requests.

## Examples

### Single Requests

When using `single_request.py` the generated file will be saved to the `output_file`.

Some examples of usage of `single_requests.py` are shown below:
```
python single_request.py --language en-US --token USERS_TOKEN --output_file my_video.mp4 --output_type video --text "A text for the sync AI platform"

python single_request.py --language en-US --token USERS_TOKEN --output_file my_video.mp4 --output_type video --actor vi --camera 7 --background_rgb 130,20,250 --emotion happy --emotion_level 1 --video_resolution 1920x1080 --text "A text for the sync AI platform"
```

Using a url to an audio file hosted online. The `text` transcript should match the audio in the file:
```
python single_request.py --language en-US --token USERS_TOKEN --output_file my_video.mp4 --audio_file /local/path/to/audio_file.wav --text "A text for the sync AI platform"
```

Using a url to an audio file that is on the local machine. The `text` transcript should match the audio in the file:
```
python single_request.py --language en-US --token USERS_TOKEN --output_file my_video.mp4 --audio_url https://www.awebsite.com/audio_file.wav --text "A text for the sync AI platform"
```


### Multiple Requests from file

(inputs.json)[inputs.json] is example json file specifying multiple jobs, which can be used with the client as shown in the example below. 

```
python multiple_requests_from_file.py --token USERS_TOKEN --input_file inputs.json
```

In the above example, a json file of service responses will be saved to `inputs_results.json`.
