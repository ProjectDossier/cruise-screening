import React from 'react';
import Base from '../base/Base';

const faqData = [
    {
        question: "What is CRUISE?",
        answer: "CRUISE is a collaborative project initiated by student researchers from the DoSSIER Project. As a part of CRUISE, this search engine aims to help academics searching for a literature on a specific topic find the relevant items faster."
    },
    {
        question: "What is the purpose of CRUISE?",
        answer: "CRUISE aims to provide a comprehensive and up-to-date overview of the research landscape of a given field by combining data from multiple sources. We provide a meta search engine that allows for the exploration of relevant publications to create a literature review. We apply some automation techniques to speed up the process of finding relevant publications."
    },
    {
        question: "Who is behind CRUISE?",
        answer: "CRUISE is a collaborative project initiated by student researchers from the DoSSIER Project. The project is currently maintained by the DoSSIER team."
    },
    {
        question: "Is CRUISE open-source?",
        answer: "Yes! You can find the source code for the project on GitHub."
    },
    {
        question: "Do I need to register to use CRUISE?",
        answer: "Unregistered users can use the meta-search functionality. However, if you want to create a literature review, you need to create an account. It is free. You can also create the"
    },
    {
        question: "What are the limitations of CRUISE?",
        answer: "CRUISE is currently in the alpha version. It has several limitations related to its user interface and functionalities. We are working on improving the user interface and adding more data sources. Previous work has shown that large language models such as the ones used to generate automatic predictions in CRUISE, can generate realistic but inaccurate and unreliable output and even hallucinate. We tried to mitigate this issue by adding several filters to the output of the model. However, we cannot guarantee that the output of the model is always accurate. We are working on improving the model to make it more reliable."
    },
    {
        question: "How can I help?",
        answer: "CRUISE is a collaborative, open-source project, and we are always looking for people to help out. If you would like to contribute to the project, you can find more information on our About page."
    },
    {
        question: "Do you have some other questions?",
        answer: "If you have any other questions, please feel free to contact us at Wojciech.Kusa@tuwien.ac.at."
    }
];

function Faq() {
    return (
        <Base>
            <div className="max-w-3xl mx-auto p-6 bg-white border border-gray-200 rounded-lg shadow-lg my-12">
                <h1 className="text-3xl font-bold text-orange-600 text-center mb-8">Frequently Asked Questions</h1>
                
                {faqData.map((item, index) => (
                    <div key={index} className="mb-6">
                        <h2 className="text-xl font-semibold text-gray-800 border-l-4 pl-3 border-orange-600 mb-4">
                            {item.question}
                        </h2>
                        <p className="text-gray-600 text-base leading-relaxed">
                            {item.answer}
                        </p>
                    </div>
                ))}
            </div>
        </Base>
    );
}

export default Faq;
