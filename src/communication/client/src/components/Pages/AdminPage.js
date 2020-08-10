import React, {Component} from "react";
import {
    MDBBtn,
    MDBBtnGroup,
    MDBCard,
    MDBCardBody,
    MDBCardFooter,
    MDBCardHeader,
    MDBCardText,
    MDBCardTitle,
    MDBCol,
    MDBContainer, MDBLink,
    MDBRow
} from "mdbreact";
import {withRouter, Link, Redirect} from "react-router-dom"
import axios from "axios";
import * as HttpStatus from "http-status-codes";
import PropTypes from "prop-types";
import RegisterPage from "./RegisterPage";
import OnlyHeaderComponent from "../OnlyHeaderComponent";


export class AdminPage extends Component {

    state = {}


    render() {
        if (this.props.isAdmin.bind(this)() && this.props.isLoggedIn.bind(this)()) {

            const watch_all_purchase_history =
                <Link style={{'color': 'white'}}
                      to={'/admin_watch_all_purchases/'}><MDBBtn color="grey darken-1">All Purchases</MDBBtn></Link>

            const watch_purchase_of_store =
                <Link style={{'color': 'white'}}
                      to={'/admin_store_purchase_history/'}><MDBBtn color="grey darken-2">Store Purchases
                </MDBBtn> </Link>

            const watch_user_purchase_history =
                <Link style={{'color': 'white'}}
                      to={'/admin_watch_user_purchase_history/'}><MDBBtn color="grey darken-3">User
                    Purchases</MDBBtn></Link>

            const add_admin =
                <Link style={{'color': 'white'}}
                      to={'/add_admin'}><MDBBtn color="grey darken-3">Add Admin
                </MDBBtn></Link>

            const view_stats =
                <Link style={{'color': 'white'}}
                      to={'/system_admin_stats'}><MDBBtn color="grey darken-3">View Statistics
                </MDBBtn></Link>

            return (
                <MDBContainer>
                    <MDBCol size={12}>
                        <MDBCard>
                            <MDBCardHeader color="orange" tag="h3">
                                Admin Page
                            </MDBCardHeader>
                            <MDBCardBody>
                                <MDBCardTitle>Choose an Action</MDBCardTitle>
                                <MDBCardText>
                                    ...
                                </MDBCardText>
                                <MDBRow>
                                    <MDBCol md='8' className="mb-4">
                                        <MDBBtnGroup size="lg">
                                            {watch_all_purchase_history}
                                            {watch_purchase_of_store}
                                            {watch_user_purchase_history}
                                            {add_admin}
                                            {view_stats}
                                        </MDBBtnGroup>
                                    </MDBCol>
                                </MDBRow>
                                <MDBCardFooter tag="h5">
                                    MegaBuyMarket
                                </MDBCardFooter>
                            </MDBCardBody>
                        </MDBCard>
                    </MDBCol>
                </MDBContainer>
            );
        } else {
            return (
                <OnlyHeaderComponent header="This Page is For Admins Only"/>
            );
        }

    }
}

// PropTypes
AdminPage.propTypes = {
    isLoggedIn: PropTypes.func.isRequired,
    isAdmin: PropTypes.func.isRequired,
    updateParent: PropTypes.func.isRequired,
    getUserName: PropTypes.func.isRequired,
};


export default withRouter(AdminPage);
