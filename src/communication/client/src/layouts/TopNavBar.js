import React, {Component} from "react";
import PropTypes from "prop-types";
import {
    MDBCol,
    MDBCollapse,
    MDBContainer,
    MDBIcon,
    MDBNavbar,
    MDBNavbarBrand,
    MDBNavbarNav,
    MDBNavbarToggler,
    MDBNavItem,
    MDBNavLink,
    MDBRow,
    MDBTooltip,
} from "mdbreact";
import axios from "axios";


class TopNavBar extends Component {

    state = {
        isOpen: false,
    };

    toggleCollapse = () => {
        this.setState({isOpen: !this.state.isOpen});
    };

    getName = () => {
        return this.props.getUserName.bind(this)();
    }
    logout = () => {
        let username = this.props.getUserName()
        axios
            .post("/logout", {
                user_id: this.props.getUserId(),
                user_name:username
            }).then((x) => {
            if (x.data === null) {
                x.data = {};
            }
            x.data['user_id'] = -1
            x.data['push_messages'] = []
            this.props.updateParent(x)
        })
    }

    itemsByLoginStatus = () => {
        const loggedIn = this.props.isLoggedIn.bind(this)()
        const isAdmin = this.props.isAdmin.bind(this)()
        if (loggedIn) {
            return <React.Fragment>
                <MDBNavItem>
                    <MDBNavLink disabled to="/">{`Hello ${this.getName()}`}</MDBNavLink>
                </MDBNavItem>
                <MDBNavItem>
                    <MDBNavLink onClick={() => this.logout()} to="/">Logout</MDBNavLink>
                </MDBNavItem>
                {isAdmin ? <MDBNavItem active> <MDBTooltip placement="top">
                    <MDBNavLink to="/admin_page"> <MDBIcon icon="tools"/></MDBNavLink>
                    <div>Admin Page</div>
                </MDBTooltip></MDBNavItem> : <div/>}
            </React.Fragment>
        } else {
            return <React.Fragment> <MDBNavItem>
                <MDBNavLink to="/registration_page">Register</MDBNavLink>
            </MDBNavItem>
                <MDBNavItem>
                    <MDBNavLink to="/login_page">Login</MDBNavLink>
                </MDBNavItem></React.Fragment>
        }
    }
    render() {
        return (
            <MDBContainer fluid>
                <MDBRow>
                    <MDBCol>
                        <MDBNavbar color="default-color" dark expand="md">
                            <MDBNavbarBrand tag="a" href="/">
                                <strong className="white-text h2">MegaBuyMarket</strong>
                            </MDBNavbarBrand>
                            <MDBNavbarToggler onClick={this.toggleCollapse}/>
                            <MDBCollapse id="navbarCollapse3" isOpen={this.state.isOpen} navbar>
                                <MDBNavbarNav right>
                                    <MDBNavItem active>
                                        <MDBTooltip placement="top">
                                            <MDBNavLink to="/watch_shopping_cart"> <MDBIcon
                                                icon="shopping-cart"/></MDBNavLink>
                                            <div>Shopping cart</div>
                                        </MDBTooltip>
                                    </MDBNavItem>
                                    {this.itemsByLoginStatus()}
                                    {/*<MDBNavItem>*/}
                                    {/*    <MDBTooltip placement="top">*/}
                                    {/*        <MDBNavLink to="/about"><MDBIcon far icon="question-circle"/></MDBNavLink>*/}
                                    {/*        <div>About</div>*/}
                                    {/*    </MDBTooltip>*/}
                                    {/*</MDBNavItem>*/}
                                </MDBNavbarNav>
                            </MDBCollapse>
                        </MDBNavbar>
                    </MDBCol>
                </MDBRow>
                <MDBRow>
                    <MDBCol>
                        <MDBNavbar color="orange" dark expand="md">
                        </MDBNavbar>
                    </MDBCol>
                </MDBRow>
            </MDBContainer>


        );
    }
}

// PropTypes
TopNavBar.propTypes = {
    isLoggedIn: PropTypes.func.isRequired,
    isAdmin: PropTypes.func.isRequired,
    getUserName: PropTypes.func.isRequired,
};

export default TopNavBar;