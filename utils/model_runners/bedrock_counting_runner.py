from typing import Optional, Tuple
from fmeval.constants import MIME_TYPE_JSON
from fmeval.model_runners.bedrock_model_runner import BedrockModelRunner
import json
from datetime import datetime, timezone
import fcntl
import os

class CountingBedrockModelRunner(BedrockModelRunner):
    '''Decorates the base BedrockModelRunner to emit invocation metrics,
      emits accurate model consumption figures in tokens using Bedrock 
      response metadata  available from the response headers.'''
    
    def __init__(self, model_id: str, content_template: str, output: str | None = None, log_probability: str | None = None, content_type: str = MIME_TYPE_JSON, accept_type: str = MIME_TYPE_JSON, metrics_folder: str = None,  model_key:str = None):
        """
        :param model_id: Id of the Bedrock model to be used for model predictions
        :param content_template: String template to compose the model input from the prompt
        :param output: JMESPath expression of output in the model output
        :param log_probability: JMESPath expression of log probability in the model output
        :param content_type: The content type of the request sent to the model for inference
        :param accept_type: The accept type of the request sent to the model for inference
        :param metrics_folder: The destination of the invocation metric file
        :param model_key: The base name of the file to disambiguate metrics
        """
        super().__init__(model_id = model_id, content_template = content_template, output = output, log_probability=log_probability, content_type = content_type, accept_type = accept_type)
        self._metrics_folder = metrics_folder
        self._model_key = model_key
        


    def predict(self, prompt: str) -> Tuple[Optional[str], Optional[float]]:
        """
        Invoke the Bedrock model and parse the model response.
        :param prompt: Input data for which you want the model to provide inference.
        """
        
        composed_data = self._composer.compose(prompt)
        body = json.dumps(composed_data)
        start_time = datetime.now(timezone.utc)

        response = self._bedrock_runtime_client.invoke_model(
            body=body, modelId=self._model_id, accept=self._accept_type, contentType=self._content_type
        )
        delta =  datetime.now(timezone.utc) - start_time
        processing_time = delta.total_seconds()
        model_output = json.loads(response.get("body").read())
        
        input_token_count = int(response["ResponseMetadata"]["HTTPHeaders"][
            "x-amzn-bedrock-input-token-count"
        ])
        
        output_token_count = int(response["ResponseMetadata"]["HTTPHeaders"][
            "x-amzn-bedrock-output-token-count"
        ])
        
        output = (
            self._extractor.extract_output(data=model_output, num_records=1)
            if self._extractor.output_jmespath_expression
            else None
        )
        log_probability = (
            self._extractor.extract_log_probability(data=model_output, num_records=1)
            if self._extractor.log_probability_jmespath_expression
            else None
        )
        
        sw = json.dumps({"input_tokens":input_token_count,"output_tokens":output_token_count, "processing_time":processing_time,"model_id":self._model_id})
        fp = open(self._metrics_folder + f"/{self._model_key}_usage.jsonl", 'a')
        fcntl.flock(fp.fileno(), fcntl.LOCK_EX)
        fp.seek(0, 2)
        fp.write(sw + "\n")
        fcntl.flock(fp.fileno(), fcntl.LOCK_UN)
        fp.close()

        return output, log_probability
    
    def __reduce__(self):
        """
        Custom serializer method used by Ray when it serializes instances of this
        class in eval_algorithms.util.generate_model_predict_response_for_dataset.
        """
        serialized_data = (
            self._model_id,
            self._content_template,
            self._output,
            self._log_probability,
            self._content_type,
            self._accept_type,
            self._metrics_folder,
            self._model_key
        )
        return self.__class__, serialized_data
