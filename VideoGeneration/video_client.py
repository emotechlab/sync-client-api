import json
import os
from tqdm import tqdm
import requests


def get_tts_params(voice=None, speed=None):
    tts_params =  {
        "engine": "Google",
    }

    if voice:
        tts_params["voice"] = voice

    if speed != 0:
        tts_params["speed"] = speed

    return tts_params


class SyncAiVideoClient():

    def __init__(self, token, url=None):
        if not url:
            self.url = "https://lipsync-ai.api.emotechlab.com/lipsync"
        
        self.token = token
        self.valid_fields = ['language', 'actor', 'text', 'camera', 'background_rgb', 'sentences_file', 'tts_voice', 'tts_speed', 'target_rig', 'audio_url', 'audio_file', 'emotion', 'emotion_level', 'token', 'frame_height', 'frame_width', 'output_dir', 'output_file']

    def check_status(self, job_id):
        resp = requests.get(os.path.join(self.url, f"status?jobId={job_id}&token={self.token}"))
        return resp.json()
    
    def download_content(self, job_id, save_file):
        # check status in a loop until a 'finished' status is returned then download the video
        # file extension of save_file must match the output type of the request
        while True:
            status = self.check_status(job_id)
            if status["status"] == "finished":
                break
            elif status["status"] == "failed":
                print("Job {} failed with: {}".format(job_id, status))
                return status
        
        # get file extension from the save_file
        download_file = job_id + "." + save_file.split(".")[-1]
        resp = requests.get(os.path.join(self.url, f"download?fileName={download_file}&token={self.token}"))

        try: 
            # Download failed if the response is json
            resp_json = resp.json()
            print("Download failed: ", resp_json)
        except:
            # File is returned in bytes in the response
            with open(save_file, "wb") as fp:
                fp.write(resp.content)

        return None

        
    def generate(self, text, language, target_rig, actor=None, camera=None, tts_voice=None, tts_speed=None, background_rgb=None, audio_url=None, audio_file=None, emotion="", emotion_level=1, frame_width=None, frame_height=None, display=False):
        # Sends a request to generate a video.

        if audio_url and audio_file:
            raise Exception("Only one of audio_file or audio_url should be supplied.")

        is_ssml = False
        if "<speak>" in text:
            is_ssml = True

        # set emotion and level
        emotion_obj = None
        if emotion:
            emotion_obj = {
                "level": emotion_level,
                "expression": emotion
            }
        
        # set background color
        background_color = None
        if background_rgb:
            red, green, blue = background_rgb.split(",")
            background_color = {
                "red": int(red),
                "green": int(green),
                "blue": int(blue),
            }

        output = {
            "type": "video",
            "width": frame_width,
            "height": frame_height,
            "background_color": background_color
        }
    
        job = {
            "target_rig": target_rig,
            "text": text,
            "language": language,
            "tts_params": get_tts_params(tts_voice, tts_speed),
            "output": output,
            "is_ssml": is_ssml,
            "wait_time": None,
        }

        if actor:
            job["actor"] = actor

        if camera is not None:
            job["camera"] = camera

        if emotion_obj:
            job["emotion"] = emotion_obj
        
        if audio_url and audio_file:
            raise Exception("Both audio_url and audio_path are given. Only one can be used.")
        elif audio_url:
            job["audio_url"] = audio_url

        if audio_file:
            # Send multipart request if audio file is present
            with open(audio_file, "rb") as fp:
                resp = requests.post(
                    os.path.join(self.url, f"generate?token={self.token}"), 
                    files={"audio": fp, "job": json.dumps(job, indent=2).encode('utf-8')}
                )
        else: 
            resp = requests.post(os.path.join(self.url, f"generate?token={self.token}"), json=job)
    
        if not resp:
            response = {"error": "curl request failed"}
        else:
            response = resp.json()

        if display:
            print(response)

        return response

    def generate_and_download_from_file(self, input_file):
        """ 
        input_file should be a json with a "jobs" field containing a list of settings/arguments to use for each sample
        Each sample must have a "language", "text", and "output_file" fields. If "output_type" is "video" (which is default),
        then the "camera" and "actor" field must be supplied as well.
        eg.
        {
            "jobs": [
                {
                    "language": "en-US",
                    "text": "I am powered by Emotech's revolutionary A.I. technology",
                    "camera": 0,
                    "actor": "caprica",
                    "output_file": "/path/to/my_video.mp4"
                },
                {
                    "language": "ar",
                    "actor": "laura",
                    "text": "أنا مدعوم بتقنية الذكاء الاصطناعي الثورية من Emotech",
                    "camera": 7,
                    "background_rgb": "150,120,180",
                    "emotion": "sad",
                    "emotion_level": 0.5,
                    "output_file": "/path/to/my_video2.mp4"
                },
                ...
            ]
        }

        - Generate method responses are saved in a json file in the save_dir 
        with the same name as the input file with '_results' appended to the end.

        ** NOTE **
        This function waits for each video to be generated, then downloaded before sending the next request
        """
        with open(input_file, "r") as json_file:
            input_samples = json.load(json_file)
        print(input_samples)
        if "jobs" not in input_samples:
            raise Exception("Input json file incorrect format, needs \"jobs\" field")

        # prepare results file
        results_file = f"{os.path.splitext(input_file)[0]}_results.json"
        if not os.path.exists(results_file):
            open(results_file, 'a').close()
    
        results = {}    
        required_fields = ["text", "language", "output_file", "target_rig"]
        # send requests
        for i, args_dictionary in tqdm(enumerate(input_samples["jobs"]), total=len(input_samples["jobs"])):
            # target rig is always metahumans for generating video content
            args_dictionary["target_rig"] = "metahumans"
            for field in required_fields:
                if field not in args_dictionary:
                    raise Exception("Input sample {} is missing {} field".format(i, field))
            
            output_file = args_dictionary.pop("output_file")

            for key in args_dictionary.keys():
                if key not in self.valid_fields:
                    raise Exception("Input sample {} has invalid field: {}".format(i, key))

            response = self.generate(**args_dictionary)
            results[i] = response

            status = self.download_content(response["jobId"], output_file)

            # if content download fails, save it to the results dictionary
            if status is not None:  
                results[i] = {results[i], status}
            
        with open(results_file, "w") as fp:
            json.dump(results, fp, indent=4)


