import React, {Component} from "react";
import {MDBBtn, MDBCol, MDBContainer, MDBInput, MDBRow} from 'mdbreact';
import PropTypes from "prop-types";
import FormUtils from "../FormUtils";
import axios from "axios";
import * as HttpStatus from "http-status-codes"
import {Redirect, withRouter} from "react-router-dom";


export class RemoveStoreOwner extends Component {
    state = {
        username: "",
        errors: FormUtils.defaultUsernameDictionary(),
        been_submitted: false,
        msg: "",
        redirectAfterDeletion: null
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
            axios.post(
                `/delete_owner_from_store`,
                {
                    user_id: this.props.getUserId(),
                    removed_username: this.state.username,
                    store_name: this.props.match.params.storename
                },
            )
                .then((res) => {
                    this.dealWithDeleteResult(res);
                }).catch(error => {
                console.log(error)
                this.dealWithDeleteResult(error.response);
            });
        }
    }

    dealWithDeleteResult = (res) => {
        if(res){
            console.log(res)
        if (res.status === HttpStatus.OK) {
            // delete successful
            this.setState({redirectAfterDeletion: `/`})
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
        if (this.state.redirectAfterDeletion) {
            return <Redirect to={this.state.redirectAfterDeletion}/>
        } else {
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
                                    <p onChange={this.onChange} className="h3 text-center mb-4">Remove owner</p>
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
                                                color="danger">Remove</MDBBtn>
                                    </div>
                                </form>
                                <p onChange={this.onChange}
                                   className="h3 text-center mb-4 text-danger">{this.state.msg}</p>
                            </MDBCol>
                        </MDBRow>
                    </MDBContainer>
                </React.Fragment>
            );
        }
    }
}

// PropTypes
RemoveStoreOwner.propTypes = {
    isLoggedIn: PropTypes.func.isRequired,
    isAdmin: PropTypes.func.isRequired,
    updateParent: PropTypes.func.isRequired,
    getUserName: PropTypes.func.isRequired,

};
export default withRouter(RemoveStoreOwner)