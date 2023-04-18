# Sync-AI API Client

This is the official python client to use with the Emotech Sync-AI platform. Please consult the API documentation for a detailed overview of its functions and usage.

## Usage

The `sync_ai_client.py` file contains the `SyncAiClient` class which is used as the base for making API calls.

The files `single_request.py` and `multiple_requests_from_file.py` contain functions that use the `SyncAiClient` to generate and download videos and animation files using the Sync-AI platform

A user needs their token to use this client. This can be found in the `Account Settings` section on `https://lipsync-ai.bubbleapps.io/`. 

## Examples

- Simple video output request
    - `python single_request.py --languge en-US --token USERS_TOKEN --output_file my_video.mp4 --output_type video --text "A text for the sync AI platform"`

