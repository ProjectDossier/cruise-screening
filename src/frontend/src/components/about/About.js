import React from 'react';
import Base from '../base/Base';

const description1 = "CRUISE is a collaborative project initiated by DoSSIER student researchers. As a part of CRUISE, this \
          search engine aims to help academics coming into a space understand how the concepts associated with a \
          specific field relate to each other and give them some structuring of the information space.";

const description2 = "DoSSIER is an EU Horizon 2020 ITN/ETN on Domain Specific Systems for Information Extraction and \
Retrieval. DoSSIER will elucidate, model, and address the different information needs of professional \
users."

const About = () => {
  return (
    <Base>
      <div className="max-w-3xl mx-auto p-6 bg-white border border-gray-200 rounded-lg shadow-lg my-12">
        <h1 className="text-3xl font-bold text-orange-600 text-center mb-8">About CRUISE</h1>
        <article className="text-gray-800 text-base leading-relaxed">
          <p className="flex justify-center mb-8">
            <img
              src="/cruise-logo.png"
              alt="Cruise Logo"
              className="w-48 h-48 object-contain"
            />
          </p>
          <div className="space-y-4">
            <p>{description1}</p>
            <p>{description2}</p>
            <p>
              <a
                href="https://dossier-project.eu/researchers.html"
                target="_blank"
                rel="noopener noreferrer"
                className="text-orange-600 font-semibold hover:underline"
              >
                Meet our team: PhD Students
              </a>
            </p>
            <p>
              <a
                href="https://dossier-project.eu"
                target="_blank"
                rel="noopener noreferrer"
                className="text-orange-600 font-semibold hover:underline"
              >
                More about Project DoSSIER
              </a>
            </p>
            <p className="text-sm text-gray-500">Version: 0.6.0 (23 January 2023)</p>
          </div>
          <p className="flex justify-center mt-8">
            <a
              href="mailto:Wojciech.Kusa@tuwien.ac.at"
              className="bg-orange-600 text-white px-4 py-2 rounded-md hover:bg-orange-700 transition"
            >
              Contact
            </a>
          </p>
        </article>
      </div>
    </Base>
  );
};


export default About;