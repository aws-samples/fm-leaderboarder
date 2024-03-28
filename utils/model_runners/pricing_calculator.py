import boto3
import json
import traceback
import sys
import os

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PricingCalculator():
  '''Calculate the pricing of the inference depending on the model specific.
  Uses pricing API where available, lookup tables from pricing sources when not available,
  and can calculate cost both per token pricing and per hosting time models.'''
  COST_PER_TOKEN = 'cpt'
  COST_PER_HOUR = 'cph'
  
  _pricing_client = boto3.client('pricing', region_name = 'us-east-1')
  _model_prive_by_name = {}
  _model_name_by_id = {}
  @classmethod
  def static_init(self):
    for model in boto3.client('bedrock').list_foundation_models()['modelSummaries']:
        PricingCalculator._model_name_by_id[model['modelId']] = model['modelName']

    pricing_data = []

    paginator = PricingCalculator._pricing_client.get_paginator('get_products')
    operation_parameters = {'ServiceCode': 'AmazonBedrock'}
    page_iterator = paginator.paginate(**operation_parameters)

    try:
        for page in page_iterator:
            pricing_data.extend(page['PriceList'])
    except Exception as e:
        logger.log(logging.WARNING, f'Failed to fetch price list: {e}')
        return
    
    

    for item in pricing_data:
        try:
            price_item = json.loads(item)
            usage_type = price_item['product']['attributes']['usagetype']
            region_code = price_item['product']['attributes']['regionCode']
            if region_code != boto3.session.Session().region_name:
                continue
            if 'inferenceType' in price_item['product']['attributes']:
                inference_type = price_item['product']['attributes']['inferenceType']
            else:
                inference_type = 'N/A'
            
            if 'model' in price_item['product']['attributes']:
                model_name = price_item['product']['attributes']['model']
            elif 'titanModel' in price_item['product']['attributes']:
                model_name = price_item['product']['attributes']['titanModel']
            elif 'titanModelUnit' in price_item['product']['attributes']:
                model_name = price_item['product']['attributes']['titanModelUnit']
            else:
                logger.log(logging.ERROR, "Model name is missing. Skipping price item: {price_item['product']['attributes']}")
                continue;
                
            l1 = price_item['terms']['OnDemand']
            l2 = list(l1.values())[0]['priceDimensions']
            price_per_unit = list(l2.values())[0]['pricePerUnit']['USD']
            unit = list(l2.values())[0]['unit']
            if not model_name in PricingCalculator._model_prive_by_name:
                PricingCalculator._model_prive_by_name[model_name] = dict()
            PricingCalculator._model_prive_by_name[model_name]['model_id'] = model_name
            if 'input-tokens' in usage_type and unit =='1K tokens':
                PricingCalculator._model_prive_by_name[model_name]['input_cost_per_1000_tokens'] = price_per_unit
            elif 'output-tokens' in usage_type and unit =='1K tokens':
                PricingCalculator._model_prive_by_name[model_name]['output_cost_per_1000_tokens'] = price_per_unit
            elif 'ProvisionedThroughput' in usage_type:
                PricingCalculator._model_prive_by_name[model_name]['instance_type'] = usage_type
                PricingCalculator._model_prive_by_name[model_name]['hosting_cost_per_hour'] = price_per_unit
            else:
                pass
        except Exception as e:
            logger.log(logging.ERROR, 'ERROR: Failed to parse price item')
            raise e;



    #TODO Waiting for an official api to support markeplace's models
  _lookup_price_table = [
      {
        "model_id": "anthropic.claude-v2:1",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.008,
        "output_cost_per_1000_tokens": 0.024
      },
      {
        "model_id": "anthropic.claude-v2",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.008,
        "output_cost_per_1000_tokens": 0.024
      },
      {
        "model_id": "anthropic.claude-instant-v1",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.0008,
        "output_cost_per_1000_tokens": 0.0024
      },
      {
        "model_id": "amazon.titan-text-lite-v1",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.0003,
        "output_cost_per_1000_tokens": 0.0004
      },
      {
        "model_id": "amazon.titan-text-express-v1",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.0008,
        "output_cost_per_1000_tokens": 0.0016
      },
      {
        "model_id": "meta.llama2-13b-chat-v1",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.00075,
        "output_cost_per_1000_tokens": 0.001
      },
      {
        "model_id": "cohere.command-light-text-v14",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.0003,
        "output_cost_per_1000_tokens": 0.0006
      },

      {
        "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.003,
        "output_cost_per_1000_tokens": 0.015
      },
      {
        "model_id": "anthropic.claude-3-haiku-20240307-v1:0",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.00025,
        "output_cost_per_1000_tokens": 0.00125
      },
      {
        "model_id": "meta.llama2-70b-chat-v1",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.00195,
        "output_cost_per_1000_tokens": 0.00256
      },
      {
        "model_id": "ai21.j2-mid-v1",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.0125,
        "output_cost_per_1000_tokens": 0.0125
      },
    {
        "model_id": "ai21.ai21.j2-ultra-v1",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.0188,
        "output_cost_per_1000_tokens": 0.0188
      },
    {
        "model_id": "cohere.command-text-v14",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.0015,
        "output_cost_per_1000_tokens": 0.0020
      },
    {
        "model_id": "mistral.mistral-7b-instruct-v0:2",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.00015,
        "output_cost_per_1000_tokens": 0.0002
      },
      {
        "model_id": "mistral.mixtral-8x7b-instruct-v0:1",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.00045,
        "output_cost_per_1000_tokens": 0.0007

      },
      {
        "model_id": "self_hosted_test",
        "id_type": "model_id",
        "instance_type": "g5.12xlarge",
      },
      {
        "model_id": "gpt-4-0125-preview",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.01,
        "output_cost_per_1000_tokens": 0.03
      },
      {
        "model_id": "gpt-4-1106-preview",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.01,
        "output_cost_per_1000_tokens": 0.03
      },
      {
        "model_id": "gpt-4-1106-vision-preview",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.01,
        "output_cost_per_1000_tokens": 0.03
      },
      {
        "model_id": "gpt-4",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.03,
        "output_cost_per_1000_tokens": 0.06
      },
      {
        "model_id": "gpt-4-32k",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.06,
        "output_cost_per_1000_tokens": 0.12
      },
      {
        "model_id": "gpt-3.5-turbo-0125",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.0005,
        "output_cost_per_1000_tokens": 0.0015
      },
      {
        "model_id": "gpt-3.5-turbo-instruct",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.0015,
        "output_cost_per_1000_tokens": 0.002
      },
      {
        "model_id": "gpt-3.5-turbo-1106",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.001,
        "output_cost_per_1000_tokens": 0.002
      },
      {
        "model_id": "gpt-3.5-turbo-0613",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.0015,
        "output_cost_per_1000_tokens": 0.002
      },
      {
        "model_id": "gpt-3.5-turbo-16k-0613",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.003,
        "output_cost_per_1000_tokens": 0.004
      },
      {
        "model_id": "gpt-3.5-turbo-0301",
        "id_type": "model_id",
        "input_cost_per_1000_tokens": 0.0015,
        "output_cost_per_1000_tokens": 0.002
      }    
    ]


  @classmethod
  def _instance_pricing(self, instance_type):
    data = PricingCalculator._pricing_client.get_products(ServiceCode='AmazonEC2', Filters=[{"Field": "tenancy", "Value": "shared", "Type": "TERM_MATCH"},
      {"Field": "operatingSystem", "Value": "Linux", "Type": "TERM_MATCH"},
      {"Field": "preInstalledSw", "Value": "NA", "Type": "TERM_MATCH"},
      {"Field": "instanceType", "Value": instance_type, "Type": "TERM_MATCH"},
      {"Field": "marketoption", "Value": "OnDemand", "Type": "TERM_MATCH"},
      {"Field": "regionCode", "Value": boto3.session.Session().region_name , "Type": "TERM_MATCH"},
      {"Field": "capacitystatus", "Value": "Used", "Type": "TERM_MATCH"}])
    for price in (json.loads(x) for x in data['PriceList']):
        first_id =  list(price['terms']['OnDemand'].keys())[0]
        price_data = price['terms']['OnDemand'][first_id]
        second_id = list(price_data['priceDimensions'].keys())[0]
        instance_price = price_data['priceDimensions'][second_id]['pricePerUnit']['USD']
        if float(instance_price) > 0:
            return float(instance_price)
    raise(Exception(f'Failed to get instance pricing for instance type {instance_type}'))

  @classmethod 
  def retrieve_cost_structure(self, model_id):
      cost_structure = None
      mName = PricingCalculator._model_name_by_id[model_id] if model_id in PricingCalculator._model_name_by_id else None
      if not (mName == None):
          #handle internal model   
          if mName in PricingCalculator._model_prive_by_name:
              return PricingCalculator._model_prive_by_name[mName]
      for model_cost in PricingCalculator._lookup_price_table:
          if model_id in model_cost['model_id'] or model_id.split(':')[0] in model_cost['model_id'].split(':')[0]:
              return model_cost 

  @classmethod
  def _calculate_usage_cost(self, model_id, input_tokens:int=0, output_tokens:int=0, inference_time_s:float=0, instance_type:str = None):
      try:
          cost_structure = PricingCalculator.retrieve_cost_structure(model_id)
          if cost_structure is None:
              return None
          if 'instance_type' in cost_structure and cost_structure['instance_type'] == instance_type:
              return PricingCalculator._calculate_usage_per_second(inference_time_s, cost_structure), cost_structure, PricingCalculator.COST_PER_HOUR
          else: 
              return PricingCalculator._calculate_usage_per_token(input_tokens, output_tokens, cost_structure),cost_structure, PricingCalculator.COST_PER_TOKEN
      except Exception as e:
          logger.log(logging.ERROR, f'Failed to calculate cost for model {model_id}, invokation parameters: {input_tokens}, {output_tokens}, {inference_time_s}')
          raise e;        

  @classmethod
  def _calculate_usage_per_second(self, inference_time_s:float=0, cost_structure = None):
      if 'hosting_cost_per_hour' in cost_structure:
          return cost_structure['hosting_cost_per_hour'] * inference_time_s / (60*60)
      return PricingCalculator._instance_pricing(cost_structure['instance_type']) * inference_time_s / (60*60) 
  
  @classmethod
  def _calculate_usage_per_token(self, input_tokens, output_tokens, model_cost):
      input_cost = model_cost['input_cost_per_1000_tokens'] * input_tokens / 1000
      output_cost = model_cost['output_cost_per_1000_tokens'] * output_tokens / 1000
      return input_cost + output_cost 
  
  @classmethod
  def read_model_score_aggregate(self, model_name, folder):
      '''Read model usage information from the test report and calculate the overall 
      cost based on the known pricing, it expects to find a file {folder}/{model_name}_usage.jsonl
      containing json lines for each invocation with these keys:
      model_id #name of the model as used in the invocation API
      input_tokens #number of token in the prompt
      output_tokens #number of token in the output
      processing_time #total invocation time in second
      instance_type #type of the instance for models priced on hosting time
      '''
      file = f"{folder}/{model_name}_usage.jsonl"
      if not os.path.exists(file):
          return None
      
      # Initialize the sum dictionary
      sum_dict = {
      'input_tokens': 0,
      'output_tokens': 0,
      'processing_time': 0,
      'cost': None,
      'cost_model': None,
      'cost_hour': None,
      'cost_input_1M': None,
      'cost_output_1M': None
      }
      samples = 0

      with open(file, 'r') as file:
          for line in file:
              samples = samples + 1
              item = json.loads(line)
              input_tokens = item['input_tokens'] if 'input_tokens' in item else 0
              output_tokens = item['output_tokens'] if 'output_tokens' in item else 0
              processing_time = item['processing_time'] if 'processing_time' in item else 0                  
              cost, cost_structure, cost_model = PricingCalculator._calculate_usage_cost(item['model_id'], input_tokens, output_tokens, processing_time,
                  item['instance_type'] if 'instance_type' in item else None )
              if sum_dict['cost_model'] == None:
                  sum_dict['cost_model'] = cost_model
                  if cost_model == PricingCalculator.COST_PER_HOUR:
                      sum_dict['cost_hour'] = cost_structure['hosting_cost_per_hour'] if 'hosting_cost_per_hour' in cost_structure else PricingCalculator._instance_pricing(cost_structure['instance_type'])
                  if cost_model == PricingCalculator.COST_PER_TOKEN:
                      sum_dict['cost_input_1M'] = cost_structure['input_cost_per_1000_tokens']*1000.0
                      sum_dict['cost_output_1M'] = cost_structure['output_cost_per_1000_tokens']*1000.0
              sum_dict['input_tokens'] += input_tokens
              sum_dict['output_tokens'] += output_tokens
              sum_dict['processing_time'] += processing_time
              if cost is None:
                  continue
              if sum_dict['cost'] is None: 
                  sum_dict["cost"] = cost
              else:
                  sum_dict['cost'] += cost
                                                                      

      # Convert the sum dictionary to JSON string
      sum_dict['samples'] = samples
      sum_dict['avg_cost'] = sum_dict['cost'] / samples
      sum_dict['avg_processing_time'] = sum_dict['processing_time'] / samples
      return sum_dict

  @classmethod
  def cleanup_previous_runs(self, dir_path):
    for file_name in os.listdir(dir_path):
      if file_name.endswith('_usage.jsonl'):
          # Construct the full file path
          file_path = os.path.join(dir_path, file_name)
          os.remove(file_path)

PricingCalculator.static_init()