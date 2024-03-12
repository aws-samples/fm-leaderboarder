import requests
import json

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
    
    def __init__(self, model_config: GPTModelConfig):
        self.config = model_config
        
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
        
        response = requests.request("POST", self.url, headers=headers, data=payload)
        return json.loads(response.text)["choices"][0]["message"]["content"], None