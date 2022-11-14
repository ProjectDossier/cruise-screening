import time

import openai
import os
from typing import Dict, List, Tuple
from sklearn.metrics import accuracy_score
import random

CURRENT_FILE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
api_key_file = f"{CURRENT_FILE_DIRECTORY}/../../../../data/open_ai_api_key.txt"

with open(api_key_file, "r") as apikey_file:
    api_key = apikey_file.readlines()[0].strip()
    if api_key == "ADD_YOUR_OPEN_AI_API_KEY_HERE":
        raise ValueError(
            f"You need to update Open AI API key in {api_key_file} in order to use GPT-3"
        )

openai.api_key = api_key


def postprocess_response(response: str) -> str:
    """
    Postprocess the response from GPT-3 to make it more human-readable.
    :param response:
    :return:
    """
    original = response
    # response = response.split("\n")[1]
    response = response.strip()
    response = response.strip('.').strip()

    if response.lower() not in ["yes", "no", "not sure"]:
        if '.' in response:
            response = response.split('.')[0]
        if ',' in response:
            response = response.split(',')[0]

    print(f"{original}, {response}")
    return response.lower()


def classify_paper(paper: Dict[str, str],
                   criteria: List[str],
                   gpt_model="text-davinci-002") -> Tuple[List[str], str]:
    """
    Classify a paper using GPT-3, write a prompt for every criteria in the list for yes/no questions.
    :param paper:
    :param criteria:
    :return:
    """
    prompt = "You are conducting a literature review of neural retrieval models for domain specific tasks.\n"
    # prompt = ""

    prompt += f"Title: {paper.get('title')}\n"
    prompt += f"Abstract: {paper.get('abstract')}\n"
    # prompt += f"Keywords: {paper.get('keywords')}\n"
    prompt += f"Authors: {paper.get('authors')}\n"
    prompt += f"Journal: {paper.get('venue')}\n"
    prompt += f"Year: {paper.get('year')}\n"
    # prompt += f"DOI: {paper.get('Doi')}\n"
    # prompt += f"URL: {paper.get('url')}\n"
    # prompt += f"PDF: {paper.get('pdf')}\n"

    # print(prompt)
    responses = []
    for criterion in criteria:
        prompt_template = f"{prompt}\n\nDoes the paper {criterion}? (yes/no/not sure)"
        # prompt_template += "Please answer 'Yes', 'No' or 'Not sure'.\n"

        try:
            response = openai.Completion.create(
                engine=gpt_model,
                prompt=prompt_template,
                temperature=0.9,
                max_tokens=150,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0.6,
                # stop=["\n", "Title:", "Abstract:", "Keywords:", "Authors:", "Journal:", "Year:", "DOI:", "URL:", "PDF:",
                #       "Source:", "Source ID:", "Source URL:", "Source PDF:", "Source DOI:", "Source Title:",
                #       "Source Authors:", "Source Year:", "Source Journal:"]
            )
        except openai.error.RateLimitError:
            # print('waiting')
            time.sleep(62)
            response = openai.Completion.create(
                engine=gpt_model,
                prompt=prompt_template,
                temperature=0.9,
                max_tokens=150,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0.6,
                # stop=["\n", "Title:", "Abstract:", "Keywords:", "Authors:", "Journal:", "Year:", "DOI:", "URL:", "PDF:",
                #       "Source:", "Source ID:", "Source URL:", "Source PDF:", "Source DOI:", "Source Title:",
                #       "Source Authors:", "Source Year:", "Source Journal:"]
            )

        # print(prompt_template)
        try:
            output = postprocess_response(response=response["choices"][0]["text"])
            responses.append(output)
        except IndexError:
            responses.append("not sure")

        # responses.append(random.choices(["Yes", "No", "Not sure"])[0])
    return responses


if __name__ == '__main__':

    papers = [
        {
            "title": "A new approach to the problem of the determination of the structure of the universe",
            "abstract": "In a complete theory there is an element corresponding to each element of reality. A sufficient condition for the reality of a physical quantity is the possibility of predicting it with certainty, without disturbing the system. In quantum mechanics in the case of two physical quantities described by non-commuting operators, the knowledge of one precludes the knowledge of the other. Then either (1) the description of reality given by the wave function in quantum mechanics is not complete or (2) these two quantities cannot have simultaneous reality. Consideration of the problem of making predictions concerning a system on the basis of measurements made on another system that had previously interacted with it leads to the result that if (1) is false then (2) is also false. One is thus led to conclude that the description of reality as given by a wave function is not complete.",
            "authors": "Einstein, A.",
            "venue": "Annalen der Physik",
            "year": "1917",
        },
        {
            "title": "Big Data technologies and extreme-scale analytics Multimodal Extreme Scale Data Analytics for Smart Cities Environments D 2 . 1 : Collection and Analysis of Experimental Data",
            "abstract": "D2.1: Collection and Analysis of Experimental Data† Abstract: Project MARVEL will create and publicly share with the academics, industrial community, and smart cities, a data pool of experimental multimodal audio-visual data and will showcase the use of the data and its processing across various pilots. This report documents the process for the collection and analysis of the experimental data. The use cases and AI tasks required to process the audio-visual data and enable the implementation of the pilots are first described. This knowledge determines how and where the audio-visual data is collected and annotated. The various devices, namely microphones and cameras, and their deployment are described next, followed by software tools that will be used in the data annotation task, that will be carried out according to what is required for training the AI models. The data is analysed to determine which parts constitute personal data, followed by a discussion on the appropriate data anonymisation techniques, which should ensure the sharing of GDPR compliant data. In addition, the data value chains are defined, including the data owner and access rights at each processing stage. The proposed datasets and AI models are matched and compared to the use cases and any gaps are identified. The volume and velocity at which data is collected and moved from one network layer to another are estimated from the technical specifications of the devices as well as from the expected output of the processing stages. These estimates enable the initial planning of the MARVEL framework, which promises a solution to collect and process big data of high volume and high variety while optimising both flow and processing at any appropriate point of the edge-fog-cloud infrastructure, typical of a smart city.",
            "authors": "M. Marazakis",
            "venue": "No journal information",
            "year": "2021",
        },
        {
            "title": "Zero-shot Neural Passage Retrieval via Domain-targeted Synthetic Question Generation",
            "abstract": "A major obstacle to the wide-spread adoption of neural retrieval models is that they require large supervised training sets to surpass traditional term-based techniques, which are constructed from raw corpora. In this paper, we propose an approach to zero-shot learning for passage retrieval that uses synthetic question generation to close this gap. The question generation system is trained on general domain data, but is applied to documents in the targeted domain. This allows us to create arbitrarily large, yet noisy, question-passage relevance pairs that are domain specific. Furthermore, when this is coupled with a simple hybrid term-neural model, first-stage retrieval performance can be improved further. Empirically, we show that this is an effective strategy for building neural passage retrieval models in the absence of large training corpora. Depending on the domain, this technique can even approach the accuracy of supervised models",
            "authors": "Ji Ma, I. Korotkov, Yinfei Yang, K. Hall, Ryan T. McDonald",
            "venue": "EACL",
            "year": "2021",
        },
        {
            "title": "An Ensemble of Bayesian Neural Networks for Exoplanetary Atmospheric Retrieval",
            "abstract": "Machine learning (ML) is now used in many areas of astrophysics, from detecting exoplanets in Kepler transit signals to removing telescope systematics. Recent work demonstrated the potential of using ML algorithms for atmospheric retrieval by implementing a random forest (RF) to perform retrievals in seconds that are consistent with the traditional, computationally expensive nested-sampling retrieval method. We expand upon their approach by presenting a new ML model, plan-net, based on an ensemble of Bayesian neural networks (BNNs) that yields more accurate inferences than the RF for the same data set of synthetic transmission spectra. We demonstrate that an ensemble provides greater accuracy and more robust uncertainties than a single model. In addition to being the first to use BNNs for atmospheric retrieval, we also introduce a new loss function for BNNs that learns correlations between the model outputs. Importantly, we show that designing ML models to explicitly incorporate domain-specific knowledge both improves performance and provides additional insight by inferring the covariance of the retrieved atmospheric parameters. We apply plan-net to the Hubble Space Telescope Wide Field Camera 3 transmission spectrum for WASP-12b and retrieve an isothermal temperature and water abundance consistent with the literature. We highlight that our method is flexible and can be expanded to higher-resolution spectra and a larger number of atmospheric parameters",
            "authors": "Adam D. Cobb, M. D. Himes, Frank Soboczenski, Simone Zorzan, M. O'Beirne, A. G. Baydin, Y. Gal, S. Domagal‐Goldman, G. Arney, D. Angerhausen",
            "venue": "The Astronomical Journal",
            "year": "2019",
        }
    ]

    criteria = [
        "is about neural retrieval model",
        "is about the problem of the determination of the structure of the universe",
        "is older than 2014",
        "is not about domain specific search",
        "is about domain specific search",
        "is about statistical models applied to manufacturing process",
        "is about physics",
    ]

    y_true = [
        ['No', 'Yes', 'Yes', 'Yes', 'No', 'No', 'Yes'],
        ['No', 'No', 'No', 'Yes', 'No', 'Not sure', 'No'],
        ['Yes', 'No', 'No', 'No', 'Yes', 'No', 'No'],
        ['Yes', 'No', 'No', 'No', 'Yes', 'No', 'Yes']
    ]

    grand_avg = 0
    small_avg = [
        0,
        0,
        0,
        0
    ]
    iters = 100000

    for _ in range(iters):
        y_pred = []
        for paper in papers:
            result = classify_paper(paper=paper,
                                    criteria=criteria)
            # print(result)
            y_pred.append(result)


        avg_acc = 0
        for index_i in range(len(y_true)):
            acc = accuracy_score(y_true=y_true[index_i], y_pred=y_pred[index_i])
            # print(f"Accuracy for paper {index_i}: {acc}")
            avg_acc += acc
            small_avg[index_i] += acc

        avg_acc /= len(y_true)
        # print(f"Average accuracy: {avg_acc}")

        grand_avg += avg_acc

    print((grand_avg / iters))
    print([x/iters for x in  small_avg])