import React from 'react'
import Base from '../base/Base'

function Home({ searchQuery }) {
    return (
        <Base>
            <div className="search-box">
                <img src="cruise-logo.png" className="search-box__logo" width="300" height="300" />

                <form id="search_box" method="" action="">{/* TODO */}
                    <div className="search-box__input">
                        <input type="search" className="input mr-2" name="search_query" value={searchQuery}
                            placeholder="Search CRUISE" aria-label="Search" />
                        <button className="button is-primary">Search</button>
                    </div>
                    <input type='hidden' name='source' value="main_search" />
                </form>
            </div>
        </Base>
    );
}

export default Home;
