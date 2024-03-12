from datasets import load_dataset
import re
import json


def clean_text(text):
    text = text.encode("ascii", "ignore").decode()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@[^\s]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return re.sub(r"\^[^ ]+", "", text)


def create_conversation_text(data_point):
    text = ""
    for item in data_point["log"]:
        user = clean_text(item["user utterance"])
        text += f"user: {user.strip()}\n"

        agent = clean_text(item["system response"])
        text += f"agent: {agent.strip()}\n"

    return text


def generate_text(data_point):
    summaries = json.loads(data_point["original dialog info"])["summaries"][
        "abstractive_summaries"
    ]
    summary = summaries[0]
    summary = " ".join(summary)

    conversation_text = create_conversation_text(data_point)
    return {
        "document": conversation_text,
        "summary": summary,
        "id": data_point['original dialog id']
    }


def create_train_test_files(folder):
    dataset = load_dataset("Salesforce/dialogstudio", "TweetSumm")
    tables = ["test", "validation"]
    modified_db = dict()

    for table in tables:
        for i in range(len(dataset[table])):

            example = generate_text(dataset[table][i])
            if table not in modified_db:
                modified_db[table] = []
            modified_db[table].append(example)

    modified_db['test'].extend(modified_db['validation'])
    del modified_db['validation']

    print(f"Test set size: {len(modified_db['test'])}")

    for k, v in modified_db.items():
        with open(f"{folder}/{k}_tweetsumm_modified.jsonl", 'w') as f:
            for item in v:
                f.write(json.dumps(item) + "\n")
            
    modified_db = []

    for i in range(len(dataset["train"])):

        example = generate_text(dataset["train"][i])
        modified_db.append({"prompt": f"Please provide a short and concise summary of the conversation below that includes a summary of both the  user and the agent:\n {example['document']}", "completion": f"{example['summary']}"})

    with open(f"{folder}/bedrock_train_tweetsumm.jsonl", 'w') as f:
        for sample in modified_db:
                f.write(json.dumps(sample) + "\n")
    
    print(f"Train set size: {len(modified_db)}")
    print(f"Created training set file that can be used for Bedrock finetuning under the folder: {folder}/bedrock_train_tweetsumm.jsonl")
    
    test_file_path = f"{folder}/test_tweetsumm_modified.jsonl"
    return test_file_path