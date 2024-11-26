import React from 'react';
import Header from '../header/Header';

function Base({ title = 'Cruise-literature', children }) {
    return (
        <html lang="en">
        <link rel="stylesheet" href="style.css" />
            <head>
                <meta charSet="utf-8" />
                <title>{title}</title>
                <meta name="description" content="" />
                <link rel="shortcut icon" type="image/x-icon" href="favicon.ico" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <link
                    rel="stylesheet"
                    href="https://cdn.jsdelivr.net/npm/bulma@0.9.3/css/bulma.min.css"
                />
                <link rel="stylesheet" type="text/css" href="/static/css/style.css" />
                <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
                <script src="sort-paginate-table.js"></script>
                <script src="modal.js"></script>
            </head>
            <body>
                <Header />
            </body>
        </html>
    );
};

export default Base;
