import React, {Component} from "react";
import {MDBBtn, MDBCol, MDBContainer, MDBInput, MDBRow} from 'mdbreact';
import PropTypes from "prop-types";
import FormUtils from "../FormUtils";
import axios from "axios";
import * as HttpStatus from "http-status-codes";
import {Redirect} from "react-router-dom";

export class LoginPage extends Component {
    state = {
        username: "",
        pass1: "",
        errors: FormUtils.defaultLoginDictionary(),
        been_submitted: false,
        msg: "",
        redirectAfterLoggedIn: null,
    };
    formUtils = new FormUtils();
    validateUsername = () => this.formUtils.validate_username(this.state.username, this.state.errors);
    validatePassword = () => this.formUtils.validate_password(this.state.pass1, this.state.errors);
    onChange = (e) => {
        this.setState({[e.target.name]: e.target.value});
    }
    clearErrors = () => {
        this.setState({errors: FormUtils.defaultLoginDictionary()})
    }
    sendIfPossible = () => {
        // console.log(`${this.state.username}\n${this.state.pass1}\n`)
        // console.log(`ERRORS\n${this.state.errors["is_valid"]}\nusername: ${this.state.errors["username"]}\npass1: ${this.state.errors["pass1"]}\n`)
        if (this.state.errors["is_valid"]) {

            axios
                .post(
                    "/login",
                    {
                        username: this.state.username,
                        password: this.state.pass1
                    },
                )
                .then((res) => {
                    console.log(res, "login")
                    this.dealWithLoginResult(res);
                }).catch(error => {
                console.log(error);
                this.dealWithLoginResult(error.response);
            });
        }
    }
    dealWithLoginResult = (res) => {
        if (res) {
            if (res.status === HttpStatus.OK) {
                this.props.updateParent(res);
                this.setState({redirectAfterLoggedIn: "/"})
            } else {
                this.setState({msg: res.data["error"]})
            }
        }
    }

    convertErrorToMessage = (msg) => {
        if (msg) {
            msg = msg.split("|").join(", ")
            msg = msg.split("_").join(" ");
            return msg;
        }
    };

    onSubmit = (e) => {
        e.preventDefault();
        this.clearErrors();
        let new_errors = this.formUtils.validate_login(this.state.username, this.state.pass1);
        this.setState({
                been_submitted: true,
                errors: new_errors
            },
            this.sendIfPossible);

    }

    render() {
        if (this.state.redirectAfterLoggedIn) {
            return <Redirect to={this.state.redirectAfterLoggedIn}/>
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
                                    <p onChange={this.onChange} className="h3 text-center mb-4">Login</p>
                                    <div className="grey-text">
                                        <div className="form-group">
                                            <MDBInput onChange={this.onChange} value={this.state.username}
                                                      name="username"
                                                      label="Your username" icon="user" group type="text"
                                                      id="defaultFormRegisterNameEx"
                                                      className={this.state.been_submitted ? (this.validateUsername() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                                      required
                                                      error="wrong"
                                                      success="right"/>
                                            <div className="invalid-feedback"
                                                 style={{display: "block"}}>{this.state.errors["username"]}</div>
                                            <div className="valid-feedback"/>
                                        </div>
                                        <div className="form-group">
                                            <MDBInput onChange={this.onChange} value={this.state.pass1} name="pass1"
                                                      label="Your password" icon="lock" group type="password"
                                                      className={this.state.been_submitted ? (this.validatePassword() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                                      required
                                                      error="wrong"
                                                      success="right"
                                            />
                                            <div className="invalid-feedback"
                                                 style={{display: "block"}}>{this.state.errors["pass1"]}</div>
                                            <div className="valid-feedback"/>
                                        </div>
                                    </div>
                                    <div className="text-center">
                                        <MDBBtn type="submit"
                                                value="Submit"
                                                outline
                                                color="info">Login</MDBBtn>
                                    </div>
                                </form>
                                <p onChange={this.onChange}
                                   className="h4 text-center mb-4 text-danger">{this.state.msg}</p>
                            </MDBCol>
                        </MDBRow>
                    </MDBContainer>
                </React.Fragment>
            );
        }

    }
}

// PropTypes
LoginPage.propTypes = {
    isLoggedIn: PropTypes.func.isRequired,
    isAdmin: PropTypes.func.isRequired,
    getUserName: PropTypes.func.isRequired,
    updateParent: PropTypes.func.isRequired,
};

export default LoginPage;

