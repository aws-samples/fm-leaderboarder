import boto3
import json
import traceback
import sys
import os

client = boto3.client('pricing')

modelNameMap = {}
for model in boto3.client('bedrock').list_foundation_models()['modelSummaries']:
    modelNameMap[model['modelId']] = model['modelName']

client = boto3.client('pricing', region_name = 'us-east-1')
next_token = None
filter = []
objects = []    
while True:
    try:
        if next_token:
            response = client.get_products(ServiceCode='AmazonBedrock', NextToken=next_token)
        else:
            response = client.get_products(ServiceCode='AmazonBedrock')
        #print(f"Found {len(response['PriceList'])} items")
        objects.extend(response['PriceList'])
        
        if 'NextToken' in response:
            next_token = response['NextToken']
        else:
            break
    except Exception as e:
        print(f'ERROR: Failed to fetch price list')
        print(e)
        break
        
mName_price_map = {}

for item in objects:
    try:
        price_item = eval(item)
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
            print(f"ERROR: Model name is missing. Skipping price item: {price_item['product']['attributes']}")
            continue;
            
        l1 = price_item['terms']['OnDemand']
        l2 = list(l1.values())[0]['priceDimensions']
        price_per_unit = list(l2.values())[0]['pricePerUnit']['USD']
        mName_price_map[model_name] = ({'region_code': region_code,'model_name':model_name, 'inference_type': inference_type, 'usage_type':usage_type, 'price_per_unit':price_per_unit})
    except Exception as e:
        print(f'ERROR: Failed to parse price item')
        raise e;



#TODO Waiting for an official api to support markeplace's models
source = [
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


COST_PER_TOKEN = 'cptoken'
COST_PER_TIME = 'cptime'

def instance_pricing(instance_type):
    data = client.get_products(ServiceCode='AmazonEC2', Filters=[{"Field": "tenancy", "Value": "shared", "Type": "TERM_MATCH"},
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
    

def calculate_usage_cost(model_id, input_tokens:int=0, output_tokens:int=0, inference_time_ms:float=0):
    try:
      mName = modelNameMap[model_id] if model_id in modelNameMap else None
      if not (mName == None):
          #handle internal model   
          if mName in mName_price_map:
              print('pricemap match')
              return mName_price_map[mName]
      for model_cost in source:
          if model_id in model_cost['model_id'] or model_id.split(':')[0] in model_cost['model_id'].split(':')[0]:
              if ('instance_type' in model_cost) and (inference_time_ms > 0):        
                  return instance_pricing(model_cost['instance_type']) * inference_time_ms / (1000*60*60) 
              else:
                  return model_cost['input_cost_per_1000_tokens'] * (input_tokens/1000) + model_cost['output_cost_per_1000_tokens'] * (output_tokens/1000)
    except Exception as e:
      print(f'ERROR: Failed to calculate cost for model {model_id}, invokation parameters: {input_tokens}, {output_tokens}, {inference_time_ms}')
      raise e;    


def read_model_score_aggregate(model_id, folder):
    data = []
    file = f"{folder}/{model_id}_usage.jsonl"
    if not os.path.exists(file):
        return None

    with open(file, 'r') as file:
        for line in file:
            data.append(json.loads(line))

    # Initialize the sum dictionary
    sum_dict = {
    'input_tokens': 0,
    'output_tokens': 0,
    'processing_time': 0,
    'cost': 0
    }

    # Calculate the sum of each key
    for item in data:
        sum_dict['input_tokens'] += item['input_tokens']
        sum_dict['output_tokens'] += item['output_tokens']
        sum_dict['processing_time'] += item['processing_time']
        sum_dict['cost'] += item['cost']

    # Convert the sum dictionary to JSON string
   
    return sum_dict
