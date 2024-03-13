import json
def create_data_stats_view(test_file_path, result_img_folder):


    def get_doc_lengths(data):
        document_sentence_length, summary_sentence_length = [], []

        for d in data:
            # TODO switch to token counting instead of characters
            document_sentence_length.append(len(d['document'].replace("\n"," ").split()))
            summary_sentence_length.append(len(d['summary'].replace("\n"," ").split()))

        return document_sentence_length, summary_sentence_length


    def read_data(filename):
        data = []
        with open(filename, "r") as file:
            for line in file:
                data.append(json.loads(line))
        return data

    test_data = read_data(f"{test_file_path}")
    test_doc_lengths, test_sum_lengths = get_doc_lengths(test_data)

    import matplotlib.pyplot as plt
    import numpy as np

    fig, axs = plt.subplots(2)
    axs[0].hist(test_doc_lengths, density=False, bins=50)
    axs[0].set_title('Test documents length')
    axs[1].hist(test_sum_lengths, density=False, bins=50)
    axs[1].set_title('Test summary length')

    for ax in axs.flat:
        ax.set(xlabel='Num. of words', ylabel='Count')

    for ax in axs.flat:
        ax.label_outer()

    plt.savefig(f"{result_img_folder}/dataset_stats.png")