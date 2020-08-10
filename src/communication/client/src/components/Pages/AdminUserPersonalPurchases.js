import React, {Component} from "react";
import {MDBBtn, MDBCol, MDBContainer, MDBInput, MDBRow} from 'mdbreact';
import PropTypes from "prop-types";
import FormUtils from "../FormUtils";
import axios from "axios";
import * as HttpStatus from "http-status-codes"
import {Redirect} from "react-router-dom";
import PurchaseTable from "../PurchaseTable";
import OnlyHeaderComponent from "../OnlyHeaderComponent";


export class AdminUserPersonalPurchases extends Component {
    state = {
        username: "",
        errors: FormUtils.defaultUsernameDictionary(),
        been_submitted: false,
        msg: "",
        purchases: []
    };
    formUtils = new FormUtils();

    validateUsername = () => this.formUtils.validate_username(this.state.username, this.state.errors);

    onChange = (e) => {
        this.setState({[e.target.name]: e.target.value});
    }
    clearErrors = () => {
        this.setState({errors: FormUtils.defaultUsernameDictionary()})
    }
    sendIfPossible = () => {
        if (this.state.errors["is_valid"]) {
            axios.get(
                `/fetch_user_purchases_as_admin/${this.props.getUserId()}/${this.state.username}`
            )
                .then((res) => {
                    console.log(res)
                    this.dealWithSearchResult(res);
                }).catch(error => {
                console.log(error)
                this.dealWithSearchResult(error.response);
            });
        }
    }

    dealWithSearchResult = (res) => {
        if(res){
            if (res.status === HttpStatus.CREATED || res.status === HttpStatus.OK) {
                this.setState({msg: "", purchases: res.data !== null && 'purchases' in res.data ? res.data.purchases : []})
            } else {
                this.setState({msg: this.convertErrorToMessage(res.data["error"])})
            }
        }
    };

    convertErrorToMessage = (msg) => {
        if (msg) {
            msg = msg.split("|").join(", ");
            msg = msg.split("_").join(" ");
            return msg;
        }
    }


    onSubmit = (e) => {
        e.preventDefault();
        this.clearErrors();
        let new_errors = this.formUtils.validate_new_store_manager(this.state.username);
        this.setState({
                been_submitted: true,
                errors: new_errors
            },
            this.sendIfPossible);

    }

    render() {
        if (this.props.isAdmin.bind(this)() && this.props.isLoggedIn.bind(this)()) {
            return (
                <React.Fragment>
                    <MDBContainer style={{padding: "10px"}}>
                        <MDBRow
                            style={{
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                            }}>
                            <MDBCol md="6">
                                <form className="needs-validation" onSubmit={this.onSubmit} noValidate>
                                    <p onChange={this.onChange} className="h3 text-center mb-4">Search User</p>
                                    <div className="grey-text">
                                        <div className="form-group">
                                            <MDBInput onChange={this.onChange} value={this.state.username}
                                                      name="username"
                                                      label="Username" icon="user" group type="text"
                                                      id="defaultFormRegisterNameEx"
                                                      className={this.state.been_submitted ? (this.validateUsername() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                                      required
                                                      error="wrong"
                                                      success="right"/>
                                            <div className="invalid-feedback"
                                                 style={{display: "block"}}>{this.state.errors["username"]}</div>
                                            <div className="valid-feedback"/>
                                        </div>
                                    </div>
                                    <div className="text-center">
                                        <MDBBtn type="submit"
                                                value="Submit"
                                                outline
                                                color="info">Search</MDBBtn>
                                    </div>
                                </form>
                                <p onChange={this.onChange}
                                   className="h3 text-center mb-4 text-danger">{this.state.msg}</p>
                            </MDBCol>
                        </MDBRow>
                        <MDBRow>
                            <PurchaseTable purchases={this.state.purchases}/>
                        </MDBRow>
                    </MDBContainer>
                </React.Fragment>
            );


        } else {
            return <OnlyHeaderComponent header={"Only Admins Are Allowed here"}/>
        }
    }
}

// PropTypes
AdminUserPersonalPurchases.propTypes = {
    isLoggedIn: PropTypes.func.isRequired,
    isAdmin: PropTypes.func.isRequired,
    updateParent: PropTypes.func.isRequired,
    getUserName: PropTypes.func.isRequired,
};

export default AdminUserPersonalPurchases;

