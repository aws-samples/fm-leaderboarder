import requests
import json
from datetime import datetime, timezone
import fcntl
import os
from dataclasses import dataclass
from typing import Tuple, Optional

from fmeval.model_runners.model_runner import ModelRunner

@dataclass
class GPTModelConfig:
    temperature: float
    top_p: float
    max_tokens: int
    api_key: str
    model_id: str


class GPTModelRunner(ModelRunner):
    url = "https://api.openai.com/v1/chat/completions"
    
    def __init__(self, model_config: GPTModelConfig, metrics_folder: str = None,  model_key:str = None):
        self.config = model_config
        self._metrics_folder = metrics_folder
        self._model_key = model_key
        
    def predict(self, prompt: str) -> Tuple[Optional[str], Optional[float]]:
        print(prompt)
        payload = json.dumps({
            "model": self.config.model_id,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "n": 1,
            "stream": False,
            "presence_penalty": 0,
            "frequency_penalty": 0
        })

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + self.config.api_key
        }
        start_time = datetime.now(timezone.utc)

        response = requests.request("POST", self.url, headers=headers, data=payload)
        delta =  datetime.now(timezone.utc) - start_time
        processing_time = delta.total_seconds() 


        response = json.loads(response.text)
        output = response["choices"][0]["message"]["content"]
        input_token_count = int(response["usage"]["prompt_tokens"])        
        output_token_count = int(response["usage"]["completion_tokens"])
        
        sw = json.dumps({"input_tokens":input_token_count,"output_tokens":output_token_count, "processing_time":processing_time, "model_id":self.config.model_id})
        fp = open(self._metrics_folder + f"/{self._model_key}_usage.jsonl", 'a')
        fcntl.flock(fp.fileno(), fcntl.LOCK_EX)
        fp.seek(0, 2)
        fp.write(sw + "\n")
        fcntl.flock(fp.fileno(), fcntl.LOCK_UN)
        fp.close()

        return output, None
    
    def __reduce__(self):
        """
        Custom serializer method used by Ray when it serializes instances of this
        class in eval_algorithms.util.generate_model_predict_response_for_dataset.
        """
        serialized_data = (
            self.config,
            self._metrics_folder,
            self._model_key
        )
        return self.__class__, serialized_data
