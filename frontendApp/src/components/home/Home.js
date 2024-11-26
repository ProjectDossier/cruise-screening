import React from 'react'
import Base from '../base/Base'
import Footer from '../footer/Footer';

function Home({ searchQuery }) {
    return (
        <>
            <link rel="stylesheet" href="style.css" />
            <Base />
            <div class="search-box">
                <img src="cruise-logo.png" class="search-box__logo" width="300" height="300" />

                <form id="search_box" method="" action="">{/* TODO */}
                    <div class="search-box__input">
                        <input type="search" class="input mr-2" name="search_query" value={searchQuery}
                            placeholder="Search CRUISE" aria-label="Search" />
                        <button class="button is-primary">Search</button>
                    </div>
                    <input type='hidden' name='source' value="main_search" />
                </form>
            </div>
            <Footer />
        </>
    );
}

export default Home;
