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


export class StorePage extends Component {

    state = {}


    componentDidMount() {

        axios.get(
            "/fetch_store_personal_view/" + this.props.match.params.storename)
            .then((res) => {
                if (res.data !== null) {
                    this.setState(res.data)
                }
            }).catch(error => {
            console.log(error)
        });
    }

    /*
    *
*                         'can_manage_inventory': perm.can_manage_inventory,
                        'can_appoint_new_store_owner': perm.appoint_new_store_owner,
                        'can_watch_purchase_history': perm.watch_purchase_history,
                        'can_open_close_store': perm.open_and_close_store,
                        'can_appoint_new_store_manager': perm.appoint_new_store_manager,
                        'can_manage_discount': perm.can_manage_discount
    * */

    close_store = () => {
        if (window.confirm("Are you sure?")) {
            console.log('Say yes');
            axios.post(
                "/close_store",
                {
                    user_id: this.props.getUserId(),
                    store_name: this.props.match.params.storename
                },
            )
                .then((res) => {
                    console.log('Store closed', res);
                    this.dealWithCloseStoreResult(res);
                }).catch(error => {
                console.log(error);
                this.dealWithCloseStoreResult(error.response);
            });
        } else {
            console.log('Say no')
        }
    };

    open_store = () => {
        if (window.confirm("Are you sure?")) {
            console.log('Say yes');
            axios.post(
                "/open_store",
                {
                    user_id: this.props.getUserId(),
                    store_name: this.props.match.params.storename
                },
            )
                .then((res) => {
                    console.log('Store Open', res);
                    this.dealWithCloseStoreResult(res);
                }).catch(error => {
                console.log(error);
                this.dealWithCloseStoreResult(error.response);
            });
        } else {
            console.log('Say no')
        }
    };

    dealWithCloseStoreResult = (res) => {
        if (res) {
            if (res.status === HttpStatus.OK) {
                console.log('arrived here');
                this.props.history.push('/my_stores/');
            } else {
                this.setState({msg: this.convertErrorToMessage(res.data["error"])})
            }
        }
    };

    render() {
        let open_btn = null;
        let close_btn = null;
        let add_owner = null;
        let add_manager = null;
        let manage_inventory = null;
        let manage_discounts = null;
        let awaiting_approvals = null;
        let compose_discounts = null;
        let remove_manager = null;
        let remove_owner = null;
        let edit_staff = null;
        let watch_purchase_history = null;
        let manage_policies = null
        let compose_policies = null;
        let store_name = this.props.match.params.storename;
        if (this.state && this.state.permissions) {
            close_btn = this.state.permissions.can_open_close_store ?
                <MDBBtn color="danger" disabled={!this.state.open} onClick={this.close_store}>Close store</MDBBtn> : "";
            open_btn = this.state.permissions.can_open_close_store ?
                <MDBBtn color="success" disabled={this.state.open} onClick={this.open_store}>Open store</MDBBtn> : "";
            add_owner = this.state.permissions.can_appoint_new_store_owner ?
                <Link
                    to={'/new_store_owner/' + store_name}>
                    <MDBBtn style={{'color': 'white'}} color="primary">Add Owner</MDBBtn>
                </Link>
                : "";

            remove_owner =
                <Link
                    to={"/remove_store_owner/" + store_name}><MDBBtn style={{'color': 'white'}} color="danger">Remove
                    Owner</MDBBtn></Link>

            add_manager = this.state.permissions.can_appoint_new_store_manager ?
                <Link
                    to={'/new_store_manager/' + store_name}><MDBBtn style={{'color': 'white'}} color="primary">Add
                    Manager</MDBBtn></Link>
                : "";

            awaiting_approvals = this.state.permissions.can_appoint_new_store_owner ?
                <Link
                    to={"/fetch_awaiting_approvals/" + store_name}><MDBBtn style={{'color': 'white'}} color="success">Awaiting
                    approvals</MDBBtn></Link> : "";

            remove_manager =
                <Link
                    to={"/remove_store_manager/" + store_name}><MDBBtn style={{'color': 'white'}} color="danger">Remove
                    Manager</MDBBtn></Link>


            manage_inventory = this.state.permissions.can_manage_inventory ?

                <Link
                    to={'/manage_inventory/' + store_name}><MDBBtn style={{'color': 'white'}} color="warning">Manage
                    Inventory</MDBBtn></Link> : "";

            manage_discounts = this.state.permissions.can_manage_discount ?


                <Link
                    to={"/manage_discounts/" + store_name}><MDBBtn style={{'color': 'white'}} color="orange">Manage
                    Discounts</MDBBtn></Link> : "";

            compose_discounts = this.state.permissions.can_manage_discount ?
                <Link
                    to={"/compose_discounts/" + store_name}><MDBBtn style={{'color': 'white'}} color="orange">Compose
                    Discounts</MDBBtn></Link> : "";

            edit_staff =
                <Link
                    to={"/my_sub_staff/" + store_name}><MDBBtn style={{'color': 'white'}} color="primary">Edit
                    Staff</MDBBtn></Link>

            watch_purchase_history = this.state.permissions.can_watch_purchase_history ?

                <Link
                    to={'/store_purchase_history/' + store_name}><MDBBtn style={{'color': 'white'}}
                                                                         color="grey darken-2">Purchase
                    History</MDBBtn></Link>
                : "";
            manage_policies = this.state.permissions.can_manage_discount ?

                <Link
                    to={'/manage_policies/' + store_name}><MDBBtn style={{'color': 'white'}}
                                                                  color="deep-orange">Manage
                    Policies</MDBBtn></Link>
                : "";
            compose_policies = this.state.permissions.can_manage_discount ?
                <Link
                    to={"/compose_policies/" + store_name}><MDBBtn style={{'color': 'white'}} color="deep-orange">
                    Compose Policies</MDBBtn></Link> : "";
        }

        return (
            <MDBContainer>
                <MDBCol size={12}>
                    <MDBCard>
                        <MDBCardHeader color="primary-color" tag="h3">
                            {this.props.match.params.storename}
                        </MDBCardHeader>
                        <MDBCardBody>
                            <MDBCardTitle>Opened by: {this.state.initial_owner}</MDBCardTitle>
                            <MDBRow>
                                <MDBCol md='8' className="mb-4">
                                    <MDBBtnGroup size="sm">
                                        {add_owner}
                                        {add_manager}
                                        {edit_staff}
                                        {awaiting_approvals}
                                        {remove_manager}
                                        {remove_owner}
                                    </MDBBtnGroup>
                                </MDBCol>
                            </MDBRow>
                            <MDBRow>
                                <MDBCol md='8' className="mb-4">
                                    <MDBBtnGroup size="sm">
                                        {manage_inventory}
                                        {manage_discounts}
                                        {compose_discounts}
                                        {manage_policies}
                                        {compose_policies}
                                    </MDBBtnGroup>
                                </MDBCol>
                            </MDBRow>
                            <MDBRow>
                                <MDBCol md='8' className="mb-4">
                                    <MDBBtnGroup size="sm">
                                        {watch_purchase_history}
                                    </MDBBtnGroup>
                                </MDBCol>
                            </MDBRow>

                            <MDBRow>
                                <MDBCol style={{padding: "3px"}} size="2">
                                    {open_btn}
                                </MDBCol>
                                <MDBCol style={{padding: "3px"}} size="2">
                                    {close_btn}
                                </MDBCol>
                            </MDBRow>
                            <MDBCardFooter>
                                Created at({this.state.creation_date}), Status({this.state.open ? 'Open' : 'Closed'})
                            </MDBCardFooter>
                        </MDBCardBody>
                    </MDBCard>
                </MDBCol>
            </MDBContainer>
        );
    }
}

export default withRouter(StorePage);