import React, {Component} from "react";
import PropTypes from "prop-types";
import {MDBNav, MDBNavItem, MDBNavLink} from "mdbreact";

export class ToolNavBar extends Component {

    loggedInLinks = () => {
        let result = this.props.isLoggedIn.bind(this)()
        if (result) {
            return (<React.Fragment>
                <MDBNavItem className="mx-auto">
                    <MDBNavLink style={text_color} to="/new_store">New store</MDBNavLink>
                </MDBNavItem>
                <MDBNavItem className="mx-auto">
                    <MDBNavLink style={text_color} to="/my_stores">My Stores</MDBNavLink>
                </MDBNavItem>
                <MDBNavItem className="mx-auto">
                    <MDBNavLink style={text_color} to="/personal_purchase_history">Purchases History</MDBNavLink>
                </MDBNavItem>
            </React.Fragment>);
        } else {
            return <div/>
        }
    }

    render() {
        // tool bar for logged in users
        return (
            <MDBNav color='default-color' style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
            }}>

                <MDBNavItem className="mx-auto">
                    <MDBNavLink style={text_color} active to="/">Home</MDBNavLink>
                </MDBNavItem>
                <MDBNavItem className="mx-auto">
                    <MDBNavLink style={text_color} to="/search_products_info">Search Products</MDBNavLink>
                </MDBNavItem>
                <MDBNavItem className="mx-auto">
                    <MDBNavLink style={text_color} to="/search_stores">Search Stores</MDBNavLink>
                </MDBNavItem>
                {this.loggedInLinks()}
                {/*<MDBNavItem className="mx-auto">*/}
                {/*    <MDBNavLink style={text_color} to="/contact_us">Contact Us</MDBNavLink>*/}
                {/*</MDBNavItem>*/}
                {/*<MDBNavItem className="mx-auto">*/}
                {/*    <MDBNavLink style={text_color} to="/about">About</MDBNavLink>*/}
                {/*</MDBNavItem>*/}
            </MDBNav>
        );
    }
}


// PropTypes
ToolNavBar.propTypes = {
    isLoggedIn: PropTypes.func.isRequired,
    isAdmin: PropTypes.func.isRequired,
};

const text_color = {
    color: "white"
}

export default ToolNavBar;
