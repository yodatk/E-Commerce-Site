import React, {Component} from "react";
import PropTypes from "prop-types";
import {MDBNav, MDBNavItem, MDBNavLink} from "mdbreact";

export class SearchByCategoryBox extends Component {
    render() {
        return (
            <React.Fragment>
                <MDBNav className="flex-column" color="orange">
                    <MDBNavLink disabled active to="/" className="h5" style={text_color}>Search By
                        Category</MDBNavLink>
                    <MDBNavItem>
                        <MDBNavLink style={text_color} active to="/">Toys</MDBNavLink>
                    </MDBNavItem>
                    <MDBNavItem>
                        <MDBNavLink style={text_color} to="/">Food</MDBNavLink>
                    </MDBNavItem>
                    <MDBNavItem>
                        <MDBNavLink style={text_color} to="/">Clothing</MDBNavLink>
                    </MDBNavItem>
                    <MDBNavItem>
                        <MDBNavLink style={text_color} to="/">Furniture</MDBNavLink>
                    </MDBNavItem>
                    <MDBNavItem>
                        <MDBNavLink style={text_color} to="/">Electronics</MDBNavLink>
                    </MDBNavItem>
                </MDBNav>
            </React.Fragment>
        );
    }
}

const text_color = {
    color: "white"
}

// PropTypes
SearchByCategoryBox.propTypes = {
    isLoggedIn: PropTypes.func.isRequired,
    isAdmin: PropTypes.func.isRequired,
};


export default SearchByCategoryBox;
