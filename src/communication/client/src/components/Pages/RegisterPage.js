import React, {Component} from "react";
import {MDBBtn, MDBCol, MDBContainer, MDBInput, MDBRow} from 'mdbreact';
import PropTypes from "prop-types";
import FormUtils from "../FormUtils";
import axios from "axios";
import * as HttpStatus from "http-status-codes"
import {Redirect} from "react-router-dom";


export class RegisterPage extends Component {
    state = {
        username: "",
        email: "",
        pass1: "",
        pass2: "",
        errors: FormUtils.defaultRegisterDictionary(),
        been_submitted: false,
        msg: "",
        redirectAfterRegistered: null
    };
    formUtils = new FormUtils();


    validateEmail = () => this.formUtils.validate_email(this.state.email, this.state.errors);
    validateUsername = () => this.formUtils.validate_username(this.state.username, this.state.errors);
    validatePassword = () => this.formUtils.validate_password(this.state.pass1, this.state.errors);
    confirmPasswords = () => this.formUtils.confirm_passwords(this.state.pass1, this.state.pass2, this.state.errors);

    onChange = (e) => {
        this.setState({[e.target.name]: e.target.value});
    }
    clearErrors = () => {
        this.setState({errors: FormUtils.defaultRegisterDictionary()})
    }
    sendIfPossible = () => {
        // console.log(`${this.state.username}\n${this.state.email}\n${this.state.pass1}\n${this.state.pass2}\n`)
        // console.log(`ERRORS\n${this.state.errors["is_valid"]}\nusername: ${this.state.errors["username"]}\nemail: ${this.state.errors["email"]}\npass1: ${this.state.errors["pass1"]}\npass2: ${this.state.errors["pass2"]}\n`)
        if (this.state.errors["is_valid"]) {
            axios.post(
                "/register",
                {
                    user_id: this.props.getUserId(),
                    username: this.state.username,
                    email: this.state.email,
                    password: this.state.pass1
                },
            )
            .then((res) => {
                console.log(res)
                this.dealWithRegisterResult(res);
            }).catch(error => {
                console.log(error)
                this.dealWithRegisterResult(error.response);
            });
        }
    }

    dealWithRegisterResult = (res) => {
        if(res){
            if (res.status === HttpStatus.CREATED || res.status === HttpStatus.OK) {
                // register successful
                      axios.get(`/is_logged`)
                        .then((res) => {
                            this.props.updateParent(res)
                            this.setState({redirectAfterRegistered: "/login_page"})
                        }).catch(error => {
                        console.log(error)
                    });
            } else {
                this.setState({msg: this.convertErrorToMessage(res.data["error"])})
            }
        }
    };

    convertErrorToMessage = (msg) => {
        if (msg) {
            msg = msg.split("|").join(", ")
            msg = msg.split("_").join(" ");
        }
        return msg;
    }

    onSubmit = (e) => {
        e.preventDefault();
        this.clearErrors();
        let new_errors = this.formUtils.validate_register(this.state.username, this.state.email, this.state.pass1, this.state.pass2);
        this.setState({
                been_submitted: true,
                errors: new_errors
            },
            this.sendIfPossible);

    }


    render() {
        if (this.state.redirectAfterRegistered) {
            return <Redirect to={this.state.redirectAfterRegistered}/>
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
                                    <p onChange={this.onChange} className="h3 text-center mb-4">Register</p>
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
                                            <MDBInput onChange={this.onChange} value={this.state.email} name="email"
                                                      label="Your email" icon="envelope" group type="email"
                                                      className={this.state.been_submitted ? (this.validateEmail() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                                      required
                                                      error="wrong"
                                                      success="right"/>
                                            <div className="invalid-feedback"
                                                 style={{display: "block"}}>{this.state.errors["email"]}</div>
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

                                        <div className="form-group">
                                            <MDBInput onChange={this.onChange} value={this.state.pass2} name="pass2"
                                                      label="Confirm your password" icon="exclamation-triangle" group
                                                      type="password"
                                                      className={this.state.been_submitted ? (this.confirmPasswords() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                                      required
                                                      error="wrong" success="right"/>
                                            <div className="invalid-feedback"
                                                 style={{display: "block"}}>{this.state.errors["pass2"]}</div>
                                            <div className="valid-feedback"/>
                                        </div>

                                    </div>
                                    <div className="text-center">
                                        <MDBBtn type="submit"
                                                value="Submit"
                                                outline
                                                color="info">Register</MDBBtn>
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
RegisterPage.propTypes = {
    isLoggedIn: PropTypes.func.isRequired,
    isAdmin: PropTypes.func.isRequired,
    updateParent: PropTypes.func.isRequired,
    getUserName: PropTypes.func.isRequired,


};

export default RegisterPage;

